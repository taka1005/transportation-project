"""
Fullness filter: Identify full-capacity periods for Bluebikes stations
and provide functions to exclude affected inter-arrival times.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED = Path("data/processed")

BB_STATIONS = {
    "M32004": {"name": "Kendall T", "capacity": 23},
    "M32042": {"name": "MIT Vassar St", "capacity": 53},
}


def get_full_capacity_periods(station_id):
    """
    Build merged full-capacity time windows from inventory data.
    Returns list of (start, end) tuples representing continuous full periods.
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    inv["time"] = pd.to_datetime(inv["time"])

    # Each at_capacity=True arrival marks the start of a full period.
    # The period ends at the next departure event.
    full_events = inv[inv["at_capacity"]].copy()

    periods = []
    for _, row in full_events.iterrows():
        start = row["time"]
        next_dep = inv[(inv["time"] > start) & (inv["event"] == "departure")]
        if len(next_dep) > 0:
            end = next_dep.iloc[0]["time"]
            periods.append((start, end))

    if not periods:
        return []

    # Merge overlapping periods
    periods.sort(key=lambda x: x[0])
    merged = [periods[0]]
    for start, end in periods[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    return merged


def is_during_full_period(timestamp, full_periods):
    """Check if a timestamp falls within any full-capacity period."""
    for start, end in full_periods:
        if start <= timestamp <= end:
            return True
        if timestamp < start:
            break  # periods are sorted
    return False


def filter_bb_arrivals(bb, station_id, full_periods):
    """
    Filter Bluebikes arrivals for a station, excluding inter-arrival times
    affected by full-capacity periods.

    An inter-arrival time is affected if EITHER:
    - The previous arrival occurred during a full-capacity period, OR
    - Any full-capacity period falls between the previous and current arrival
      (meaning some arrivals were censored/rejected in between)

    Returns filtered dataframe with clean inter-arrival times.
    """
    mask = bb["end_station_id"] == station_id
    df = bb[mask].copy().sort_values("arrival_time").reset_index(drop=True)

    if not full_periods:
        return df

    # Convert full periods to arrays for vectorized operations
    fp_starts = np.array([s.timestamp() for s, _ in full_periods])
    fp_ends = np.array([e.timestamp() for _, e in full_periods])

    arr_times = df["arrival_time"].values.astype("datetime64[ns]").astype(np.int64) / 1e9

    # For each arrival, check if any full period overlaps with
    # the interval (previous_arrival, current_arrival)
    exclude = np.zeros(len(df), dtype=bool)
    exclude[0] = True  # first arrival has no inter-arrival time

    for i in range(1, len(df)):
        prev_t = arr_times[i - 1]
        curr_t = arr_times[i]

        # Check if any full period overlaps with (prev_t, curr_t)
        # Overlap exists if: period_start < curr_t AND period_end > prev_t
        overlaps = (fp_starts < curr_t) & (fp_ends > prev_t)
        if overlaps.any():
            exclude[i] = True

    df["exclude_fullness"] = exclude
    return df


def get_observed_fullness_rate(station_id):
    """
    Compute observed fullness rate from inventory data.
    Returns fraction of time at capacity (for Erlang B validation).
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    return inv["at_capacity"].mean()


def filter_inventory_for_service_rate(station_id):
    """
    Return inventory data excluding full-capacity periods,
    for unbiased service rate estimation.
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    return inv[~inv["at_capacity"]].copy()


if __name__ == "__main__":
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])

    for sid, info in BB_STATIONS.items():
        sname = info["name"]
        print(f"\n{'='*60}")
        print(f"  {sname} ({sid})")
        print(f"{'='*60}")

        full_periods = get_full_capacity_periods(sid)
        print(f"  Full-capacity periods (merged): {len(full_periods)}")
        if full_periods:
            durations = [(e - s).total_seconds() for s, e in full_periods]
            total_full_sec = sum(durations)
            print(f"  Avg period duration: {np.mean(durations):.0f} sec ({np.mean(durations)/60:.1f} min)")
            print(f"  Total full time: {total_full_sec:.0f} sec ({total_full_sec/3600:.1f} hr)")

        # Filter arrivals
        df = filter_bb_arrivals(bb, sid, full_periods)
        n_total = len(df)
        n_excluded = df["exclude_fullness"].sum()
        n_clean = n_total - n_excluded
        print(f"\n  Total arrivals: {n_total}")
        print(f"  Excluded (fullness-affected): {n_excluded} ({n_excluded/n_total*100:.1f}%)")
        print(f"  Clean arrivals: {n_clean}")

        # Compare stats before/after
        iat_all = df["interarrival_sec"].dropna()
        iat_all = iat_all[iat_all > 0]
        iat_clean = df.loc[~df["exclude_fullness"], "interarrival_sec"].dropna()
        iat_clean = iat_clean[iat_clean > 0]

        if len(iat_all) > 0 and len(iat_clean) > 0:
            print(f"\n  {'Metric':<20} {'Before':>12} {'After':>12} {'Change':>12}")
            print(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*12}")
            for name, fn in [("Mean (sec)", np.mean), ("Std (sec)", np.std),
                             ("CV", lambda x: np.std(x)/np.mean(x))]:
                before = fn(iat_all)
                after = fn(iat_clean)
                pct = (after - before) / before * 100
                print(f"  {name:<20} {before:>12.1f} {after:>12.1f} {pct:>+11.1f}%")

        # Observed fullness rate
        obs_full = get_observed_fullness_rate(sid)
        print(f"\n  Observed fullness rate: {obs_full*100:.2f}%")
