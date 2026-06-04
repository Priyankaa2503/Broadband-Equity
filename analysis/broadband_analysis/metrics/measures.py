"""Compute the four project analysis measures."""

import pandas as pd

from broadband_analysis.config import CORRELATION_COLUMNS


def get_analysis_subset(merged: pd.DataFrame) -> pd.DataFrame:
    """Return ZIPs with observed M-Lab download speeds."""
    return merged.dropna(subset=["median_download_mbps"]).copy()


def add_income_groups(
    analysis: pd.DataFrame,
    column: str = "median_income",
    labels: tuple[str, str] = ("Low income", "High income"),
) -> pd.DataFrame:
    """Split ZIPs into low/high income groups using the median income distribution."""
    result = analysis.copy()
    result["income_group"] = pd.qcut(
        result[column],
        q=2,
        labels=list(labels),
        duplicates="drop",
    )
    return result


def compute_measure1_speed_by_region(analysis: pd.DataFrame) -> pd.DataFrame:
    """Measure 1: mean and median download speed by ZIP."""
    columns = ["zipcode", "poname", "mean_download_mbps", "median_download_mbps", "test_count"]
    return analysis[columns].sort_values("median_download_mbps", ascending=False)


def summarize_speed_by_group(analysis: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compare speed metrics across urbanicity and income groups."""
    speed_columns = ["mean_download_mbps", "median_download_mbps", "mean_latency_ms"]

    grouped = {
        "urbanicity": analysis.groupby("urbanicity")[speed_columns].agg(["mean", "median", "count"]),
    }

    if "income_group" in analysis.columns:
        grouped["income_group"] = analysis.groupby("income_group", observed=True)[
            speed_columns
        ].agg(["mean", "median", "count"])

    return grouped


def compute_measure2_variability(analysis: pd.DataFrame) -> pd.DataFrame:
    """Measure 2: standard deviation of download speed by ZIP."""
    columns = ["zipcode", "urbanicity", "median_income", "speed_std_mbps", "test_count"]
    return analysis[columns].sort_values("speed_std_mbps", ascending=False)


def compute_measure3_speed_gap(analysis: pd.DataFrame) -> pd.DataFrame:
    """Measure 3: FCC reported speed minus M-Lab median speed by ZIP."""
    columns = ["zipcode", "fcc_reported_mbps", "median_download_mbps", "speed_gap_mbps"]
    return analysis[columns].sort_values("speed_gap_mbps", ascending=False)


def compute_correlation_matrix(analysis: pd.DataFrame) -> pd.DataFrame:
    """Measure 4: Pearson correlation matrix for demographics and performance."""
    return analysis[CORRELATION_COLUMNS].corr(method="pearson")
