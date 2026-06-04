#!/usr/bin/env python3
"""Command-line entry point for the Sacramento broadband analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from broadband_analysis.pipeline import run_full_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Sacramento broadband inequality analysis (ZIP code level)."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for CSV outputs (default: analysis/outputs)",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=None,
        help="Directory for figure outputs (default: analysis/outputs/figures)",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Display figures interactively instead of only saving them",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip writing CSV and figure files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_full_analysis(
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        save_outputs=not args.no_save,
        show_plots=args.show_plots,
    )

    print("=== Sacramento Broadband Analysis Complete ===")
    print(f"Greater Sacramento ZIP codes: {results.findings['total_sac_zipcodes']}")
    print(f"ZIP codes with M-Lab tests: {results.findings['zipcodes_with_mlab_tests']}")
    print(f"Overall median download speed: {results.findings['overall_median_download_mbps']:.1f} Mbps")
    print(f"Mean speed gap: {results.findings['overall_mean_speed_gap_mbps']:.1f} Mbps")
    print(
        "Speed gap t-test: "
        f"t={results.speed_gap_test.t_statistic:.2f}, "
        f"p={results.speed_gap_test.p_value:.2e}"
    )
    print(f"Figures saved: {len(results.figure_paths)}")


if __name__ == "__main__":
    main()
