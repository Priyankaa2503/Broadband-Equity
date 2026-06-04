"""Project paths and analysis constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEANED_DATA_DIR = PROJECT_ROOT / "cleaned_dataset"
RAW_DATA_DIR = PROJECT_ROOT / "dataset"
SUPPORT_DATA_DIR = PROJECT_ROOT / "support_data"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Greater Sacramento metro ZIP codes (study area)
SAC_ZIPCODES = [
    "94571",
    "95608", "95610", "95615", "95621", "95624", "95626", "95628",
    "95630", "95632", "95638", "95639", "95640", "95641",
    "95652", "95655", "95660", "95661", "95662", "95670",
    "95671", "95673", "95678", "95680", "95683", "95690", "95693",
    "95742", "95757", "95758", "95762",
    "95811", "95814", "95815", "95816", "95817", "95818", "95819", "95820",
    "95821", "95822", "95823", "95824", "95825", "95826", "95827", "95828",
    "95829", "95830", "95831", "95832", "95833", "95834", "95835", "95836",
    "95837", "95838", "95841", "95842", "95843", "95864",
]

MLAB_RAW_FILE = RAW_DATA_DIR / "BQ Results Jun 4 2026.csv"
MLAB_CLEAN_FILE = CLEANED_DATA_DIR / "mlab_sacramento_cleaned.csv"
FCC_RAW_FILE = RAW_DATA_DIR / "FCC Dataset.csv"
FCC_CLEAN_FILE = CLEANED_DATA_DIR / "fcc_sacramento_cleaned.csv"
CENSUS_CLEAN_FILE = CLEANED_DATA_DIR / "census_sacramento_cleaned.csv"
URBANICITY_CLEAN_FILE = CLEANED_DATA_DIR / "urbanicity_sacramento_cleaned.csv"
ZIP_TRACT_CROSSWALK_FILE = SUPPORT_DATA_DIR / "zip_tract_crosswalk_sac.csv"

OUTPUT_MERGED_CSV = OUTPUT_DIR / "sacramento_zip_analysis.csv"
OUTPUT_NOISE_CSV = OUTPUT_DIR / "noise_reduction_summary.csv"
OUTPUT_CORRELATION_CSV = OUTPUT_DIR / "correlation_matrix.csv"

CENSUS_NUMERIC_COLUMNS = [
    "median_income",
    "total_population",
    "white_pct",
    "black_pct",
    "asian_pct",
]

CORRELATION_COLUMNS = [
    "median_income",
    "total_population",
    "mean_download_mbps",
    "median_download_mbps",
    "speed_std_mbps",
    "speed_gap_mbps",
    "mean_latency_ms",
]

CORRELATION_LABELS = [
    "Median income",
    "Population",
    "Mean speed",
    "Median speed",
    "Speed std",
    "Speed gap",
    "Latency",
]

IQR_MULTIPLIER = 1.5
FCC_RESIDENTIAL_CODES = ("R", "X")

# Metro county FIPS (state 06 + county); Sac census from local CSV, others from API
CENSUS_METRO_COUNTY_PREFIXES = FCC_METRO_COUNTY_PREFIXES = (
    "06067",  # Sacramento County
    "06095",  # Solano County
    "06005",  # Amador County
    "06061",  # Placer County
    "06017",  # El Dorado County
)
