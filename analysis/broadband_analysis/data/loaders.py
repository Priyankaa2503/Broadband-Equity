"""Load cleaned datasets and supporting reference files."""

import pandas as pd

from broadband_analysis.config import (
    CENSUS_CLEAN_FILE,
    CENSUS_NUMERIC_COLUMNS,
    FCC_CLEAN_FILE,
    MLAB_CLEAN_FILE,
    MLAB_RAW_FILE,
    SAC_ZIPCODES,
    URBANICITY_CLEAN_FILE,
    ZIP_TRACT_CROSSWALK_FILE,
)


def _normalize_zip(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def _normalize_tract(series: pd.Series) -> pd.Series:
    return series.astype(str).str.zfill(11)


def load_sac_zipcodes() -> list[str]:
    """Return Greater Sacramento metro ZIP codes for the study area."""
    return [str(z).zfill(5) for z in SAC_ZIPCODES]


def load_crosswalk() -> pd.DataFrame:
    """Load ZIP-to-census-tract crosswalk for Greater Sacramento."""
    crosswalk = pd.read_csv(ZIP_TRACT_CROSSWALK_FILE, dtype=str)
    crosswalk["zipcode"] = _normalize_zip(crosswalk["zipcode"])
    crosswalk["tract_geoid"] = _normalize_tract(crosswalk["tract_geoid"])
    return crosswalk


def load_mlab(cleaned: bool = True) -> pd.DataFrame:
    """Load M-Lab speed test records."""
    path = MLAB_CLEAN_FILE if cleaned else MLAB_RAW_FILE
    mlab = pd.read_csv(path, dtype={"postal_code": str})
    if "postal_code" in mlab.columns:
        mlab["postal_code"] = _normalize_zip(mlab["postal_code"])
    return mlab


def load_urbanicity() -> pd.DataFrame:
    """Load cleaned urbanicity classifications by ZIP."""
    urbanicity = pd.read_csv(URBANICITY_CLEAN_FILE, dtype={"zipcode": str})
    urbanicity["zipcode"] = _normalize_zip(urbanicity["zipcode"])
    return urbanicity


def load_census() -> pd.DataFrame:
    """Load cleaned metro census demographics by tract (Sac + neighbor counties)."""
    census = pd.read_csv(CENSUS_CLEAN_FILE, dtype={"tract_geoid": str})
    census["tract_geoid"] = _normalize_tract(census["tract_geoid"])
    for column in CENSUS_NUMERIC_COLUMNS:
        census[column] = pd.to_numeric(census[column], errors="coerce")
    return census


def load_fcc() -> pd.DataFrame:
    """Load cleaned FCC broadband availability data."""
    fcc = pd.read_csv(FCC_CLEAN_FILE, dtype={"tract_geoid": str})
    fcc["tract_geoid"] = _normalize_tract(fcc["tract_geoid"])
    fcc["max_advertised_download_speed"] = pd.to_numeric(
        fcc["max_advertised_download_speed"],
        errors="coerce",
    )
    return fcc


def count_raw_mlab_records() -> int:
    """Return the number of rows in the raw M-Lab export."""
    return len(pd.read_csv(MLAB_RAW_FILE, usecols=["id"]))
