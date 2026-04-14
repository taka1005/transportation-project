"""
Phase 3: Discrete-Event Simulation (SimPy)
Steps 3.2.1–3.2.5: Build and run DES with empirical and best-fit arrival distributions
"""

import simpy
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import time as timer

PROCESSED = Path("data/processed")
SEED = 42

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


def compute_intraday_interarrival(df, time_col="arrival_time", group_cols=None):
    sort_cols = (group_cols or []) + ["operating_date", time_col]
    group = (group_cols or []) + ["operating_date"]
    df = df.sort_values(sort_cols)
    df["interarrival_sec"] = df.groupby(group)[time_col].diff().dt.total_seconds()
    return df


# ===================================================================
# Arrival generators
# ===================================================================

def exponential_arrivals(rng, mean_iat):
    """Generate exponential (Poisson) inter-arrival times."""
    while True:
        yield rng.exponential(mean_iat)


def empirical_arrivals(rng, iat_data):
    """Sample inter-arrival times from empirical data (with replacement)."""
    while True:
        yield rng.choice(iat_data)


def weibull_arrivals(rng, c, scale):
    """Generate Weibull-distributed inter-arrival times."""
    while True:
        yield scale * rng.weibull(c)


def lognormal_arrivals(rng, s, scale):
    """Generate log-normal inter-arrival times."""
    # scipy lognorm: s=shape, scale=scale, loc=0
    # numpy lognormal: mean and sigma of underlying normal
    # Convert: if X ~ LogNormal(mu_n, sigma_n), then
    #   scale = exp(mu_n), s = sigma_n
    mu_n = np.log(scale)
    sigma_n = s
    while True:
        yield rng.lognormal(mu_n, sigma_n)


# ===================================================================
# SimPy simulation
# ===================================================================

def run_simulation(n_servers, mean_service_time, arrival_gen, n_arrivals,
                   warmup_arrivals=500, rng=None):
    """
    Run a single-queue multi-server simulation.

    Parameters:
        n_servers: number of servers (docks for BB, 1 for MBTA)
        mean_service_time: mean service time in seconds (exponential)
        arrival_gen: generator yielding inter-arrival times
        n_arrivals: total arrivals to simulate (including warmup)
        warmup_arrivals: discard first N arrivals for warmup
        rng: numpy random generator for service times
    """
    if rng is None:
        rng = np.random.default_rng(SEED)

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=n_servers)

    # Metrics collection
    wait_times = []
    system_times = []
    queue_lengths = []

    def customer(env, server, arrival_id):
        arrive_time = env.now
        queue_lengths.append(len(server.queue))

        with server.request() as req:
            yield req
            wait = env.now - arrive_time
            service_time = rng.exponential(mean_service_time)
            yield env.timeout(service_time)

            total = env.now - arrive_time

            if arrival_id >= warmup_arrivals:
                wait_times.append(wait)
                system_times.append(total)

    def arrival_process(env, server, arrival_gen):
        for i in range(n_arrivals):
            iat = next(arrival_gen)
            yield env.timeout(iat)
            env.process(customer(env, server, i))

    env.process(arrival_process(env, server, arrival_gen))
    env.run()

    wait_arr = np.array(wait_times)
    sys_arr = np.array(system_times)
    queue_arr = np.array(queue_lengths[warmup_arrivals:])

    return {
        "Wq": np.mean(wait_arr) if len(wait_arr) > 0 else 0,
        "W": np.mean(sys_arr) if len(sys_arr) > 0 else 0,
        "Lq": np.mean(queue_arr) if len(queue_arr) > 0 else 0,
        "n_served": len(wait_arr),
    }


