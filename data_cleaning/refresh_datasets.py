#!/usr/bin/env python3
"""Regenerate all cleaned datasets and the ZIP–tract crosswalk for the 61-ZIP study area."""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from broadband_analysis.config import (  # noqa: E402
    MLAB_RAW_FILE,
    RAW_DATA_DIR,
    SAC_ZIPCODES,
)

DATASET_DIR = RAW_DATA_DIR
CLEANED_DIR = PROJECT_ROOT / "cleaned_dataset"
SUPPORT_DIR = PROJECT_ROOT / "support_data"


def classify_ruca(ruca_code: float) -> str | float:
    if pd.isna(ruca_code):
        return np.nan
    if ruca_code == 1:
        return "Urban"
    if ruca_code <= 3:
        return "Suburban"
    return "Rural"


def clean_mlab() -> pd.DataFrame:
    """Clean BQ M-Lab export and filter to study ZIP codes."""
    print(f"Loading M-Lab from {MLAB_RAW_FILE.name}...")
    mlab = pd.read_csv(MLAB_RAW_FILE, dtype={"postal_code": str})

    keep_cols = [
        "id", "date", "test_uuid", "test_time", "throughput_mbps", "min_rtt_ms",
        "loss_rate", "client_city", "client_state", "postal_code",
        "client_latitude", "client_longitude", "isp", "asn",
    ]
    mlab = mlab[[c for c in keep_cols if c in mlab.columns]].copy()

    mlab["date"] = pd.to_datetime(mlab["date"], errors="coerce")
    mlab["test_time"] = pd.to_datetime(mlab["test_time"], errors="coerce", utc=True)
    for col in ["throughput_mbps", "min_rtt_ms", "loss_rate", "client_latitude", "client_longitude"]:
        mlab[col] = pd.to_numeric(mlab[col], errors="coerce")
    mlab["asn"] = pd.to_numeric(mlab["asn"], errors="coerce")
    mlab["postal_code"] = mlab["postal_code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    for col in ["client_city", "client_state", "isp"]:
        mlab[col] = mlab[col].astype(str).str.strip()

    before = len(mlab)
    mlab = mlab.dropna(subset=["test_time", "throughput_mbps", "min_rtt_ms", "postal_code", "isp"])
    mlab = mlab[(mlab["throughput_mbps"] > 1) & (mlab["min_rtt_ms"].between(1, 500))].copy()
    mlab = mlab.drop_duplicates()

    sac = {str(z).zfill(5) for z in SAC_ZIPCODES}
    mlab = mlab[mlab["postal_code"].isin(sac)].copy()
    print(f"M-Lab: {before:,} raw -> {len(mlab):,} cleaned (study ZIPs)")
    return mlab


def clean_urbanicity() -> pd.DataFrame:
    """Build urbanicity table for all study ZIP codes."""
    sac = {str(z).zfill(5) for z in SAC_ZIPCODES}
    ruca = pd.read_csv(DATASET_DIR / "Urbanicity 2020 Dataset.csv")
    ruca.columns = ruca.columns.str.lower().str.strip()
    ruca["zipcode"] = ruca["zipcode"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
    ruca["primaryruca"] = pd.to_numeric(ruca["primaryruca"], errors="coerce")

    ruca = ruca[(ruca["state"] == "CA") & (ruca["zipcode"].isin(sac))].copy()
    ruca["urbanicity"] = ruca["primaryruca"].apply(classify_ruca)

    out = ruca[["zipcode", "poname", "primaryruca", "urbanicity"]].sort_values("zipcode")
    print(f"Urbanicity: {len(out)} ZIP codes")
    return out


def geocode_zip_to_tract(zipcode: str) -> str | None:
    """Map ZIP centroid to census tract via pgeocode + Census geocoder."""
    import pgeocode

    nom = pgeocode.Nominatim("us")
    loc = nom.query_postal_code(zipcode)
    if pd.isna(loc.latitude):
        return None

    url = (
        "https://geocoding.geo.census.gov/geocoder/geographies/coordinates?"
        f"x={loc.longitude}&y={loc.latitude}&benchmark=Public_AR_Current"
        "&vintage=Current_Current&format=json"
    )
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.load(resp)
    tracts = data["result"]["geographies"].get("Census Tracts", [])
    if not tracts:
        return None
    return str(tracts[0]["GEOID"]).zfill(11)


def build_crosswalk() -> pd.DataFrame:
    """Build ZIP-to-tract crosswalk for all study ZIP codes."""
    rows = []
    for z in SAC_ZIPCODES:
        z = str(z).zfill(5)
        geoid = geocode_zip_to_tract(z)
        if geoid:
            rows.append({"zipcode": z, "tract_geoid": geoid, "weight": 1.0})
            print(f"  {z} -> {geoid}")
        else:
            print(f"  {z} -> NO TRACT")
        time.sleep(0.25)
    return pd.DataFrame(rows)


def main() -> None:
    from clean_census_metro import clean_census_metro
    from clean_fcc_metro import clean_fcc_metro

    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Census (Sac CSV + metro counties via API) ===")
    census = clean_census_metro()
    census.to_csv(CLEANED_DIR / "census_sacramento_cleaned.csv", index=False)

    print("=== FCC (metro counties from raw) ===")
    fcc = clean_fcc_metro()
    fcc.to_csv(CLEANED_DIR / "fcc_sacramento_cleaned.csv", index=False)

    print("=== M-Lab (BQ export) ===")
    mlab = clean_mlab()
    mlab.to_csv(CLEANED_DIR / "mlab_sacramento_cleaned.csv", index=False)

    print("=== Urbanicity ===")
    urban = clean_urbanicity()
    urban.to_csv(CLEANED_DIR / "urbanicity_sacramento_cleaned.csv", index=False)

    print("=== ZIP–tract crosswalk (Census geocoder) ===")
    crosswalk = build_crosswalk()
    crosswalk.to_csv(SUPPORT_DIR / "zip_tract_crosswalk_sac.csv", index=False)

    tests_per_zip = mlab.groupby("postal_code").size()
    print(
        f"\nDone: {len(SAC_ZIPCODES)} study ZIPs, "
        f"{(tests_per_zip > 0).sum()} with M-Lab tests"
    )


if __name__ == "__main__":
    main()
