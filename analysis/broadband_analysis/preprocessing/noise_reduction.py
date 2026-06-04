"""Outlier filtering and noise-reduction reporting."""

import pandas as pd

from broadband_analysis.config import IQR_MULTIPLIER, SAC_ZIPCODES
from broadband_analysis.data.loaders import count_raw_mlab_records, load_mlab


def filter_to_sacramento_zips(mlab: pd.DataFrame, sac_zipcodes: list[str] | None = None) -> pd.DataFrame:
    """Keep only M-Lab records in the Greater Sacramento ZIP list."""
    zipcodes = sac_zipcodes or [str(z).zfill(5) for z in SAC_ZIPCODES]
    return mlab[mlab["postal_code"].isin(zipcodes)].copy()


def apply_iqr_filter(
    df: pd.DataFrame,
    column: str = "throughput_mbps",
    multiplier: float = IQR_MULTIPLIER,
) -> tuple[pd.DataFrame, dict]:
    """
    Remove outliers using the IQR rule.

    This project uses IQR filtering rather than 5th/95th percentile trimming.
    """
    q1, q3 = df[column].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    filtered = df[(df[column] >= lower) & (df[column] <= upper)].copy()

    metadata = {
        "method": f"IQR ({multiplier}×)",
        "q1": float(q1),
        "q3": float(q3),
        "lower_bound": float(lower),
        "upper_bound": float(upper),
        "rows_before": len(df),
        "rows_after": len(filtered),
        "rows_removed": len(df) - len(filtered),
    }
    return filtered, metadata


def _percentile_trim_count(df: pd.DataFrame, column: str = "throughput_mbps") -> int:
    """Count rows that would be removed by 5th/95th percentile trimming."""
    lower = df[column].quantile(0.05)
    upper = df[column].quantile(0.95)
    return int(((df[column] < lower) | (df[column] > upper)).sum())


def build_noise_reduction_summary() -> pd.DataFrame:
    """Summarize record counts at each cleaning and filtering stage."""
    raw_count = count_raw_mlab_records()
    mlab = load_mlab()
    clean_count = len(mlab)

    mlab_sac = filter_to_sacramento_zips(mlab)
    mlab_iqr, _ = apply_iqr_filter(mlab_sac)
    percentile_removed = _percentile_trim_count(mlab_sac)

    stages = [
        ("Raw M-Lab records (BQ export)", raw_count, 0),
        ("After cleaning (study ZIPs)", clean_count, raw_count - clean_count),
        ("IQR outlier removal (used)", len(mlab_iqr), len(mlab_sac) - len(mlab_iqr)),
        (
            "5th/95th percentile (NOT used)",
            len(mlab_sac) - percentile_removed,
            percentile_removed,
        ),
    ]

    return pd.DataFrame(
        [
            {
                "stage": stage,
                "rows": rows,
                "rows_removed": removed,
                "pct_of_raw": 0.0 if raw_count == 0 else 100 * removed / raw_count,
            }
            for stage, rows, removed in stages
        ]
    )
