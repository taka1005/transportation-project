"""
Phase 3: Queueing Analysis
Steps 3.1.1–3.1.2: M/M/1 and M/M/c analytical predictions
"""

import pandas as pd
import numpy as np
from math import factorial
from pathlib import Path

PROCESSED = Path("data/processed")

BB_STATIONS = {
    "M32004": {"name": "Kendall T", "capacity": 23},
    "M32042": {"name": "MIT Vassar St", "capacity": 53},
}


def assign_operating_date(df, time_col, start_hour=5):
    t = df[time_col]
    if hasattr(t.dt, 'tz') and t.dt.tz is not None:
        t_naive = t.dt.tz_localize(None)
    else:
        t_naive = t
    df["operating_date"] = (t_naive - pd.Timedelta(hours=start_hour)).dt.date
    return df


def mm1_metrics(lam, mu):
    """Compute M/M/1 queueing metrics."""
    rho = lam / mu  # utilization
    if rho >= 1:
        return {"rho": rho, "Wq": float('inf'), "Lq": float('inf'),
                "W": float('inf'), "L": float('inf'), "stable": False}
    Wq = rho / (mu - lam)           # avg wait in queue
    Lq = rho**2 / (1 - rho)         # avg queue length
    W = 1 / (mu - lam)              # avg time in system
    L = rho / (1 - rho)             # avg number in system
    return {"rho": rho, "Wq": Wq, "Lq": Lq, "W": W, "L": L, "stable": True}


def erlang_c(c, rho_total):
    """
    Compute Erlang C probability (probability of queueing in M/M/c).
    rho_total = lambda / mu (total offered load, NOT per-server).
    """
    a = rho_total  # total offered load = lambda / mu
    rho_server = a / c  # per-server utilization

    if rho_server >= 1:
        return float('inf')

    # Numerator: (a^c / c!) * (1 / (1 - rho_server))
    numerator = (a**c / factorial(c)) * (1 / (1 - rho_server))

    # Denominator: sum_{k=0}^{c-1} a^k/k!  +  numerator
    summation = sum(a**k / factorial(k) for k in range(c))
    denominator = summation + numerator

    return numerator / denominator


def mmc_metrics(lam, mu, c):
    """Compute M/M/c queueing metrics using Erlang C."""
    rho_total = lam / mu
    rho_server = rho_total / c  # per-server utilization

    if rho_server >= 1:
        return {"rho_server": rho_server, "rho_total": rho_total,
                "c": c, "Wq": float('inf'), "Lq": float('inf'),
                "W": float('inf'), "L": float('inf'), "stable": False}

    P_queue = erlang_c(c, rho_total)
    Wq = P_queue / (c * mu - lam)
    Lq = P_queue * rho_server / (1 - rho_server)
    W = Wq + 1 / mu
    L = Lq + rho_total

    return {"rho_server": rho_server, "rho_total": rho_total, "c": c,
            "P_queue": P_queue, "Wq": Wq, "Lq": Lq, "W": W, "L": L, "stable": True}


def estimate_bb_service_rate(arrivals, departures, station_id, capacity):
    """
    Estimate service rate (μ) for a Bluebikes station.
    Service = dock occupancy. Use Little's Law: L = λ * W_service
    Average inventory (L) from reconstructed data, λ from arrivals.
    μ = 1 / W_service = λ / L
    """
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{station_id}.parquet")

    # Average inventory (number of bikes docked)
    avg_inventory = inv["inventory"].mean()

    # Arrival rate: arrivals per second during operating hours
    arr = arrivals[arrivals["end_station_id"] == station_id].copy()
    arr["arrival_time"] = pd.to_datetime(arr["arrival_time"])
    arr = assign_operating_date(arr, "arrival_time")

    # Total operating hours
    n_op_days = arr["operating_date"].nunique()
    op_hours_per_day = 20  # 5am to 1am
    total_seconds = n_op_days * op_hours_per_day * 3600

    n_arrivals = len(arr)
    lam = n_arrivals / total_seconds  # arrivals per second

    # Average service time via Little's Law
    if avg_inventory > 0 and lam > 0:
        W_service = avg_inventory / lam  # avg dock occupancy time
        mu = 1 / W_service
    else:
        W_service = float('inf')
        mu = 0

    return lam, mu, avg_inventory, W_service


def estimate_mbta_service_rate(mbta, direction):
    """
    Estimate service rate (μ) for MBTA.
    Service = dwell time at station.
    """
    df = mbta[(mbta["direction"] == direction)].copy()
    df["arrival_time"] = pd.to_datetime(df["arrival_time"])
    df = assign_operating_date(df, "arrival_time")

    # Arrival rate
    n_op_days = df["operating_date"].nunique()
    op_hours_per_day = 20
    total_seconds = n_op_days * op_hours_per_day * 3600
    n_arrivals = len(df)
    lam = n_arrivals / total_seconds

    # Dwell time
    if "dwell_time_seconds" in df.columns:
        dwell = df["dwell_time_seconds"].dropna()
        dwell = dwell[dwell > 0]
        avg_dwell = dwell.mean()
    else:
        avg_dwell = 30.0  # fallback: assume 30 sec
        print(f"  WARNING: dwell_time_seconds not found, using default {avg_dwell}s")

    mu = 1 / avg_dwell if avg_dwell > 0 else 0

    return lam, mu, avg_dwell


