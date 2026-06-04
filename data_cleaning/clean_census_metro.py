#!/usr/bin/env python3
"""Build metro census tract table: Sacramento CSV + ACS API for neighbor counties."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from broadband_analysis.config import (  # noqa: E402
    CENSUS_CLEAN_FILE,
    FCC_METRO_COUNTY_PREFIXES,
    RAW_DATA_DIR,
)

SAC_RAW = RAW_DATA_DIR / "Census Data Sac.csv"
API_KEY_FILE = PROJECT_ROOT / "support_data" / "census_api_key.txt"

ACS_YEAR = "2022"
ACS_VARS = "NAME,B19013_001E,B01003_001E,B02001_002E,B02001_003E,B02001_005E"

# Neighbor counties (Sacramento 06067 comes from local CSV)
METRO_COUNTIES_API = tuple(
    (prefix[2:], name)
    for prefix, name in zip(
        FCC_METRO_COUNTY_PREFIXES,
        ["Sacramento", "Solano", "Amador", "Placer", "El Dorado"],
    )
    if prefix != "06067"
)

MISSING_CODES = {-666666666, -888888888, -999999999}


def _api_key() -> str:
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not key and API_KEY_FILE.exists():
        key = API_KEY_FILE.read_text().strip()
    if not key:
        raise RuntimeError(
            "Census API key required. Set CENSUS_API_KEY or create support_data/census_api_key.txt"
        )
    return key


def _load_sac_raw() -> pd.DataFrame:
    census = pd.read_csv(SAC_RAW, skiprows=1)
    if str(census.columns[0]).isdigit():
        census.columns = census.iloc[0].astype(str).str.lower().str.strip()
        census = census.iloc[1:].reset_index(drop=True)
    else:
        census.columns = census.columns.str.lower().str.strip()
    return census


def _fetch_county_tracts(county_fips: str, api_key: str) -> pd.DataFrame:
    params = urllib.parse.urlencode(
        {
            "get": ACS_VARS,
            "for": "tract:*",
            "in": f"state:06 county:{county_fips}",
            "key": api_key,
        }
    )
    url = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5?{params}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        rows = json.loads(resp.read().decode())
    headers = [h.lower() for h in rows[0]]
    return pd.DataFrame(rows[1:], columns=headers)


def _standardize_census(census: pd.DataFrame) -> pd.DataFrame:
    census = census.rename(
        columns={
            "name": "tract_name",
            "b19013_001e": "median_income",
            "b01003_001e": "total_population",
            "b02001_002e": "white_population",
            "b02001_003e": "black_population",
            "b02001_005e": "asian_population",
        }
    )

    numeric_cols = [
        "median_income",
        "total_population",
        "white_population",
        "black_population",
        "asian_population",
    ]
    for col in numeric_cols:
        census[col] = pd.to_numeric(census[col], errors="coerce")
        census.loc[census[col].isin(MISSING_CODES), col] = pd.NA

    census["state"] = census["state"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)
    census["county"] = census["county"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    census["tract"] = (
        census["tract"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.split(".")
        .str[0]
        .str.zfill(6)
    )
    census["tract_geoid"] = census["state"] + census["county"] + census["tract"]

    census = census.dropna(subset=["median_income", "total_population"]).copy()
    pop = census["total_population"].replace(0, pd.NA)
    census["white_pct"] = census["white_population"] / pop
    census["black_pct"] = census["black_population"] / pop
    census["asian_pct"] = census["asian_population"] / pop

    keep = [
        "tract_name",
        "median_income",
        "total_population",
        "white_population",
        "black_population",
        "asian_population",
        "state",
        "county",
        "tract",
        "tract_geoid",
        "white_pct",
        "black_pct",
        "asian_pct",
    ]
    return census[keep].copy()


def clean_census_metro(api_key: str | None = None) -> pd.DataFrame:
    """Sacramento County from CSV; neighbor counties from Census ACS API."""
    key = api_key or _api_key()
    print("Loading Sacramento County from CSV...")
    sac = _standardize_census(_load_sac_raw())
    print(f"  Sacramento (06067): {len(sac)} tracts")

    frames = [sac]
    for county_fips, name in METRO_COUNTIES_API:
        print(f"Fetching {name} (06{county_fips}) from ACS {ACS_YEAR}...")
        raw = _fetch_county_tracts(county_fips, key)
        cleaned = _standardize_census(raw)
        print(f"  {name}: {len(cleaned)} tracts")
        frames.append(cleaned)

    metro = pd.concat(frames, ignore_index=True)
    metro = metro.drop_duplicates(subset=["tract_geoid"], keep="first")
    return metro.sort_values("tract_geoid").reset_index(drop=True)


def main() -> None:
    metro = clean_census_metro()
    CENSUS_CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    metro.to_csv(CENSUS_CLEAN_FILE, index=False)
    print(f"Saved {len(metro)} tracts -> {CENSUS_CLEAN_FILE}")


if __name__ == "__main__":
    main()