def run_replications(n_servers, mean_service_time, arrival_gen_factory,
                     n_arrivals, warmup_arrivals, n_reps=10, base_seed=SEED):
    """Run multiple replications and return mean + 95% CI."""
    results = []
    for rep in range(n_reps):
        seed = base_seed + rep
        rng = np.random.default_rng(seed)
        gen = arrival_gen_factory(rng)
        r = run_simulation(n_servers, mean_service_time, gen, n_arrivals,
                           warmup_arrivals, rng)
        results.append(r)

    df = pd.DataFrame(results)
    summary = {}
    for metric in ["Wq", "W", "Lq"]:
        vals = df[metric].values
        mean = np.mean(vals)
        se = np.std(vals, ddof=1) / np.sqrt(len(vals))
        ci_lo = mean - 1.96 * se
        ci_hi = mean + 1.96 * se
        summary[metric] = {"mean": mean, "ci_lo": ci_lo, "ci_hi": ci_hi, "se": se}
    summary["n_served"] = int(df["n_served"].mean())
    return summary


def print_results(label, results, analytical=None):
    """Print simulation results with optional comparison to analytical."""
    print(f"\n  {label}:")
    print(f"    {'Metric':<8} {'Sim Mean':>12} {'95% CI':>24}", end="")
    if analytical:
        print(f"  {'Analytical':>12} {'Rel Error':>12}", end="")
    print()
    print(f"    {'-'*8} {'-'*12} {'-'*24}", end="")
    if analytical:
        print(f"  {'-'*12} {'-'*12}", end="")
    print()

    for metric in ["Wq", "W", "Lq"]:
        r = results[metric]
        unit = "sec" if metric in ["Wq", "W"] else ""
        ci_str = f"[{r['ci_lo']:.4f}, {r['ci_hi']:.4f}]"
        print(f"    {metric:<8} {r['mean']:>12.4f} {ci_str:>24}", end="")
        if analytical and metric in analytical:
            ana_val = analytical[metric]
            if ana_val > 0:
                rel_err = (r['mean'] - ana_val) / ana_val * 100
                print(f"  {ana_val:>12.4f} {rel_err:>+11.1f}%", end="")
            else:
                print(f"  {ana_val:>12.4f} {'N/A':>12}", end="")
        print()
    print(f"    Customers served: {results['n_served']:,}")


