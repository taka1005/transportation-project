"""
Data pipeline for extracting arrival timestamps and inter-arrival times
from Bluebikes and MBTA LAMP datasets.
"""

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from pathlib import Path
import glob

# Paths
RAW_BB = Path("data/raw/bluebikes")
RAW_MBTA = Path("data/raw/mbta")
PROCESSED = Path("data/processed")

# Station IDs
BB_STATIONS = {
    "M32004": {"name": "Kendall T", "capacity": 23},
    "M32042": {"name": "MIT Vassar St", "capacity": 53},
}
MBTA_STATION = "place-knncl"


def load_bluebikes_arrivals():
    """Extract arrival timestamps for selected Bluebikes stations."""
    files = sorted(RAW_BB.glob("*.csv"))
    dfs = []
    for f in files:
        df = pd.read_csv(
            f,
            usecols=["ride_id", "ended_at", "end_station_id", "end_station_name",
                      "started_at", "start_station_id", "start_station_name"],
            parse_dates=["ended_at", "started_at"],
        )
        dfs.append(df)
    all_trips = pd.concat(dfs, ignore_index=True)

    # Filter to selected stations (arrivals = trip ends at station)
    arrivals = all_trips[all_trips["end_station_id"].isin(BB_STATIONS.keys())].copy()
    arrivals = arrivals.rename(columns={"ended_at": "arrival_time"})
    arrivals = arrivals[["ride_id", "started_at", "arrival_time",
                         "start_station_id", "start_station_name",
                         "end_station_id", "end_station_name",
                         "interarrival_sec"]].copy() if "interarrival_sec" in arrivals.columns else \
               arrivals[["ride_id", "started_at", "arrival_time",
                         "start_station_id", "start_station_name",
                         "end_station_id", "end_station_name"]].copy()
    arrivals = arrivals.sort_values("arrival_time").reset_index(drop=True)

    # Also extract departures (trip starts) for inventory reconstruction
    departures = all_trips[all_trips["start_station_id"].isin(BB_STATIONS.keys())].copy()
    departures = departures.rename(columns={"started_at": "departure_time"})
    departures["station_id"] = departures["start_station_id"]
    departures = departures.sort_values("departure_time").reset_index(drop=True)

    return arrivals, departures


def load_mbta_arrivals():
    """Extract train arrival timestamps at Kendall/MIT for Red Line."""
    files = sorted(RAW_MBTA.glob("*.parquet"))
    dfs = []
    for f in files:
        t = pq.read_table(f)
        df = t.to_pandas()
        # Filter: Red Line, Kendall/MIT station, valid stop_timestamp
        mask = (
            (df["route_id"] == "Red")
            & (df["parent_station"] == MBTA_STATION)
            & (df["stop_timestamp"].notna())
        )
        dfs.append(df[mask])
    all_arrivals = pd.concat(dfs, ignore_index=True)

    # Convert Unix timestamp to datetime
    all_arrivals["arrival_time"] = pd.to_datetime(
        all_arrivals["stop_timestamp"], unit="s", utc=True
    ).dt.tz_convert("America/New_York")
    all_arrivals = all_arrivals.sort_values("arrival_time").reset_index(drop=True)

    return all_arrivals


def compute_interarrival_times(df, time_col="arrival_time", group_col=None):
    """Compute inter-arrival times in seconds."""
    if group_col:
        df = df.sort_values([group_col, time_col])
        df["interarrival_sec"] = df.groupby(group_col)[time_col].diff().dt.total_seconds()
    else:
        df = df.sort_values(time_col)
        df["interarrival_sec"] = df[time_col].diff().dt.total_seconds()
    return df


def filter_operating_hours(df, time_col="arrival_time", start_hour=5, end_hour=25):
    """Keep only records during operating hours (default 5am-1am)."""
    hour = df[time_col].dt.hour
    if end_hour > 24:
        mask = (hour >= start_hour) | (hour < end_hour - 24)
    else:
        mask = (hour >= start_hour) & (hour < end_hour)
    return df[mask].copy()


