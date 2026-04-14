"""
Phase 3.2a.3–3.2a.6: Revised queueing analysis with fullness correction.
- Re-estimate μ excluding full-capacity periods
- Compute M/M/c/c (Erlang B) blocking probability
- Re-run M/M/c with corrected parameters
- Re-run DES with finite capacity (rejection model)
"""

import sys
sys.path.insert(0, "src")

import simpy
import pandas as pd
import numpy as np
from scipy import stats
from math import factorial, exp
from pathlib import Path
import time as timer

from fullness_filter import (
    get_full_capacity_periods, get_observed_fullness_rate, filter_inventory_for_service_rate
)
from phase3_queueing import mm1_metrics, mmc_metrics
from phase3_simulation import (
    exponential_arrivals, empirical_arrivals, weibull_arrivals,
    lognormal_arrivals, run_replications, print_results, SEED
)
from phase2_rerun import get_clean_iat, assign_operating_date, compute_intraday_interarrival

PROCESSED = Path("data/processed")

BB_STATIONS = {
    "M32004": {"name": "Kendall T", "capacity": 23},
    "M32042": {"name": "MIT Vassar St", "capacity": 53},
}


def erlang_b(c, a):
    """
    Compute Erlang B blocking probability for M/M/c/c (loss system).
    a = offered load = λ/μ (total, not per server)
    c = number of servers
    """
    # Use recursive formula to avoid overflow:
    # B(c, a) = (a * B(c-1, a)) / (c + a * B(c-1, a))
    b = 1.0  # B(0, a) = 1
    for i in range(1, c + 1):
        b = (a * b) / (i + a * b)
    return b


def run_finite_simulation(n_servers, mean_service_time, arrival_gen, n_arrivals,
                          warmup_arrivals=500, rng=None):
    """
    Run M/M/c/c simulation: finite capacity, no queue, arrivals rejected when full.
    """
    if rng is None:
        rng = np.random.default_rng(SEED)

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=n_servers)

    served_times = []
    n_rejected = [0]
    n_served_post_warmup = [0]
    n_rejected_post_warmup = [0]
    n_total = [0]

    def customer(env, server, arrival_id):
        if server.count < server.capacity:
            # Server available, serve immediately
            req = server.request()
            yield req
            service_time = rng.exponential(mean_service_time)
            yield env.timeout(service_time)
            server.release(req)
            if arrival_id >= warmup_arrivals:
                served_times.append(service_time)
                n_served_post_warmup[0] += 1
        else:
            # All servers busy, reject (no waiting)
            if arrival_id >= warmup_arrivals:
                n_rejected_post_warmup[0] += 1

    def arrival_process(env, server, arrival_gen):
        for i in range(n_arrivals):
            iat = next(arrival_gen)
            yield env.timeout(iat)
            n_total[0] = i + 1
            env.process(customer(env, server, i))

    env.process(arrival_process(env, server, arrival_gen))
    env.run()

    total_post = n_served_post_warmup[0] + n_rejected_post_warmup[0]
    blocking_prob = n_rejected_post_warmup[0] / total_post if total_post > 0 else 0

    return {
        "blocking_prob": blocking_prob,
        "n_served": n_served_post_warmup[0],
        "n_rejected": n_rejected_post_warmup[0],
        "avg_service_time": np.mean(served_times) if served_times else 0,
    }


def run_finite_replications(n_servers, mean_service_time, arrival_gen_factory,
                            n_arrivals, warmup_arrivals, n_reps=10, base_seed=SEED):
    results = []
    for rep in range(n_reps):
        seed = base_seed + rep
        rng = np.random.default_rng(seed)
        gen = arrival_gen_factory(rng)
        r = run_finite_simulation(n_servers, mean_service_time, gen, n_arrivals,
                                  warmup_arrivals, rng)
        results.append(r)

    df = pd.DataFrame(results)
    bp = df["blocking_prob"].values
    mean_bp = np.mean(bp)
    se_bp = np.std(bp, ddof=1) / np.sqrt(len(bp))

    return {
        "blocking_prob": {"mean": mean_bp, "ci_lo": mean_bp - 1.96*se_bp, "ci_hi": mean_bp + 1.96*se_bp},
        "n_served": int(df["n_served"].mean()),
        "n_rejected": int(df["n_rejected"].mean()),
    }