if __name__ == "__main__":
    # --- Load data ---
    print("Loading data...")
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb_dep_data = []  # We need departures too
    # Reconstruct departures from arrivals data isn't ideal; use inventory events
    # Actually, we can get departure rate from inventory data

    mbta = pd.read_parquet(PROCESSED / "mbta_arrivals.parquet")
    mbta["arrival_time"] = pd.to_datetime(mbta["arrival_time"])
    if "disruption" in mbta.columns:
        mbta = mbta[~mbta["disruption"]].copy()

    # === Bluebikes ===
    print(f"\n{'='*70}")
    print("  Bluebikes: Parameter Estimation")
    print(f"{'='*70}")

    for sid, info in BB_STATIONS.items():
        sname = info["name"]
        c = info["capacity"]
        lam, mu, avg_inv, W_service = estimate_bb_service_rate(bb, None, sid, c)

        print(f"\n  {sname} ({sid}):")
        print(f"    Arrival rate (λ):         {lam:.6f} /sec  ({lam*3600:.2f} /hr)")
        print(f"    Avg inventory:            {avg_inv:.1f} bikes")
        print(f"    Avg dock occupancy:       {W_service:.0f} sec  ({W_service/60:.1f} min)")
        print(f"    Service rate (μ):         {mu:.6f} /sec  ({mu*3600:.4f} /hr)")
        print(f"    Utilization (ρ = λ/μ):    {lam/mu:.4f}")
        print(f"    Dock count (c):           {c}")

        # M/M/1
        print(f"\n    --- M/M/1 Predictions ---")
        m1 = mm1_metrics(lam, mu)
        if m1["stable"]:
            print(f"    ρ = {m1['rho']:.4f}")
            print(f"    Wq (avg wait):   {m1['Wq']:.1f} sec  ({m1['Wq']/60:.1f} min)")
            print(f"    Lq (avg queue):  {m1['Lq']:.4f}")
            print(f"    W  (avg system): {m1['W']:.1f} sec  ({m1['W']/60:.1f} min)")
            print(f"    L  (avg in sys): {m1['L']:.4f}")
        else:
            print(f"    UNSTABLE: ρ = {m1['rho']:.4f} ≥ 1")

        # M/M/c
        print(f"\n    --- M/M/c Predictions (c={c}) ---")
        mc = mmc_metrics(lam, mu, c)
        if mc["stable"]:
            print(f"    ρ_server = {mc['rho_server']:.6f}")
            print(f"    P(queue) = {mc['P_queue']:.6e}")
            print(f"    Wq (avg wait):   {mc['Wq']:.4f} sec  ({mc['Wq']*1000:.4f} ms)")
            print(f"    Lq (avg queue):  {mc['Lq']:.6e}")
            print(f"    W  (avg system): {mc['W']:.1f} sec  ({mc['W']/60:.1f} min)")
            print(f"    L  (avg in sys): {mc['L']:.4f}")
        else:
            print(f"    UNSTABLE: ρ_server = {mc['rho_server']:.4f} ≥ 1")

    # === MBTA ===
    print(f"\n\n{'='*70}")
    print("  MBTA Red Line: Parameter Estimation")
    print(f"{'='*70}")

    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")
        lam, mu, avg_dwell = estimate_mbta_service_rate(mbta, direction)

        print(f"\n  {dir_label}:")
        print(f"    Arrival rate (λ):         {lam:.6f} /sec  ({lam*3600:.2f} /hr)")
        print(f"    Avg dwell time:           {avg_dwell:.1f} sec")
        print(f"    Service rate (μ):         {mu:.6f} /sec  ({mu*3600:.4f} /hr)")
        print(f"    Utilization (ρ = λ/μ):    {lam/mu:.4f}")

        # M/M/1 (single platform track per direction)
        print(f"\n    --- M/M/1 Predictions ---")
        m1 = mm1_metrics(lam, mu)
        if m1["stable"]:
            print(f"    ρ = {m1['rho']:.4f}")
            print(f"    Wq (avg wait):   {m1['Wq']:.1f} sec  ({m1['Wq']/60:.1f} min)")
            print(f"    Lq (avg queue):  {m1['Lq']:.4f}")
            print(f"    W  (avg system): {m1['W']:.1f} sec  ({m1['W']/60:.1f} min)")
            print(f"    L  (avg in sys): {m1['L']:.4f}")
        else:
            print(f"    UNSTABLE: ρ = {m1['rho']:.4f} ≥ 1")

    print(f"\n\n{'='*70}")
    print("  Summary")
    print(f"{'='*70}")
    print("  M/M/c for MBTA is not computed (c=1, same as M/M/1 for single track per direction)")