def reconstruct_inventory(arrivals, departures, station_id, capacity):
    """
    Reconstruct dock inventory by forward event-stream replay with
    bookkeeping clamps for unlogged operator rebalancing, and flag
    full/empty as *state transitions* (not per-clamp).

    Inventory step:
    1. Build event stream of arrivals (+1) and departures (-1), sorted by time.
    2. Start from capacity // 2 (no GBFS ground truth available).
    3. Apply deltas in order; if the running count would exceed [0, capacity],
       clamp to the boundary. The clamp is a bookkeeping correction for
       unlogged truck pickups/drop-offs and is *not* evidence of a full/empty
       state on its own.

    State flags (used downstream for full-capacity exclusion):
    - `at_capacity[i] = True` only when this event is a *trip-end* (arrival)
      that raises inventory from capacity-1 to capacity via natural
      increment (no clamp). A clamp event is not flagged, because the
      successful trip-end is physical evidence that a slot was available
      at that instant — flagging it as "full" would be self-contradictory.
    - `at_empty[i] = True` symmetrically: only a trip-start (departure)
      that lowers inventory from 1 to 0 via natural decrement.
    """
    arr = arrivals[arrivals["end_station_id"] == station_id][["arrival_time"]].copy()
    arr["event"] = "arrival"
    arr = arr.rename(columns={"arrival_time": "time"})
    arr["delta"] = 1  # bike docked

    dep = departures[departures["station_id"] == station_id][["departure_time"]].copy()
    dep["event"] = "departure"
    dep = dep.rename(columns={"departure_time": "time"})
    dep["delta"] = -1  # bike undocked

    events = pd.concat([arr, dep]).sort_values("time").reset_index(drop=True)

    n = len(events)
    inventory = np.zeros(n, dtype=int)
    at_full = np.zeros(n, dtype=bool)
    at_empty = np.zeros(n, dtype=bool)

    current = capacity // 2

    for i in range(n):
        delta = events.loc[i, "delta"]
        event = events.loc[i, "event"]

        proposed = current + delta
        clamped = False

        if proposed < 0:
            proposed = 0
            clamped = True  # bookkeeping correction for an unlogged pickup

        if proposed > capacity:
            proposed = capacity
            clamped = True  # bookkeeping correction for an unlogged drop-off

        # Natural-transition flags: set only when the physical state actually
        # reaches the boundary via a non-clamped delta.
        if not clamped:
            if event == "arrival" and current == capacity - 1 and proposed == capacity:
                at_full[i] = True
            if event == "departure" and current == 1 and proposed == 0:
                at_empty[i] = True

        current = proposed
        inventory[i] = current

    events["inventory"] = inventory
    # `at_capacity` is now strictly the natural-transition flag. The previous
    # union with `inventory >= capacity` has been dropped because a persistent
    # at-capacity stretch is represented by the entry transition plus the
    # absence of an exit transition, not by every event that happens to be
    # at the boundary.
    events["at_capacity"] = at_full
    events["at_empty"] = at_empty
    events.attrs["capacity"] = capacity

    return events


def flag_mbta_disruptions(df, headway_ratio_threshold=2.0):
    """
    Flag MBTA records where actual headway exceeds scheduled headway
    by more than the given ratio (indicating service disruption).
    """
    df = df.copy()
    df["disruption"] = False
    mask = (
        df["headway_trunk_seconds"].notna()
        & df["scheduled_headway_trunk"].notna()
        & (df["scheduled_headway_trunk"] > 0)
    )
    ratio = df.loc[mask, "headway_trunk_seconds"] / df.loc[mask, "scheduled_headway_trunk"]
    df.loc[mask, "headway_ratio"] = ratio
    df.loc[mask, "disruption"] = ratio > headway_ratio_threshold
    return df


if __name__ == "__main__":
    PROCESSED.mkdir(parents=True, exist_ok=True)

    print("Loading Bluebikes data...")
    bb_arrivals, bb_departures = load_bluebikes_arrivals()
    print(f"  Arrivals: {len(bb_arrivals)} trips at selected stations")
    print(f"  Departures: {len(bb_departures)} trips from selected stations")

    print("Filtering to operating hours (5am-1am)...")
    bb_arrivals = filter_operating_hours(bb_arrivals)
    bb_departures = filter_operating_hours(bb_departures, time_col="departure_time")
    print(f"  Arrivals after filter: {len(bb_arrivals)}")

    print("Computing Bluebikes inter-arrival times...")
    bb_arrivals = compute_interarrival_times(bb_arrivals, group_col="end_station_id")

    print("Reconstructing inventory (forward event replay with bookkeeping clamps, state-transition flags)...")
    for sid, info in BB_STATIONS.items():
        inv = reconstruct_inventory(bb_arrivals, bb_departures, sid, capacity=info["capacity"])
        n_full_entries = int(inv["at_capacity"].sum())
        n_empty_entries = int(inv["at_empty"].sum())
        print(f"  {info['name']} ({sid}): capacity={info['capacity']}, "
              f"full-entry events {n_full_entries}, empty-entry events {n_empty_entries}")
        inv.to_parquet(PROCESSED / f"bb_inventory_{sid}.parquet", index=False)

    bb_arrivals.to_parquet(PROCESSED / "bb_arrivals.parquet", index=False)
    print(f"  Saved to {PROCESSED / 'bb_arrivals.parquet'}")

    print("\nLoading MBTA data...")
    mbta = load_mbta_arrivals()
    print(f"  Red Line arrivals at Kendall/MIT: {len(mbta)}")

    print("Filtering to operating hours...")
    mbta = filter_operating_hours(mbta)
    print(f"  After filter: {len(mbta)}")

    print("Flagging disruptions...")
    mbta = flag_mbta_disruptions(mbta)
    n_disruptions = mbta["disruption"].sum()
    print(f"  Disrupted records: {n_disruptions} ({n_disruptions/len(mbta)*100:.1f}%)")

    print("Computing MBTA inter-arrival times (by direction)...")
    mbta = compute_interarrival_times(mbta, group_col="direction")

    mbta.to_parquet(PROCESSED / "mbta_arrivals.parquet", index=False)
    print(f"  Saved to {PROCESSED / 'mbta_arrivals.parquet'}")

    print("\nPipeline complete.")
