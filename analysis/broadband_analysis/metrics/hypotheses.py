"""Hypothesis testing and final summary statistics."""

from dataclasses import dataclass

import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class SpeedGapTestResult:
    mean_gap_mbps: float
    positive_gap_count: int
    total_zips: int
    t_statistic: float
    p_value: float


def test_speed_gap(analysis: pd.DataFrame) -> SpeedGapTestResult:
    """Test Hypothesis 2: ISP-reported speeds exceed observed M-Lab speeds."""
    gap = analysis["speed_gap_mbps"].dropna()
    t_statistic, p_value = stats.ttest_1samp(gap, 0)

    return SpeedGapTestResult(
        mean_gap_mbps=float(gap.mean()),
        positive_gap_count=int((gap > 0).sum()),
        total_zips=len(gap),
        t_statistic=float(t_statistic),
        p_value=float(p_value),
    )


def summarize_findings(merged: pd.DataFrame, analysis: pd.DataFrame) -> dict[str, float | int]:
    """Return headline results for the interpretation section."""
    return {
        "total_sac_zipcodes": len(merged),
        "zipcodes_with_mlab_tests": len(analysis),
        "overall_median_download_mbps": float(analysis["median_download_mbps"].median()),
        "overall_mean_speed_gap_mbps": float(analysis["speed_gap_mbps"].mean()),
        "income_speed_correlation": float(
            analysis["median_income"].corr(analysis["median_download_mbps"])
        ),
        "variability_speed_correlation": float(
            analysis["speed_std_mbps"].corr(analysis["median_download_mbps"])
        ),
    }
