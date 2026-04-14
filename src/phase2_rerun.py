"""
Phase 3.2a.2: Re-run Phase 2 Bluebikes analysis with fullness exclusion.
Reports before/after comparison to show censoring impact.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROCESSED = Path("data/processed")

BB_STATIONS = {
    "M32004": {"name": "Kendall T", "capacity": 23},
    "M32042": {"name": "MIT Vassar St", "capacity": 53},
}


def assign_operating_date(df, time_col="arrival_time", start_hour=5):
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


def get_clean_iat(bb, station_id):
    """Get inter-arrival times with both overnight and fullness exclusion."""
    from fullness_filter import get_full_capacity_periods, filter_bb_arrivals

    # First: assign operating dates and compute intraday IAT
    mask = bb["end_station_id"] == station_id
    df = bb[mask].copy()
    df = assign_operating_date(df)
    df = compute_intraday_interarrival(df, group_cols=["operating_date"])

    # Second: apply fullness filter
    full_periods = get_full_capacity_periods(station_id)
    fp_starts = np.array([s.timestamp() for s, _ in full_periods])
    fp_ends = np.array([e.timestamp() for _, e in full_periods])
    arr_times = df["arrival_time"].values.astype("datetime64[ns]").astype(np.int64) / 1e9

    exclude = np.zeros(len(df), dtype=bool)
    for i in range(1, len(df)):
        prev_t = arr_times[i - 1]
        curr_t = arr_times[i]
        overlaps = (fp_starts < curr_t) & (fp_ends > prev_t)
        if overlaps.any():
            exclude[i] = True
    df["exclude_fullness"] = exclude

    # Before: only overnight exclusion (NaN from intraday computation)
    iat_before = df["interarrival_sec"].dropna()
    iat_before = iat_before[iat_before > 0]

    # After: overnight + fullness exclusion
    iat_after = df.loc[~df["exclude_fullness"], "interarrival_sec"].dropna()
    iat_after = iat_after[iat_after > 0]

    return iat_before.values, iat_after.values, df


def summary_stats(iat, label):
    n = len(iat)
    mean = np.mean(iat)
    std = np.std(iat, ddof=1)
    cv = std / mean
    skew = float(pd.Series(iat).skew())
    return {"label": label, "n": n, "mean": mean, "std": std, "cv": cv, "skewness": skew}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")

    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])

    for sid, info in BB_STATIONS.items():
        sname = info["name"]
        print(f"\n{'='*70}")
        print(f"  {sname} ({sid})")
        print(f"{'='*70}")

        iat_before, iat_after, df_full = get_clean_iat(bb, sid)

        # --- 2.1: Summary statistics comparison ---
        s_before = summary_stats(iat_before, "Before (overnight excluded)")
        s_after = summary_stats(iat_after, "After (overnight + fullness excluded)")

        print(f"\n  Step 2.1: Summary Statistics")
        print(f"  {'Metric':<12} {'Before':>12} {'After':>12} {'Change':>12}")
        print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
        for key in ["n", "mean", "std", "cv", "skewness"]:
            b = s_before[key]
            a = s_after[key]
            if key == "n":
                print(f"  {'N':<12} {b:>12,} {a:>12,} {a-b:>+12,}")
            else:
                pct = (a - b) / b * 100 if b != 0 else 0
                label = {"mean": "Mean (sec)", "std": "Std (sec)", "cv": "CV", "skewness": "Skewness"}[key]
                print(f"  {label:<12} {b:>12.2f} {a:>12.2f} {pct:>+11.1f}%")

        # --- 2.2: Distribution fitting comparison ---
        print(f"\n  Step 2.2: Distribution Fitting (AIC)")
        print(f"  {'Distribution':<16} {'Before AIC':>14} {'After AIC':>14}")
        print(f"  {'-'*16} {'-'*14} {'-'*14}")

        dist_names = {
            "Exponential": stats.expon,
            "Log-normal": stats.lognorm,
            "Weibull": stats.weibull_min,
            "Gamma": stats.gamma,
        }

        for dname, dist in dist_names.items():
            # Before
            params_b = dist.fit(iat_before, floc=0)
            ll_b = np.sum(dist.logpdf(iat_before, *params_b))
            k = len(params_b) - 1
            aic_b = 2 * k - 2 * ll_b

            # After
            params_a = dist.fit(iat_after, floc=0)
            ll_a = np.sum(dist.logpdf(iat_after, *params_a))
            aic_a = 2 * k - 2 * ll_a

            best_b = " ◄" if dname == "Weibull" else ""
            print(f"  {dname:<16} {aic_b:>14.1f} {aic_a:>14.1f}{best_b}")

        # Show Weibull params before/after
        wb_b = stats.weibull_min.fit(iat_before, floc=0)
        wb_a = stats.weibull_min.fit(iat_after, floc=0)
        print(f"\n  Weibull params: c={wb_b[0]:.4f}→{wb_a[0]:.4f}, scale={wb_b[2]:.1f}→{wb_a[2]:.1f}")

        # --- 2.3: Arrival count IoD comparison (60-min window) ---
        print(f"\n  Step 2.3: Index of Dispersion (60-min window)")
        df_before = df_full.copy()
        df_after = df_full[~df_full["exclude_fullness"]].copy()

        for label, subdf in [("Before", df_before), ("After", df_after)]:
            t = subdf["arrival_time"]
            if hasattr(t.dt, 'tz') and t.dt.tz is not None:
                subdf = subdf.copy()
                subdf["_tn"] = t.dt.tz_localize(None)
            else:
                subdf = subdf.copy()
                subdf["_tn"] = t
            subdf["time_bin"] = subdf["_tn"].dt.floor("60min")
            counts = subdf.groupby("time_bin").size()
            mean_c = counts.mean()
            var_c = counts.var()
            iod = var_c / mean_c if mean_c > 0 else float('nan')
            print(f"  {label:>8}: mean={mean_c:.2f}, var={var_c:.2f}, IoD={iod:.3f}")

    print("\n\nRe-run complete.")
