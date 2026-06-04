# Greater Sacramento Broadband Inequality Project

Analysis of M-Lab speeds, FCC reported speeds, Census demographics, and urbanicity for **61 ZIP codes** in the Greater Sacramento metro area.

## Setup

```bash
pip install -r requirements.txt
```

Place raw data under `dataset/` (gitignored):

| File | Purpose |
|------|---------|
| `BQ Results Jun 4 2026.csv` | M-Lab speed tests |
| `FCC Dataset.csv` | FCC broadband availability |
| `Census Data Sac.csv` | Sacramento County ACS tracts |
| `Urbanicity 2020 Dataset.csv` | RUCA urban/rural by ZIP |

Census API key for neighbor counties: `support_data/census_api_key.txt` or `CENSUS_API_KEY` env var.

## 1. Refresh cleaned data

```bash
python data_cleaning/refresh_datasets.py
```

Produces `cleaned_dataset/*.csv` and `support_data/zip_tract_crosswalk_sac.csv`.

Individual steps (optional):

```bash
python data_cleaning/clean_fcc_metro.py
python data_cleaning/clean_census_metro.py
```

## 2. Run analysis

```bash
cd analysis && python run_analysis.py
```

Outputs: `analysis/outputs/` (CSVs + `figures/`).

Or open `analysis/sacramento_broadband_analysis.ipynb` from the `analysis/` folder.

## Project layout

```
data_cleaning/          # refresh + FCC/census metro cleaners
analysis/
  broadband_analysis/   # load, merge, IQR, metrics, plots, pipeline
  run_analysis.py
cleaned_dataset/        # cleaned inputs for analysis
support_data/           # crosswalk, census API key (local only)
```
