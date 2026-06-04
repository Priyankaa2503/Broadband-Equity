"""End-to-end analysis pipeline."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from broadband_analysis.config import (
    FIGURES_DIR,
    OUTPUT_CORRELATION_CSV,
    OUTPUT_DIR,
    OUTPUT_MERGED_CSV,
    OUTPUT_NOISE_CSV,
)
from broadband_analysis.data.merge import build_zip_analysis_table
from broadband_analysis.metrics.hypotheses import SpeedGapTestResult, summarize_findings, test_speed_gap
from broadband_analysis.metrics.measures import (
    add_income_groups,
    compute_correlation_matrix,
    compute_measure1_speed_by_region,
    compute_measure2_variability,
    compute_measure3_speed_gap,
    get_analysis_subset,
    summarize_speed_by_group,
)
from broadband_analysis.preprocessing.noise_reduction import build_noise_reduction_summary
from broadband_analysis.visualization.plots import plot_all


@dataclass
class AnalysisResults:
    """Container for all analysis outputs."""

    noise_summary: pd.DataFrame
    merged: pd.DataFrame
    analysis: pd.DataFrame
    measure1: pd.DataFrame
    measure2: pd.DataFrame
    measure3: pd.DataFrame
    correlation_matrix: pd.DataFrame
    group_summaries: dict[str, pd.DataFrame]
    speed_gap_test: SpeedGapTestResult
    findings: dict[str, float | int]
    figure_paths: list[Path]


def _save_tables(
    noise_summary: pd.DataFrame,
    merged: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    noise_summary.to_csv(output_dir / OUTPUT_NOISE_CSV.name, index=False)
    merged.to_csv(output_dir / OUTPUT_MERGED_CSV.name, index=False)
    correlation_matrix.to_csv(output_dir / OUTPUT_CORRELATION_CSV.name, index=False)


def run_full_analysis(
    output_dir: Path | None = None,
    figures_dir: Path | None = None,
    save_outputs: bool = True,
    show_plots: bool = False,
) -> AnalysisResults:
    """
    Run the complete Sacramento broadband analysis pipeline.

    Steps:
    1. Quantify noise reduction
    2. Merge datasets at the ZIP level
    3. Compute Measures 1–4
    4. Test Hypothesis 2
    5. Save CSV outputs and figures
    """
    output_dir = output_dir or OUTPUT_DIR
    figures_dir = figures_dir or FIGURES_DIR

    noise_summary = build_noise_reduction_summary()
    merged = build_zip_analysis_table()
    analysis = add_income_groups(get_analysis_subset(merged))

    measure1 = compute_measure1_speed_by_region(analysis)
    measure2 = compute_measure2_variability(analysis)
    measure3 = compute_measure3_speed_gap(analysis)
    correlation_matrix = compute_correlation_matrix(analysis)
    group_summaries = summarize_speed_by_group(analysis)
    speed_gap_test = test_speed_gap(analysis)
    findings = summarize_findings(merged, analysis)

    if save_outputs:
        _save_tables(noise_summary, merged, correlation_matrix, output_dir)

    figure_paths = plot_all(
        noise_summary=noise_summary,
        analysis=analysis,
        measure2=measure2,
        measure3=measure3,
        correlation_matrix=correlation_matrix,
        output_dir=figures_dir,
        show=show_plots,
    )

    return AnalysisResults(
        noise_summary=noise_summary,
        merged=merged,
        analysis=analysis,
        measure1=measure1,
        measure2=measure2,
        measure3=measure3,
        correlation_matrix=correlation_matrix,
        group_summaries=group_summaries,
        speed_gap_test=speed_gap_test,
        findings=findings,
        figure_paths=figure_paths,
    )