if __name__ == "__main__":
    print("Loading data...")
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])

    N_ARRIVALS = 20000
    WARMUP = 2000
    N_REPS = 10

    for sid, info in BB_STATIONS.items():
        sname = info["name"]
        c = info["capacity"]

        print(f"\n\n{'='*70}")
        print(f"  {sname} ({sid}, c={c})")
        print(f"{'='*70}")

        # --- 3.2a.1: Get clean IAT data ---
        iat_before, iat_after, _ = get_clean_iat(bb, sid)
        print(f"\n  IAT data: {len(iat_before)} before → {len(iat_after)} after fullness exclusion")

        mean_iat_clean = np.mean(iat_after)
        lam_clean = 1 / mean_iat_clean

        # --- 3.2a.3: Re-estimate μ excluding full-capacity ---
        inv_clean = filter_inventory_for_service_rate(sid)
        avg_inv_clean = inv_clean["inventory"].mean()
        W_service_clean = avg_inv_clean / lam_clean
        mu_clean = 1 / W_service_clean

        # Also compute original (uncorrected) for comparison
        inv_all = pd.read_parquet(PROCESSED / f"bb_inventory_{sid}.parquet")
        avg_inv_all = inv_all["inventory"].mean()
        lam_old = 1 / np.mean(iat_before)
        W_service_old = avg_inv_all / lam_old
        mu_old = 1 / W_service_old

        print(f"\n  Parameter Comparison:")
        print(f"  {'Param':<25} {'Before':>14} {'After':>14} {'Change':>10}")
        print(f"  {'-'*25} {'-'*14} {'-'*14} {'-'*10}")
        print(f"  {'λ (/hr)':<25} {lam_old*3600:>14.3f} {lam_clean*3600:>14.3f} {(lam_clean-lam_old)/lam_old*100:>+9.1f}%")
        print(f"  {'Avg inventory':<25} {avg_inv_all:>14.1f} {avg_inv_clean:>14.1f} {(avg_inv_clean-avg_inv_all)/avg_inv_all*100:>+9.1f}%")
        print(f"  {'Mean service (sec)':<25} {W_service_old:>14.0f} {W_service_clean:>14.0f} {(W_service_clean-W_service_old)/W_service_old*100:>+9.1f}%")
        print(f"  {'μ (/hr)':<25} {mu_old*3600:>14.4f} {mu_clean*3600:>14.4f} {(mu_clean-mu_old)/mu_old*100:>+9.1f}%")
        print(f"  {'ρ_server':<25} {lam_old/(c*mu_old):>14.4f} {lam_clean/(c*mu_clean):>14.4f}")

        # --- 3.2a.4: Erlang B ---
        offered_load = lam_clean / mu_clean
        pb_erlang = erlang_b(c, offered_load)
        obs_fullness = get_observed_fullness_rate(sid)

        print(f"\n  --- M/M/c/c (Erlang B) ---")
        print(f"  Offered load (a = λ/μ): {offered_load:.4f}")
        print(f"  Predicted blocking prob: {pb_erlang*100:.4f}%")
        print(f"  Observed fullness rate:  {obs_fullness*100:.4f}%")
        print(f"  Ratio (predicted/observed): {pb_erlang/obs_fullness:.3f}" if obs_fullness > 0 else "")

        # --- 3.2a.5: M/M/c with corrected params ---
        print(f"\n  --- M/M/c (corrected) ---")
        mc = mmc_metrics(lam_clean, mu_clean, c)
        if mc["stable"]:
            print(f"  ρ_server = {mc['rho_server']:.6f}")
            print(f"  Wq = {mc['Wq']:.4f} sec")
            print(f"  W  = {mc['W']:.1f} sec ({mc['W']/60:.1f} min)")

        # --- 3.2a.6: DES with finite capacity ---
        print(f"\n  --- DES Simulations (corrected, {N_REPS} reps × {N_ARRIVALS}) ---")
        t0 = timer.time()

        # Fit Weibull to clean data
        wb_params = stats.weibull_min.fit(iat_after, floc=0)
        wb_c_param, _, wb_scale = wb_params
        print(f"  Weibull fit (clean): c={wb_c_param:.4f}, scale={wb_scale:.2f}")

        # A. Infinite queue (M/M/c style) — for comparison
        print(f"\n  [A] M/M/c DES (infinite queue):")
        for arr_label, gen_factory in [
            ("Exponential", lambda rng: exponential_arrivals(rng, mean_iat_clean)),
            ("Empirical", lambda rng: empirical_arrivals(rng, iat_after)),
            ("Weibull", lambda rng: weibull_arrivals(rng, wb_c_param, wb_scale)),
        ]:
            results = run_replications(c, W_service_clean, gen_factory,
                                       N_ARRIVALS, WARMUP, N_REPS)
            wq = results["Wq"]
            w = results["W"]
            print(f"    {arr_label:<14} Wq={wq['mean']:.2f}s [{wq['ci_lo']:.2f},{wq['ci_hi']:.2f}]  "
                  f"W={w['mean']:.0f}s ({w['mean']/60:.1f}min)")

        # B. Finite capacity (M/M/c/c style) — blocking probability
        print(f"\n  [B] M/M/c/c DES (finite capacity, rejection):")
        for arr_label, gen_factory in [
            ("Exponential", lambda rng: exponential_arrivals(rng, mean_iat_clean)),
            ("Empirical", lambda rng: empirical_arrivals(rng, iat_after)),
            ("Weibull", lambda rng: weibull_arrivals(rng, wb_c_param, wb_scale)),
        ]:
            results = run_finite_replications(c, W_service_clean, gen_factory,
                                              N_ARRIVALS, WARMUP, N_REPS)
            bp = results["blocking_prob"]
            print(f"    {arr_label:<14} Block={bp['mean']*100:.4f}% [{bp['ci_lo']*100:.4f},{bp['ci_hi']*100:.4f}]  "
                  f"served={results['n_served']:,}  rejected={results['n_rejected']:,}")

        print(f"\n  Erlang B analytical: {pb_erlang*100:.4f}%")
        print(f"  Observed fullness:   {obs_fullness*100:.4f}%")

        elapsed = timer.time() - t0
        print(f"  Elapsed: {elapsed:.1f}s")

    print("\n\nRevised analysis complete.")
