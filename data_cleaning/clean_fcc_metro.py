#!/usr/bin/env python3
"""Clean FCC broadband data for Greater Sacramento metro counties."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "analysis"))

from broadband_analysis.config import FCC_CLEAN_FILE, FCC_METRO_COUNTY_PREFIXES, FCC_RAW_FILE  # noqa: E402

KEEP_COLS = [
    "frn",
    "provider_id",
    "brand_name",
    "technology",
    "max_advertised_download_speed",
    "max_advertised_upload_speed",
    "low_latency",
    "business_residential_code",
    "state_usps",
    "block_geoid",
]

COUNTY_NAMES = ["Sacramento", "Solano", "Amador", "Placer", "El Dorado"]


def clean_fcc_metro() -> pd.DataFrame:
    """Load raw FCC data and filter to CA metro counties used in the study."""
    print(f"Loading {FCC_RAW_FILE.name}...")
    fcc = pd.read_csv(FCC_RAW_FILE, dtype={"block_geoid": str})

    fcc = fcc[[c for c in KEEP_COLS if c in fcc.columns]].copy()
    fcc["block_geoid"] = fcc["block_geoid"].astype(str).str.strip().str.zfill(15)
    fcc["tract_geoid"] = fcc["block_geoid"].str[:11]

    fcc = fcc[fcc["state_usps"] == "CA"].copy()
    pattern = "^(" + "|".join(FCC_METRO_COUNTY_PREFIXES) + ")"
    fcc = fcc[fcc["block_geoid"].str.match(pattern)].copy()

    fcc["max_advertised_download_speed"] = pd.to_numeric(
        fcc["max_advertised_download_speed"], errors="coerce"
    )
    fcc["max_advertised_upload_speed"] = pd.to_numeric(
        fcc["max_advertised_upload_speed"], errors="coerce"
    )
    fcc["low_latency"] = pd.to_numeric(fcc["low_latency"], errors="coerce")

    before = len(fcc)
    fcc = fcc.dropna(
        subset=[
            "max_advertised_download_speed",
            "max_advertised_upload_speed",
            "block_geoid",
            "brand_name",
        ]
    ).copy()
    print(f"FCC metro counties: {len(fcc):,} rows ({before - len(fcc):,} dropped for missing values)")

    for prefix, name in zip(FCC_METRO_COUNTY_PREFIXES, COUNTY_NAMES):
        n = fcc["block_geoid"].str.startswith(prefix).sum()
        print(f"  {name} ({prefix}): {n:,}")

    return fcc


def main() -> None:
    fcc = clean_fcc_metro()
    FCC_CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    fcc.to_csv(FCC_CLEAN_FILE, index=False)
    print(f"Saved {FCC_CLEAN_FILE}")


if __name__ == "__main__":
    main()
