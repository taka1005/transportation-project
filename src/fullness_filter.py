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
    Build committed full-capacity time windows from inventory data.

    An entry event (at_capacity=True: a natural C-1 → C trip-end transition,
    per the revised data_pipeline semantics) starts a candidate window. The
    candidate is committed ONLY if the next station event is a trip-start
    (departure), which confirms the station remained full long enough for a
    bike to be withdrawn. If the next event is another trip-end — which
    implies a rebalancing pickup between the two arrivals and therefore a
    moment of non-fullness — the candidate interval is retracted entirely
    (no partial span retained), because we lack evidence that the station
    was continuously at capacity across the interval.

    Committed windows do not overlap by construction: a committed window
    ends at a trip-start that lowers I_s to C-1, and the next natural entry
    (C-1 → C) requires a subsequent trip-end whose time is strictly later.

    Returns list of (start, end) tuples.
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    inv["time"] = pd.to_datetime(inv["time"])
    inv = inv.sort_values("time").reset_index(drop=True)

    entry_rows = inv.index[inv["at_capacity"]].tolist()

    periods = []
    for idx in entry_rows:
        if idx + 1 >= len(inv):
            continue  # no subsequent event — cannot confirm the window
        next_event = inv.iloc[idx + 1]
        if next_event["event"] == "departure":
            periods.append((inv.loc[idx, "time"], next_event["time"]))
        # else: next event is another trip-end → retract candidate

    return periods


def mark_in_full_periods(inv, full_periods):
    """
    Boolean mask over an inventory DataFrame marking events whose timestamp
    falls within any committed full-capacity period (inclusive of endpoints).
    """
    if not full_periods:
        return np.zeros(len(inv), dtype=bool)
    times = inv["time"].values.astype("datetime64[ns]")
    in_full = np.zeros(len(inv), dtype=bool)
    for start, end in full_periods:
        start_ns = np.datetime64(pd.Timestamp(start))
        end_ns = np.datetime64(pd.Timestamp(end))
        in_full |= (times >= start_ns) & (times <= end_ns)
    return in_full


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
    Observed fullness rate: fraction of total observation time the station
    spent inside a committed full-capacity period. This is the quantity to
    compare against the Erlang B blocking prediction.
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    inv["time"] = pd.to_datetime(inv["time"])
    periods = get_full_capacity_periods(station_id)
    if not periods:
        return 0.0
    total_full = sum((e - s).total_seconds() for s, e in periods)
    obs_span = (inv["time"].iloc[-1] - inv["time"].iloc[0]).total_seconds()
    if obs_span <= 0:
        return 0.0
    return total_full / obs_span


def filter_inventory_for_service_rate(station_id):
    """
    Inventory data excluding events inside any committed full-capacity
    period, for unbiased service-rate (mu) estimation via Little's Law.
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")
    inv["time"] = pd.to_datetime(inv["time"])
    periods = get_full_capacity_periods(station_id)
    in_full = mark_in_full_periods(inv, periods)
    return inv[~in_full].copy()


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
