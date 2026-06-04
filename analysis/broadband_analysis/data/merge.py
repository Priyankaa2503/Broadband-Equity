"""Integrate datasets at the ZIP code level."""

import pandas as pd

from broadband_analysis.config import FCC_RESIDENTIAL_CODES
from broadband_analysis.data.loaders import (
    load_census,
    load_crosswalk,
    load_fcc,
    load_mlab,
    load_sac_zipcodes,
    load_urbanicity,
)
from broadband_analysis.preprocessing.noise_reduction import (
    apply_iqr_filter,
    filter_to_sacramento_zips,
)


def _aggregate_mlab_by_zip(mlab: pd.DataFrame) -> pd.DataFrame:
    """Compute ZIP-level speed metrics from individual M-Lab tests."""
    return (
        mlab.groupby("postal_code")
        .agg(
            mean_download_mbps=("throughput_mbps", "mean"),
            median_download_mbps=("throughput_mbps", "median"),
            speed_std_mbps=("throughput_mbps", "std"),
            mean_latency_ms=("min_rtt_ms", "mean"),
            test_count=("throughput_mbps", "size"),
        )
        .reset_index()
        .rename(columns={"postal_code": "zipcode"})
    )


def _aggregate_fcc_by_tract(fcc: pd.DataFrame) -> pd.DataFrame:
    """Compute tract-level maximum advertised residential download speed."""
    residential = fcc[fcc["business_residential_code"].isin(FCC_RESIDENTIAL_CODES)]
    return (
        residential.groupby("tract_geoid")["max_advertised_download_speed"]
        .max()
        .reset_index(name="fcc_reported_mbps")
    )


def build_zip_analysis_table() -> pd.DataFrame:
    """
    Merge M-Lab, FCC, Census, and Urbanicity data at the ZIP code level.

    Returns one row per Greater Sacramento ZIP with speed metrics,
    demographic variables, urbanicity, and the FCC vs M-Lab speed gap.
    """
    sac_zipcodes = load_sac_zipcodes()
    crosswalk = load_crosswalk()

    mlab_sac = filter_to_sacramento_zips(load_mlab(), sac_zipcodes)
    mlab_filtered, _ = apply_iqr_filter(mlab_sac)
    zip_speed = _aggregate_mlab_by_zip(mlab_filtered)

    zip_demo = crosswalk.merge(load_census(), on="tract_geoid", how="left")
    zip_fcc = crosswalk.merge(_aggregate_fcc_by_tract(load_fcc()), on="tract_geoid", how="left")

    merged = (
        pd.DataFrame({"zipcode": sac_zipcodes})
        .merge(load_urbanicity(), on="zipcode", how="left")
        .merge(zip_demo, on="zipcode", how="left")
        .merge(zip_speed, on="zipcode", how="left")
        .merge(zip_fcc[["zipcode", "fcc_reported_mbps"]], on="zipcode", how="left")
    )
    merged["speed_gap_mbps"] = merged["fcc_reported_mbps"] - merged["median_download_mbps"]
    return merged
