"""
Phase 2: Descriptive Arrival-Process Analysis
Step 2.1: Summary statistics for inter-arrival times
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROCESSED = Path("data/processed")


def assign_operating_date(df, time_col="arrival_time", start_hour=5):
    """
    Assign an operating date to each record. Operating day runs from
    start_hour (5am) to start_hour next day. Arrivals between midnight
    and start_hour belong to the previous operating day.
    """
    t = df[time_col]
    # Remove timezone for consistent arithmetic if present
    if hasattr(t.dt, 'tz') and t.dt.tz is not None:
        t_naive = t.dt.tz_localize(None)
    else:
        t_naive = t
    df["operating_date"] = (t_naive - pd.Timedelta(hours=start_hour)).dt.date
    return df


def compute_intraday_interarrival(df, time_col="arrival_time", group_cols=None):
    """
    Compute inter-arrival times within the same operating day.
    The first arrival of each operating day gets NaN (no overnight gap).
    """
    sort_cols = (group_cols or []) + ["operating_date", time_col]
    group = (group_cols or []) + ["operating_date"]
    df = df.sort_values(sort_cols)
    df["interarrival_sec"] = df.groupby(group)[time_col].diff().dt.total_seconds()
    return df


def summary_stats(series, label):
    """Compute mean, std, CV, skewness for a series of inter-arrival times."""
    clean = series.dropna()
    clean = clean[clean > 0]  # exclude zero or negative values
    n = len(clean)
    mean = clean.mean()
    std = clean.std()
    cv = std / mean if mean > 0 else np.nan
    skew = clean.skew()
    median = clean.median()
    q25 = clean.quantile(0.25)
    q75 = clean.quantile(0.75)
    minimum = clean.min()
    maximum = clean.max()

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  N observations:   {n:,}")
    print(f"  Mean:             {mean:,.1f} sec  ({mean/60:,.1f} min)")
    print(f"  Std deviation:    {std:,.1f} sec  ({std/60:,.1f} min)")
    print(f"  CV (σ/μ):         {cv:.3f}  (Poisson theoretical = 1.0)")
    print(f"  Skewness:         {skew:.3f}")
    print(f"  Median:           {median:,.1f} sec  ({median/60:,.1f} min)")
    print(f"  25th percentile:  {q25:,.1f} sec")
    print(f"  75th percentile:  {q75:,.1f} sec")
    print(f"  Min:              {minimum:,.1f} sec")
    print(f"  Max:              {maximum:,.1f} sec")

    return {"label": label, "n": n, "mean": mean, "std": std, "cv": cv,
            "skewness": skew, "median": median, "min": minimum, "max": maximum}


if __name__ == "__main__":
    # --- Bluebikes ---
    print("Loading Bluebikes arrivals...")
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])
    bb = assign_operating_date(bb)
    bb = compute_intraday_interarrival(bb, group_cols=["end_station_id"])

    results = []
    for station_id in ["M32004", "M32042"]:
        station_name = {"M32004": "Kendall T", "M32042": "MIT Vassar St"}[station_id]
        mask = bb["end_station_id"] == station_id
        iat = bb.loc[mask, "interarrival_sec"]
        r = summary_stats(iat, f"Bluebikes — {station_name} ({station_id})")
        results.append(r)

    # --- MBTA ---
    print("\n\nLoading MBTA arrivals...")
    mbta = pd.read_parquet(PROCESSED / "mbta_arrivals.parquet")
    mbta["arrival_time"] = pd.to_datetime(mbta["arrival_time"])

    # Exclude disruption-flagged records
    if "disruption" in mbta.columns:
        mbta_clean = mbta[~mbta["disruption"]].copy()
        print(f"  Excluded {mbta['disruption'].sum()} disruption records")
    else:
        mbta_clean = mbta.copy()

    mbta_clean = assign_operating_date(mbta_clean)
    mbta_clean = compute_intraday_interarrival(mbta_clean, group_cols=["direction"])

    for direction in sorted(mbta_clean["direction"].dropna().unique()):
        dir_label = {0: "Southbound (Ashmont/Braintree)", 1: "Northbound (Alewife)"}.get(
            direction, f"Direction {direction}")
        mask = mbta_clean["direction"] == direction
        iat = mbta_clean.loc[mask, "interarrival_sec"]
        r = summary_stats(iat, f"MBTA Red Line — {dir_label}")
        results.append(r)

    # --- Summary table ---
    print(f"\n\n{'='*60}")
    print("  Summary Comparison (Overall)")
    print(f"{'='*60}")
    print(f"  {'System':<40} {'CV':>6}  {'Poisson?'}")
    print(f"  {'-'*40} {'-'*6}  {'-'*20}")
    for r in results:
        if r["cv"] > 1.1:
            assessment = "More variable (CV > 1)"
        elif r["cv"] < 0.9:
            assessment = "More regular (CV < 1)"
        else:
            assessment = "Near Poisson (CV ≈ 1)"
        print(f"  {r['label']:<40} {r['cv']:>6.3f}  {assessment}")

    # =================================================================
    # Step 2.1.4: CV by time-of-day (peak vs off-peak) and day-of-week
    # =================================================================
    print(f"\n\n{'='*60}")
    print("  Step 2.1.4: CV by Time-of-Day")
    print(f"{'='*60}")

    def cv_by_hour(df, group_col, label_map, time_col="arrival_time"):
        """Compute CV of inter-arrival times for each hour, grouped by group_col."""
        df = df.copy()
        df["hour"] = df[time_col].dt.hour
        rows = []
        for gval in sorted(df[group_col].dropna().unique()):
            glabel = label_map.get(gval, str(gval))
            gdf = df[df[group_col] == gval]
            for h in range(5, 25):  # operating hours 5am-1am
                actual_h = h % 24
                hdf = gdf[gdf["hour"] == actual_h]
                iat = hdf["interarrival_sec"].dropna()
                iat = iat[iat > 0]
                if len(iat) >= 10:
                    rows.append({
                        "system": glabel, "hour": h,
                        "n": len(iat), "mean": iat.mean(),
                        "cv": iat.std() / iat.mean()
                    })
        return pd.DataFrame(rows)

    # Bluebikes by hour
    bb_station_map = {"M32004": "BB Kendall T", "M32042": "BB MIT Vassar St"}
    bb_hourly = cv_by_hour(bb, "end_station_id", bb_station_map)

    # MBTA by hour
    mbta_dir_map = {0: "MBTA Southbound", 1: "MBTA Northbound"}
    mbta_hourly = cv_by_hour(mbta_clean, "direction", mbta_dir_map)

    hourly = pd.concat([bb_hourly, mbta_hourly], ignore_index=True)

    # Print hourly CV table
    for sys_name in hourly["system"].unique():
        sdf = hourly[hourly["system"] == sys_name]
        print(f"\n  {sys_name}:")
        print(f"  {'Hour':>6} {'N':>7} {'Mean(s)':>9} {'CV':>7}")
        print(f"  {'-'*6} {'-'*7} {'-'*9} {'-'*7}")
        for _, row in sdf.iterrows():
            h_label = f"{row['hour'] % 24:02d}:00"
            print(f"  {h_label:>6} {int(row['n']):>7} {row['mean']:>9.1f} {row['cv']:>7.3f}")

    # Peak vs off-peak summary
    print(f"\n\n{'='*60}")
    print("  Peak vs Off-Peak CV Summary")
    print(f"{'='*60}")
    print("  Peak hours: 7-9am, 4-7pm  |  Off-peak: all other operating hours")
    print(f"\n  {'System':<25} {'Peak CV':>9} {'Off-Peak CV':>13} {'Overall CV':>12}")
    print(f"  {'-'*25} {'-'*9} {'-'*13} {'-'*12}")

    peak_hours = {7, 8, 16, 17, 18}
    for sys_name in hourly["system"].unique():
        sdf = hourly[hourly["system"] == sys_name]
        peak = sdf[sdf["hour"].isin(peak_hours)]
        offpeak = sdf[~sdf["hour"].isin(peak_hours)]
        # Weighted average CV (weighted by N)
        if len(peak) > 0 and peak["n"].sum() > 0:
            peak_cv = (peak["cv"] * peak["n"]).sum() / peak["n"].sum()
        else:
            peak_cv = np.nan
        if len(offpeak) > 0 and offpeak["n"].sum() > 0:
            offpeak_cv = (offpeak["cv"] * offpeak["n"]).sum() / offpeak["n"].sum()
        else:
            offpeak_cv = np.nan
        overall_cv = (sdf["cv"] * sdf["n"]).sum() / sdf["n"].sum()
        print(f"  {sys_name:<25} {peak_cv:>9.3f} {offpeak_cv:>13.3f} {overall_cv:>12.3f}")

    # Day-of-week analysis
    print(f"\n\n{'='*60}")
    print("  Step 2.1.4: CV by Day-of-Week")
    print(f"{'='*60}")

    def cv_by_dow(df, group_col, label_map, time_col="arrival_time"):
        df = df.copy()
        df["dow"] = df[time_col].dt.dayofweek  # 0=Mon, 6=Sun
        dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        rows = []
        for gval in sorted(df[group_col].dropna().unique()):
            glabel = label_map.get(gval, str(gval))
            gdf = df[df[group_col] == gval]
            for d in range(7):
                ddf = gdf[gdf["dow"] == d]
                iat = ddf["interarrival_sec"].dropna()
                iat = iat[iat > 0]
                if len(iat) >= 10:
                    rows.append({
                        "system": glabel, "dow": d, "dow_name": dow_names[d],
                        "n": len(iat), "mean": iat.mean(),
                        "cv": iat.std() / iat.mean()
                    })
        return pd.DataFrame(rows)

    bb_dow = cv_by_dow(bb, "end_station_id", bb_station_map)
    mbta_dow = cv_by_dow(mbta_clean, "direction", mbta_dir_map)
    dow_all = pd.concat([bb_dow, mbta_dow], ignore_index=True)

    for sys_name in dow_all["system"].unique():
        sdf = dow_all[dow_all["system"] == sys_name]
        print(f"\n  {sys_name}:")
        print(f"  {'Day':>5} {'N':>7} {'Mean(s)':>9} {'CV':>7}")
        print(f"  {'-'*5} {'-'*7} {'-'*9} {'-'*7}")
        for _, row in sdf.iterrows():
            print(f"  {row['dow_name']:>5} {int(row['n']):>7} {row['mean']:>9.1f} {row['cv']:>7.3f}")

    # Weekday vs weekend
    print(f"\n\n  {'System':<25} {'Weekday CV':>12} {'Weekend CV':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    for sys_name in dow_all["system"].unique():
        sdf = dow_all[dow_all["system"] == sys_name]
        wd = sdf[sdf["dow"] < 5]
        we = sdf[sdf["dow"] >= 5]
        wd_cv = (wd["cv"] * wd["n"]).sum() / wd["n"].sum() if len(wd) > 0 else np.nan
        we_cv = (we["cv"] * we["n"]).sum() / we["n"].sum() if len(we) > 0 else np.nan
        print(f"  {sys_name:<25} {wd_cv:>12.3f} {we_cv:>12.3f}")

    # =================================================================
    # Section 2.3: Arrival Count Analysis
    # =================================================================
    print(f"\n\n{'='*70}")
    print("  Section 2.3: Arrival Count Analysis")
    print(f"{'='*70}")

    def arrival_count_analysis(df, group_col, label_map, time_col="arrival_time"):
        """
        Steps 2.3.1–2.3.3: Count arrivals in time windows, compute mean vs variance,
        and Index of Dispersion.
        """
        windows = [15, 30, 60]  # minutes
        all_rows = []

        for gval in sorted(df[group_col].dropna().unique()):
            glabel = label_map.get(gval, str(gval))
            gdf = df[df[group_col] == gval].copy()

            # Make time column timezone-naive for consistent binning
            t = gdf[time_col]
            if hasattr(t.dt, 'tz') and t.dt.tz is not None:
                gdf["_time_naive"] = t.dt.tz_localize(None)
            else:
                gdf["_time_naive"] = t

            for w in windows:
                # Bin arrivals into time windows
                gdf["time_bin"] = gdf["_time_naive"].dt.floor(f"{w}min")

                # Include zero-count bins within operating date range
                full_counts = []
                for od in gdf["operating_date"].unique():
                    day_data = gdf[gdf["operating_date"] == od]
                    if len(day_data) == 0:
                        continue
                    # Operating hours: 5am to 1am next day
                    day_start = pd.Timestamp(od) + pd.Timedelta(hours=5)
                    day_end = pd.Timestamp(od) + pd.Timedelta(hours=25)
                    full_idx = pd.date_range(day_start, day_end, freq=f"{w}min", inclusive="left")
                    day_counts = day_data.groupby("time_bin").size().reindex(full_idx, fill_value=0)
                    full_counts.append(day_counts)

                if len(full_counts) == 0:
                    continue
                counts_series = pd.concat(full_counts)

                mean_c = counts_series.mean()
                var_c = counts_series.var()
                iod = var_c / mean_c if mean_c > 0 else np.nan  # Index of Dispersion

                all_rows.append({
                    "system": glabel, "window_min": w,
                    "n_windows": len(counts_series),
                    "mean": mean_c, "variance": var_c, "iod": iod,
                })

        return pd.DataFrame(all_rows)

    # Bluebikes
    bb_station_map = {"M32004": "BB Kendall T", "M32042": "BB MIT Vassar St"}
    bb_counts = arrival_count_analysis(bb, "end_station_id", bb_station_map)

    # MBTA
    mbta_dir_map = {0: "MBTA Southbound", 1: "MBTA Northbound"}
    mbta_counts = arrival_count_analysis(mbta_clean, "direction", mbta_dir_map)

    count_results = pd.concat([bb_counts, mbta_counts], ignore_index=True)

    # Print results
    print(f"\n  Step 2.3.1–2.3.3: Arrival Counts by Time Window")
    print(f"  (IoD = Index of Dispersion = Var/Mean; Poisson → IoD = 1.0)")
    print(f"\n  {'System':<22} {'Window':>8} {'N bins':>8} {'Mean':>8} {'Var':>10} {'IoD':>8} {'Assessment'}")
    print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*20}")

    for _, row in count_results.iterrows():
        if row["iod"] > 1.1:
            assessment = "Overdispersed"
        elif row["iod"] < 0.9:
            assessment = "Underdispersed"
        else:
            assessment = "≈ Poisson"
        print(f"  {row['system']:<22} {row['window_min']:>5}min {int(row['n_windows']):>8} "
              f"{row['mean']:>8.2f} {row['variance']:>10.2f} {row['iod']:>8.3f} {assessment}")

    # --- Step 2.3.4: Segment by time-of-day and day-of-week ---
    print(f"\n\n  Step 2.3.4: IoD by Peak/Off-Peak (60-min window)")

    def iod_by_period(df, group_col, label_map, time_col="arrival_time", window_min=60):
        """Compute IoD for peak and off-peak periods."""
        peak_hours = {7, 8, 16, 17, 18}
        rows = []

        for gval in sorted(df[group_col].dropna().unique()):
            glabel = label_map.get(gval, str(gval))
            gdf = df[df[group_col] == gval].copy()
            t = gdf[time_col]
            if hasattr(t.dt, 'tz') and t.dt.tz is not None:
                gdf["_time_naive"] = t.dt.tz_localize(None)
            else:
                gdf["_time_naive"] = t
            gdf["time_bin"] = gdf["_time_naive"].dt.floor(f"{window_min}min")
            gdf["hour"] = gdf["_time_naive"].dt.hour

            for period_name, hour_mask in [("Peak", True), ("Off-Peak", False)]:
                if period_name == "Peak":
                    pdf = gdf[gdf["hour"].isin(peak_hours)]
                else:
                    pdf = gdf[~gdf["hour"].isin(peak_hours)]

                if len(pdf) == 0:
                    continue

                counts = pdf.groupby("time_bin").size()
                mean_c = counts.mean()
                var_c = counts.var()
                iod = var_c / mean_c if mean_c > 0 else np.nan

                rows.append({
                    "system": glabel, "period": period_name,
                    "n_windows": len(counts), "mean": mean_c,
                    "variance": var_c, "iod": iod,
                })

        return pd.DataFrame(rows)

    bb_period = iod_by_period(bb, "end_station_id", bb_station_map)
    mbta_period = iod_by_period(mbta_clean, "direction", mbta_dir_map)
    period_results = pd.concat([bb_period, mbta_period], ignore_index=True)

    print(f"\n  {'System':<22} {'Period':>10} {'Mean':>8} {'Var':>10} {'IoD':>8}")
    print(f"  {'-'*22} {'-'*10} {'-'*8} {'-'*10} {'-'*8}")
    for _, row in period_results.iterrows():
        print(f"  {row['system']:<22} {row['period']:>10} {row['mean']:>8.2f} "
              f"{row['variance']:>10.2f} {row['iod']:>8.3f}")

    # Weekday vs weekend
    print(f"\n\n  Step 2.3.4: IoD by Weekday/Weekend (60-min window)")

    def iod_by_daytype(df, group_col, label_map, time_col="arrival_time", window_min=60):
        rows = []
        for gval in sorted(df[group_col].dropna().unique()):
            glabel = label_map.get(gval, str(gval))
            gdf = df[df[group_col] == gval].copy()
            t = gdf[time_col]
            if hasattr(t.dt, 'tz') and t.dt.tz is not None:
                gdf["_time_naive"] = t.dt.tz_localize(None)
            else:
                gdf["_time_naive"] = t
            gdf["time_bin"] = gdf["_time_naive"].dt.floor(f"{window_min}min")
            gdf["dow"] = gdf["_time_naive"].dt.dayofweek

            for dtype, mask_fn in [("Weekday", lambda d: d < 5), ("Weekend", lambda d: d >= 5)]:
                pdf = gdf[mask_fn(gdf["dow"])]
                if len(pdf) == 0:
                    continue
                counts = pdf.groupby("time_bin").size()
                mean_c = counts.mean()
                var_c = counts.var()
                iod = var_c / mean_c if mean_c > 0 else np.nan
                rows.append({"system": glabel, "daytype": dtype, "mean": mean_c,
                             "variance": var_c, "iod": iod})
        return pd.DataFrame(rows)

    bb_daytype = iod_by_daytype(bb, "end_station_id", bb_station_map)
    mbta_daytype = iod_by_daytype(mbta_clean, "direction", mbta_dir_map)
    daytype_results = pd.concat([bb_daytype, mbta_daytype], ignore_index=True)

    print(f"\n  {'System':<22} {'Day Type':>10} {'Mean':>8} {'Var':>10} {'IoD':>8}")
    print(f"  {'-'*22} {'-'*10} {'-'*8} {'-'*10} {'-'*8}")
    for _, row in daytype_results.iterrows():
        print(f"  {row['system']:<22} {row['daytype']:>10} {row['mean']:>8.2f} "
              f"{row['variance']:>10.2f} {row['iod']:>8.3f}")
