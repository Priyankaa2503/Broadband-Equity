"""Generate project figures and save them to the outputs directory."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from broadband_analysis.config import CORRELATION_LABELS, FIGURES_DIR


def _ensure_figures_dir(output_dir: Path | None = None) -> Path:
    figures_dir = output_dir or FIGURES_DIR
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def configure_plot_style() -> None:
    """Apply a consistent visual style across all figures."""
    sns.set_theme(style="whitegrid", palette="colorblind")


def plot_noise_reduction_pipeline(
    noise_summary: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> Path:
    """Plot the M-Lab record counts retained at each cleaning stage."""
    figures_dir = _ensure_figures_dir(output_dir)
    used_stages = noise_summary[~noise_summary["stage"].str.contains("NOT used", case=False)]
    stages = used_stages.iloc[:3]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(stages["stage"], stages["rows"], color=["#4C72B0", "#55A868", "#C44E52"][: len(stages)])
    ax.set_xlabel("M-Lab test records")
    ax.set_title("Noise Reduction Pipeline (61 ZIP Study Area)")
    fig.tight_layout()

    output_path = figures_dir / "01_noise_reduction_pipeline.png"
    fig.savefig(output_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_average_speed_by_zip(
    analysis: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> Path:
    """Plot Measure 1: mean and median download speed by ZIP."""
    figures_dir = _ensure_figures_dir(output_dir)
    plot_df = analysis.sort_values("median_download_mbps")
    y = range(len(plot_df))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([i - 0.2 for i in y], plot_df["mean_download_mbps"], height=0.4, label="Mean")
    ax.barh([i + 0.2 for i in y], plot_df["median_download_mbps"], height=0.4, label="Median")
    ax.set_yticks(list(y))
    ax.set_yticklabels(plot_df["zipcode"])
    ax.set_xlabel("Download speed (Mbps)")
    ax.set_title("Measure 1: Average Internet Speed by ZIP Code")
    ax.legend()
    fig.tight_layout()

    output_path = figures_dir / "02_avg_speed_by_zip.png"
    fig.savefig(output_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_speed_variability(
    measure2: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> Path:
    """Plot Measure 2: download speed standard deviation by ZIP."""
    figures_dir = _ensure_figures_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=measure2, y="zipcode", x="speed_std_mbps", ax=ax, color="#C44E52")
    ax.set_xlabel("Standard deviation of download speed (Mbps)")
    ax.set_title("Measure 2: Speed Variability by ZIP Code")
    fig.tight_layout()

    output_path = figures_dir / "03_speed_variability_by_zip.png"
    fig.savefig(output_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_speed_gap(
    measure3: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> Path:
    """Plot Measure 3: FCC reported minus M-Lab median speed by ZIP."""
    figures_dir = _ensure_figures_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(measure3["zipcode"], measure3["speed_gap_mbps"], color="#DD8452")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Speed gap = FCC reported − M-Lab median (Mbps)")
    ax.set_title("Measure 3: ISP Reported vs Actual Speed Gap by ZIP")
    fig.tight_layout()

    output_path = figures_dir / "04_speed_gap_by_zip.png"
    fig.savefig(output_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_reported_vs_actual(
    analysis: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> Path:
    """Scatter plot comparing FCC reported and M-Lab median speeds."""
    figures_dir = _ensure_figures_dir(output_dir)
    fig, ax = plt.subplots(figsize=(8, 6))
    max_speed = max(analysis["fcc_reported_mbps"].max(), analysis["median_download_mbps"].max()) * 1.05
    limits = [0, max_speed]

    ax.scatter(analysis["median_download_mbps"], analysis["fcc_reported_mbps"], s=100)
    ax.plot(limits, limits, "k--", alpha=0.5, label="Perfect match")
    for _, row in analysis.iterrows():
        ax.annotate(
            row["zipcode"],
            (row["median_download_mbps"], row["fcc_reported_mbps"]),
            fontsize=8,
            alpha=0.7,
        )
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.set_xlabel("M-Lab median download (Mbps)")
    ax.set_ylabel("FCC max advertised download (Mbps)")
    ax.set_title("Reported vs Actual Speed by ZIP")
    ax.legend()
    fig.tight_layout()

    output_path = figures_dir / "07_reported_vs_actual_scatter.png"
    fig.savefig(output_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def plot_correlation_analysis(
    analysis: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> tuple[Path, Path]:
    """Plot Measure 4: correlation heatmap and income vs speed scatter."""
    figures_dir = _ensure_figures_dir(output_dir)

    heatmap_fig, heatmap_ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        ax=heatmap_ax,
        xticklabels=CORRELATION_LABELS,
        yticklabels=CORRELATION_LABELS,
    )
    heatmap_ax.set_title("Measure 4: Correlation Matrix (ZIP-level)")
    heatmap_fig.tight_layout()
    heatmap_path = figures_dir / "05_correlation_heatmap.png"
    heatmap_fig.savefig(heatmap_path, dpi=150)

    scatter_fig, scatter_ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=analysis,
        x="median_income",
        y="median_download_mbps",
        ax=scatter_ax,
        scatter_kws={"s": 80},
    )
    for _, row in analysis.iterrows():
        scatter_ax.annotate(
            row["zipcode"],
            (row["median_income"], row["median_download_mbps"]),
            fontsize=8,
            alpha=0.7,
        )
    scatter_ax.set_xlabel("Median household income ($)")
    scatter_ax.set_ylabel("Median download speed (Mbps)")
    scatter_ax.set_title("Demographics vs Broadband Performance")
    scatter_fig.tight_layout()
    scatter_path = figures_dir / "06_income_vs_speed.png"
    scatter_fig.savefig(scatter_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(heatmap_fig)
        plt.close(scatter_fig)
    return heatmap_path, scatter_path


def plot_all(
    noise_summary: pd.DataFrame,
    analysis: pd.DataFrame,
    measure2: pd.DataFrame,
    measure3: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    output_dir: Path | None = None,
    show: bool = False,
) -> list[Path]:
    """Generate and save all project figures."""
    configure_plot_style()
    return [
        plot_noise_reduction_pipeline(noise_summary, output_dir, show),
        plot_average_speed_by_zip(analysis, output_dir, show),
        plot_speed_variability(measure2, output_dir, show),
        plot_speed_gap(measure3, output_dir, show),
        *plot_correlation_analysis(analysis, correlation_matrix, output_dir, show),
        plot_reported_vs_actual(analysis, output_dir, show),
    ]
