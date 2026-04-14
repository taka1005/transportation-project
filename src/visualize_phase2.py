"""
Phase 2 Visualizations: Distribution fitting and comparison
Step 2.2.1: Empirical inter-arrival time distributions (histograms, CDFs)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

PROCESSED = Path("data/processed")
FIGURES = Path("outputs/figures")
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (12, 6),
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

BB_STATIONS = {
    "M32004": "Kendall T",
    "M32042": "MIT Vassar St",
}


def assign_operating_date(df, time_col="arrival_time", start_hour=5):
    t = df[time_col]
    df["operating_date"] = (t - pd.Timedelta(hours=start_hour)).dt.date
    return df


def compute_intraday_interarrival(df, time_col="arrival_time", group_cols=None):
    sort_cols = (group_cols or []) + ["operating_date", time_col]
    group = (group_cols or []) + ["operating_date"]
    df = df.sort_values(sort_cols)
    df["interarrival_sec"] = df.groupby(group)[time_col].diff().dt.total_seconds()
    return df


def load_data(exclude_fullness=False):
    # Bluebikes
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])
    bb = assign_operating_date(bb)
    bb = compute_intraday_interarrival(bb, group_cols=["end_station_id"])

    if exclude_fullness:
        import sys
        sys.path.insert(0, "src")
        from fullness_filter import get_full_capacity_periods
        import numpy as np_ff

        for sid in BB_STATIONS.keys():
            full_periods = get_full_capacity_periods(sid)
            if not full_periods:
                continue
            fp_starts = np_ff.array([s.timestamp() for s, _ in full_periods])
            fp_ends = np_ff.array([e.timestamp() for _, e in full_periods])

            mask = bb["end_station_id"] == sid
            idx = bb[mask].index
            arr_times = bb.loc[idx, "arrival_time"].values.astype("datetime64[ns]").astype(np_ff.int64) / 1e9

            exclude = np_ff.zeros(len(idx), dtype=bool)
            for i in range(1, len(idx)):
                prev_t = arr_times[i - 1]
                curr_t = arr_times[i]
                overlaps = (fp_starts < curr_t) & (fp_ends > prev_t)
                if overlaps.any():
                    exclude[i] = True

            # Set excluded inter-arrival times to NaN
            exclude_idx = idx[exclude]
            bb.loc[exclude_idx, "interarrival_sec"] = np_ff.nan

    # MBTA
    mbta = pd.read_parquet(PROCESSED / "mbta_arrivals.parquet")
    mbta["arrival_time"] = pd.to_datetime(mbta["arrival_time"])
    if "disruption" in mbta.columns:
        mbta = mbta[~mbta["disruption"]].copy()
    mbta = assign_operating_date(mbta)
    mbta = compute_intraday_interarrival(mbta, group_cols=["direction"])

    return bb, mbta


def plot_histograms_and_cdfs(bb, mbta):
    """Plot histograms and CDFs for all four systems in a single figure."""

    datasets = []
    for sid, sname in BB_STATIONS.items():
        iat = bb.loc[bb["end_station_id"] == sid, "interarrival_sec"].dropna()
        iat = iat[iat > 0]
        datasets.append((f"Bluebikes — {sname}", iat, "tab:blue" if sid == "M32004" else "tab:cyan"))

    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")
        iat = mbta.loc[mbta["direction"] == direction, "interarrival_sec"].dropna()
        iat = iat[iat > 0]
        datasets.append((f"MBTA Red Line — {dir_label}", iat, "tab:red" if direction == 1 else "tab:orange"))

    # --- Figure 1: Histograms ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, (label, iat, color) in zip(axes, datasets):
        # Convert to minutes for readability
        iat_min = iat / 60
        mean_min = iat_min.mean()
        median_min = iat_min.median()

        # Cap at 99th percentile for cleaner histogram
        cap = iat_min.quantile(0.99)
        iat_capped = iat_min[iat_min <= cap]

        ax.hist(iat_capped, bins=60, density=True, alpha=0.7, color=color, edgecolor="white", linewidth=0.5)

        # Overlay exponential PDF with same mean (Poisson reference)
        x = np.linspace(0, cap, 200)
        exp_pdf = stats.expon.pdf(x, scale=mean_min)
        ax.plot(x, exp_pdf, 'k--', linewidth=1.5, label=f"Exponential (λ⁻¹={mean_min:.1f} min)")

        ax.axvline(mean_min, color="red", linestyle=":", alpha=0.7, label=f"Mean={mean_min:.1f} min")
        ax.axvline(median_min, color="green", linestyle=":", alpha=0.7, label=f"Median={median_min:.1f} min")

        ax.set_title(label)
        ax.set_xlabel("Inter-arrival time (minutes)")
        ax.set_ylabel("Density")
        ax.legend(fontsize=9)

    fig.suptitle("Empirical Inter-Arrival Time Distributions (Histograms)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURES / "phase2_histograms.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase2_histograms.png'}")
    plt.close()

    # --- Figure 2: Empirical CDFs ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, (label, iat, color) in zip(axes, datasets):
        iat_min = iat / 60
        mean_min = iat_min.mean()

        # Cap at 99th percentile
        cap = iat_min.quantile(0.99)
        iat_capped = iat_min[iat_min <= cap].sort_values()
        ecdf_y = np.arange(1, len(iat_capped) + 1) / len(iat_capped)

        ax.step(iat_capped, ecdf_y, color=color, linewidth=1.5, label="Empirical CDF")

        # Overlay exponential CDF
        x = np.linspace(0, cap, 200)
        exp_cdf = stats.expon.cdf(x, scale=mean_min)
        ax.plot(x, exp_cdf, 'k--', linewidth=1.5, label=f"Exponential CDF (λ⁻¹={mean_min:.1f} min)")

        ax.set_title(label)
        ax.set_xlabel("Inter-arrival time (minutes)")
        ax.set_ylabel("Cumulative probability")
        ax.legend(fontsize=9, loc="lower right")
        ax.grid(True, alpha=0.3)

    fig.suptitle("Empirical vs Exponential CDFs of Inter-Arrival Times", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURES / "phase2_cdfs.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase2_cdfs.png'}")
    plt.close()

    # --- Figure 3: Log-scale histograms (to see tail behavior) ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, (label, iat, color) in zip(axes, datasets):
        iat_min = iat / 60
        mean_min = iat_min.mean()

        cap = iat_min.quantile(0.995)
        iat_capped = iat_min[iat_min <= cap]

        ax.hist(iat_capped, bins=80, density=True, alpha=0.7, color=color, edgecolor="white", linewidth=0.5)

        x = np.linspace(0.01, cap, 200)
        exp_pdf = stats.expon.pdf(x, scale=mean_min)
        ax.plot(x, exp_pdf, 'k--', linewidth=1.5, label=f"Exponential")

        ax.set_yscale("log")
        ax.set_title(label)
        ax.set_xlabel("Inter-arrival time (minutes)")
        ax.set_ylabel("Density (log scale)")
        ax.legend(fontsize=9)

    fig.suptitle("Inter-Arrival Time Distributions (Log-Scale Density)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURES / "phase2_histograms_log.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase2_histograms_log.png'}")
    plt.close()


def fit_distributions(bb, mbta):
    """
    Step 2.2.2: Fit exponential distribution
    Step 2.2.3: Fit candidate non-Poisson distributions (log-normal, Weibull, gamma)
    """
    datasets = []
    for sid, sname in BB_STATIONS.items():
        iat = bb.loc[bb["end_station_id"] == sid, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"Bluebikes — {sname}", iat))

    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")
        iat = mbta.loc[mbta["direction"] == direction, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"MBTA Red Line — {dir_label}", iat))

    dist_names = {
        "Exponential": stats.expon,
        "Log-normal": stats.lognorm,
        "Weibull": stats.weibull_min,
        "Gamma": stats.gamma,
    }

    all_results = []

    for label, iat in datasets:
        print(f"\n{'='*60}")
        print(f"  {label}  (N={len(iat):,})")
        print(f"{'='*60}")
        print(f"  {'Distribution':<16} {'Params':>40}  {'Log-Lik':>12}  {'AIC':>12}  {'BIC':>12}")
        print(f"  {'-'*16} {'-'*40}  {'-'*12}  {'-'*12}  {'-'*12}")

        results = []
        for dname, dist in dist_names.items():
            params = dist.fit(iat, floc=0)  # fix location to 0 (inter-arrival times >= 0)
            ll = np.sum(dist.logpdf(iat, *params))
            k = len(params) - 1  # subtract 1 for fixed loc
            n = len(iat)
            aic = 2 * k - 2 * ll
            bic = k * np.log(n) - 2 * ll

            # Format params nicely
            if dname == "Exponential":
                param_str = f"scale={params[1]:.2f}"
            elif dname == "Log-normal":
                param_str = f"s={params[0]:.4f}, scale={params[2]:.2f}"
            elif dname == "Weibull":
                param_str = f"c={params[0]:.4f}, scale={params[2]:.2f}"
            elif dname == "Gamma":
                param_str = f"a={params[0]:.4f}, scale={params[2]:.2f}"

            print(f"  {dname:<16} {param_str:>40}  {ll:>12.1f}  {aic:>12.1f}  {bic:>12.1f}")
            results.append({
                "system": label, "distribution": dname,
                "params": params, "loglik": ll, "aic": aic, "bic": bic,
            })

        best = min(results, key=lambda x: x["aic"])
        print(f"\n  >>> Best fit (AIC): {best['distribution']}")
        all_results.extend(results)

    # --- Summary table ---
    print(f"\n\n{'='*60}")
    print("  Best-Fit Distribution Summary (by AIC)")
    print(f"{'='*60}")
    print(f"  {'System':<35} {'Best Fit':<16} {'AIC':>12}  {'vs Exponential':>16}")
    print(f"  {'-'*35} {'-'*16} {'-'*12}  {'-'*16}")

    df_results = pd.DataFrame(all_results)
    for label, _ in datasets:
        sdf = df_results[df_results["system"] == label]
        best = sdf.loc[sdf["aic"].idxmin()]
        exp_aic = sdf.loc[sdf["distribution"] == "Exponential", "aic"].values[0]
        delta = best["aic"] - exp_aic
        print(f"  {label:<35} {best['distribution']:<16} {best['aic']:>12.1f}  {delta:>+16.1f}")

    return df_results


def plot_fitted_distributions(bb, mbta, fit_results):
    """Plot empirical vs all fitted distributions."""
    datasets = []
    for sid, sname in BB_STATIONS.items():
        iat = bb.loc[bb["end_station_id"] == sid, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"Bluebikes — {sname}", iat))

    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")
        iat = mbta.loc[mbta["direction"] == direction, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"MBTA Red Line — {dir_label}", iat))

    dist_objs = {
        "Exponential": stats.expon,
        "Log-normal": stats.lognorm,
        "Weibull": stats.weibull_min,
        "Gamma": stats.gamma,
    }
    colors = {
        "Exponential": "black",
        "Log-normal": "red",
        "Weibull": "green",
        "Gamma": "purple",
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, (label, iat) in zip(axes, datasets):
        iat_min = iat / 60
        cap = np.percentile(iat_min, 99)
        iat_capped = iat_min[iat_min <= cap]

        ax.hist(iat_capped, bins=60, density=True, alpha=0.5, color="gray",
                edgecolor="white", linewidth=0.5, label="Empirical")

        x = np.linspace(0.01, cap, 300)
        sdf = fit_results[fit_results["system"] == label]

        for _, row in sdf.iterrows():
            dname = row["distribution"]
            dist = dist_objs[dname]
            # Convert params from seconds to minutes
            params = list(row["params"])
            # Scale parameter is the last one; loc is second-to-last
            params[-1] = params[-1] / 60  # scale
            params[-2] = params[-2] / 60  # loc (fixed to 0, stays 0)

            pdf = dist.pdf(x, *params)
            style = "--" if dname == "Exponential" else "-"
            ax.plot(x, pdf, style, color=colors[dname], linewidth=1.5, label=dname)

        ax.set_title(label)
        ax.set_xlabel("Inter-arrival time (minutes)")
        ax.set_ylabel("Density")
        ax.legend(fontsize=8)

    fig.suptitle("Empirical vs Fitted Distributions", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIGURES / "phase2_fitted_distributions.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase2_fitted_distributions.png'}")
    plt.close()


def goodness_of_fit_tests(bb, mbta, fit_results):
    """
    Step 2.2.4: Formal goodness-of-fit tests
    - Kolmogorov-Smirnov (KS)
    - Anderson-Darling (AD) — for exponential only (scipy limitation)
    - Chi-squared
    """
    datasets = []
    for sid, sname in BB_STATIONS.items():
        iat = bb.loc[bb["end_station_id"] == sid, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"Bluebikes — {sname}", iat))

    for direction in sorted(mbta["direction"].dropna().unique()):
        dir_label = {0: "Southbound", 1: "Northbound"}.get(direction, f"Dir {direction}")
        iat = mbta.loc[mbta["direction"] == direction, "interarrival_sec"].dropna()
        iat = iat[iat > 0].values
        datasets.append((f"MBTA Red Line — {dir_label}", iat))

    dist_objs = {
        "Exponential": stats.expon,
        "Log-normal": stats.lognorm,
        "Weibull": stats.weibull_min,
        "Gamma": stats.gamma,
    }

    for label, iat in datasets:
        print(f"\n{'='*70}")
        print(f"  {label}  (N={len(iat):,})")
        print(f"{'='*70}")

        sdf = fit_results[fit_results["system"] == label]

        # --- KS test ---
        print(f"\n  Kolmogorov-Smirnov Test:")
        print(f"  {'Distribution':<16} {'KS Stat':>10} {'p-value':>12}  {'Reject H0?'}")
        print(f"  {'-'*16} {'-'*10} {'-'*12}  {'-'*12}")

        for _, row in sdf.iterrows():
            dname = row["distribution"]
            dist = dist_objs[dname]
            params = row["params"]
            ks_stat, ks_p = stats.kstest(iat, dist.cdf, args=params)
            reject = "YES (p<0.05)" if ks_p < 0.05 else "no"
            print(f"  {dname:<16} {ks_stat:>10.6f} {ks_p:>12.4e}  {reject}")

        # --- Anderson-Darling for exponential ---
        print(f"\n  Anderson-Darling Test (exponential):")
        ad_result = stats.anderson(iat, dist="expon")
        print(f"  Statistic: {ad_result.statistic:.4f}")
        for sl, cv in zip(ad_result.significance_level, ad_result.critical_values):
            reject = "REJECT" if ad_result.statistic > cv else "fail to reject"
            print(f"    {sl}% significance: critical={cv:.4f} → {reject}")

        # --- Chi-squared test ---
        print(f"\n  Chi-Squared Test (30 bins):")
        print(f"  {'Distribution':<16} {'χ² Stat':>12} {'p-value':>12}  {'Reject H0?'}")
        print(f"  {'-'*16} {'-'*12} {'-'*12}  {'-'*12}")

        n_bins = 30
        for _, row in sdf.iterrows():
            dname = row["distribution"]
            dist = dist_objs[dname]
            params = row["params"]

            # Create bins based on quantiles of the fitted distribution
            bin_edges = dist.ppf(np.linspace(0, 1, n_bins + 1), *params)
            bin_edges[0] = 0
            bin_edges[-1] = np.inf

            observed, _ = np.histogram(iat, bins=bin_edges)
            expected = np.full(n_bins, len(iat) / n_bins)

            # Only test bins with expected count >= 5
            mask = expected >= 5
            if mask.sum() >= 3:
                chi2_stat, chi2_p = stats.chisquare(observed[mask], expected[mask])
                n_params = len(params) - 1  # subtract fixed loc
                # Adjust df for estimated parameters
                dof = mask.sum() - 1 - n_params
                if dof > 0:
                    chi2_p = 1 - stats.chi2.cdf(chi2_stat, dof)
                reject = "YES (p<0.05)" if chi2_p < 0.05 else "no"
                print(f"  {dname:<16} {chi2_stat:>12.2f} {chi2_p:>12.4e}  {reject}")
            else:
                print(f"  {dname:<16} {'insufficient bins':>30}")


if __name__ == "__main__":
    print("Loading data (with fullness exclusion)...")
    bb, mbta = load_data(exclude_fullness=True)

    print("Plotting Step 2.2.1: Histograms and CDFs...")
    plot_histograms_and_cdfs(bb, mbta)

    print("\n\nStep 2.2.2–2.2.3: Distribution fitting...")
    fit_results = fit_distributions(bb, mbta)

    print("\nPlotting fitted distributions...")
    plot_fitted_distributions(bb, mbta, fit_results)

    print("\n\nStep 2.2.4: Goodness-of-fit tests...")
    goodness_of_fit_tests(bb, mbta, fit_results)

    print("\nDone.")