if __name__ == "__main__":
    # --- Load and prepare data ---
    print("Loading data...")
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])
    bb = assign_operating_date(bb, "arrival_time")
    bb = compute_intraday_interarrival(bb, group_cols=["end_station_id"])

    mbta = pd.read_parquet(PROCESSED / "mbta_arrivals.parquet")
    mbta["arrival_time"] = pd.to_datetime(mbta["arrival_time"])
    if "disruption" in mbta.columns:
        mbta = mbta[~mbta["disruption"]].copy()
    mbta = assign_operating_date(mbta, "arrival_time")
    mbta = compute_intraday_interarrival(mbta, group_cols=["direction"])

    # Simulation parameters
    N_ARRIVALS = 20000
    WARMUP = 2000
    N_REPS = 10

    # --- Fit distributions (need params for best-fit generators) ---
    print("Fitting distributions...")

    # ===================================================================
    # BLUEBIKES
    # ===================================================================
    for sid, info in BB_STATIONS.items():
        sname = info["name"]
        c = info["capacity"]

        print(f"\n\n{'='*70}")
        print(f"  Bluebikes — {sname} ({sid}, c={c})")
        print(f"{'='*70}")

        # Get inter-arrival data
        mask = bb["end_station_id"] == sid
        iat_data = bb.loc[mask, "interarrival_sec"].dropna()
        iat_data = iat_data[iat_data > 0].values

        mean_iat = iat_data.mean()
        lam = 1 / mean_iat

        # Service rate from Little's Law
        inv = pd.read_parquet(PROCESSED / f"bb_inventory_{sid}.parquet")
        avg_inv = inv["inventory"].mean()
        mean_service = avg_inv / lam  # avg dock occupancy time
        mu = 1 / mean_service

        print(f"  λ = {lam:.6f}/s ({lam*3600:.2f}/hr), μ = {mu:.6f}/s")
        print(f"  Mean IAT = {mean_iat:.1f}s, Mean service = {mean_service:.0f}s")
        print(f"  ρ_server = {lam/(c*mu):.4f}")

        # Fit Weibull
        wb_params = stats.weibull_min.fit(iat_data, floc=0)
        wb_c, wb_loc, wb_scale = wb_params
        print(f"  Weibull fit: c={wb_c:.4f}, scale={wb_scale:.2f}")

        # Analytical M/M/c
        from phase3_queueing import mmc_metrics
        ana_mmc = mmc_metrics(lam, mu, c)

        # --- Simulations ---
        print(f"\n  Running simulations ({N_REPS} reps × {N_ARRIVALS} arrivals)...")
        t0 = timer.time()

        # 1. Exponential (Poisson) arrivals — should match M/M/c analytical
        print("\n  [1/3] Exponential arrivals (Poisson baseline)...")
        exp_results = run_replications(
            c, mean_service,
            lambda rng: exponential_arrivals(rng, mean_iat),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Exponential (Poisson) — M/M/c validation",
                       exp_results, ana_mmc if ana_mmc["stable"] else None)

        # 2. Empirical arrivals
        print("\n  [2/3] Empirical arrivals...")
        emp_results = run_replications(
            c, mean_service,
            lambda rng: empirical_arrivals(rng, iat_data),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Empirical arrivals", emp_results)

        # 3. Weibull arrivals
        print("\n  [3/3] Weibull arrivals...")
        wb_results = run_replications(
            c, mean_service,
            lambda rng: weibull_arrivals(rng, wb_c, wb_scale),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Weibull arrivals (best-fit)", wb_results)

        elapsed = timer.time() - t0
        print(f"\n  Elapsed: {elapsed:.1f}s")

    # ===================================================================
    # MBTA
    # ===================================================================
    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")

        print(f"\n\n{'='*70}")
        print(f"  MBTA Red Line — {dir_label}")
        print(f"{'='*70}")

        mask = mbta["direction"] == direction
        iat_data = mbta.loc[mask, "interarrival_sec"].dropna()
        iat_data = iat_data[iat_data > 0].values

        mean_iat = iat_data.mean()
        lam = 1 / mean_iat

        # Dwell time as service
        if "dwell_time_seconds" in mbta.columns:
            dwell = mbta.loc[mask, "dwell_time_seconds"].dropna()
            dwell = dwell[dwell > 0]
            mean_service = dwell.mean()
        else:
            mean_service = 30.0
        mu = 1 / mean_service

        print(f"  λ = {lam:.6f}/s ({lam*3600:.2f}/hr), μ = {mu:.6f}/s")
        print(f"  Mean IAT = {mean_iat:.1f}s, Mean dwell = {mean_service:.1f}s")
        print(f"  ρ = {lam/mu:.4f}")

        # Fit log-normal
        ln_params = stats.lognorm.fit(iat_data, floc=0)
        ln_s, ln_loc, ln_scale = ln_params
        print(f"  Log-normal fit: s={ln_s:.4f}, scale={ln_scale:.2f}")

        # Analytical M/M/1
        from phase3_queueing import mm1_metrics
        ana_mm1 = mm1_metrics(lam, mu)

        # --- Simulations ---
        print(f"\n  Running simulations ({N_REPS} reps × {N_ARRIVALS} arrivals)...")
        t0 = timer.time()

        # 1. Exponential (Poisson) arrivals — validate against M/M/1
        print("\n  [1/3] Exponential arrivals (Poisson baseline)...")
        exp_results = run_replications(
            1, mean_service,
            lambda rng: exponential_arrivals(rng, mean_iat),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Exponential (Poisson) — M/M/1 validation",
                       exp_results, ana_mm1 if ana_mm1["stable"] else None)

        # 2. Empirical arrivals
        print("\n  [2/3] Empirical arrivals...")
        emp_results = run_replications(
            1, mean_service,
            lambda rng: empirical_arrivals(rng, iat_data),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Empirical arrivals", emp_results)

        # 3. Log-normal arrivals
        print("\n  [3/3] Log-normal arrivals...")
        ln_results = run_replications(
            1, mean_service,
            lambda rng: lognormal_arrivals(rng, ln_s, ln_scale),
            N_ARRIVALS, WARMUP, N_REPS
        )
        print_results("Log-normal arrivals (best-fit)", ln_results)

        elapsed = timer.time() - t0
        print(f"\n  Elapsed: {elapsed:.1f}s")

    print("\n\nAll simulations complete.")
