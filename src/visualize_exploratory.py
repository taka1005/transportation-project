"""
Exploratory visualizations for Bluebikes and MBTA arrival data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

BB_STATIONS = {"M32004": "Kendall T", "M32042": "MIT Vassar St"}


def load_data():
    bb = pd.read_parquet(PROCESSED / "bb_arrivals.parquet")
    bb["arrival_time"] = pd.to_datetime(bb["arrival_time"])
    mbta = pd.read_parquet(PROCESSED / "mbta_arrivals.parquet")
    mbta["arrival_time"] = pd.to_datetime(mbta["arrival_time"], utc=True)
    mbta["arrival_time"] = mbta["arrival_time"].dt.tz_convert("America/New_York")
    return bb, mbta


def plot_bb_arrivals_by_hour(bb):
    """Bluebikes arrivals by hour of day, per station."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for i, (sid, sname) in enumerate(BB_STATIONS.items()):
        subset = bb[bb["end_station_id"] == sid]
        subset["hour"] = subset["arrival_time"].dt.hour
        counts = subset.groupby("hour").size()
        axes[i].bar(counts.index, counts.values, color="steelblue", alpha=0.8)
        axes[i].set_title(f"{sname} ({sid})")
        axes[i].set_xlabel("Hour of Day")
        axes[i].set_xticks(range(0, 24, 2))
    axes[0].set_ylabel("Total Arrivals (Sep–Dec 2025)")
    fig.suptitle("Bluebikes: Arrival Counts by Hour of Day", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "bb_arrivals_by_hour.png", dpi=150)
    print(f"  Saved: {FIGURES / 'bb_arrivals_by_hour.png'}")


def plot_bb_arrivals_by_dow(bb):
    """Bluebikes arrivals by day of week, per station."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, (sid, sname) in enumerate(BB_STATIONS.items()):
        subset = bb[bb["end_station_id"] == sid]
        subset["dow"] = subset["arrival_time"].dt.dayofweek
        counts = subset.groupby("dow").size().reindex(range(7), fill_value=0)
        axes[i].bar(range(7), counts.values, color="darkorange", alpha=0.8)
        axes[i].set_title(f"{sname} ({sid})")
        axes[i].set_xticks(range(7))
        axes[i].set_xticklabels(dow_labels)
        axes[i].set_xlabel("Day of Week")
    axes[0].set_ylabel("Total Arrivals (Sep–Dec 2025)")
    fig.suptitle("Bluebikes: Arrival Counts by Day of Week", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "bb_arrivals_by_dow.png", dpi=150)
    print(f"  Saved: {FIGURES / 'bb_arrivals_by_dow.png'}")


def plot_bb_daily_arrivals(bb):
    """Bluebikes daily arrival counts over time."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    for i, (sid, sname) in enumerate(BB_STATIONS.items()):
        subset = bb[bb["end_station_id"] == sid]
        daily = subset.set_index("arrival_time").resample("D").size()
        axes[i].plot(daily.index, daily.values, color="steelblue", linewidth=0.8)
        axes[i].fill_between(daily.index, daily.values, alpha=0.3, color="steelblue")
        axes[i].set_title(f"{sname} ({sid})")
        axes[i].set_ylabel("Daily Arrivals")
        axes[i].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        axes[i].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    fig.suptitle("Bluebikes: Daily Arrival Counts (Sep–Dec 2025)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "bb_daily_arrivals.png", dpi=150)
    print(f"  Saved: {FIGURES / 'bb_daily_arrivals.png'}")


def plot_bb_interarrival_hist(bb):
    """Histogram of Bluebikes inter-arrival times."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, (sid, sname) in enumerate(BB_STATIONS.items()):
        subset = bb[(bb["end_station_id"] == sid) & (bb["interarrival_sec"].notna())]
        iat = subset["interarrival_sec"]
        # Clip to reasonable range for visualization
        iat_clipped = iat[iat.between(0, iat.quantile(0.99))]
        mean_iat = iat_clipped.mean()
        axes[i].hist(iat_clipped, bins=80, density=True, color="steelblue", alpha=0.7,
                     edgecolor="white", linewidth=0.3)
        # Overlay exponential fit
        x = np.linspace(0, iat_clipped.max(), 300)
        lam = 1.0 / mean_iat
        axes[i].plot(x, lam * np.exp(-lam * x), "r-", linewidth=2,
                     label=f"Exp(λ={lam:.4f})")
        axes[i].set_title(f"{sname} ({sid})\nMean={mean_iat:.0f}s, CV={iat_clipped.std()/mean_iat:.2f}")
        axes[i].set_xlabel("Inter-arrival Time (seconds)")
        axes[i].set_ylabel("Density")
        axes[i].legend()
    fig.suptitle("Bluebikes: Inter-arrival Time Distribution", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "bb_interarrival_hist.png", dpi=150)
    print(f"  Saved: {FIGURES / 'bb_interarrival_hist.png'}")


def plot_mbta_headway_by_hour(mbta):
    """MBTA headway by hour of day."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, direction in enumerate(["North", "South"]):
        subset = mbta[(mbta["direction"] == direction) & (~mbta["disruption"])]
        subset = subset.copy()
        subset["hour"] = subset["arrival_time"].dt.hour
        hourly = subset.groupby("hour")["headway_trunk_seconds"].agg(["mean", "std"])
        axes[i].bar(hourly.index, hourly["mean"] / 60, yerr=hourly["std"] / 60,
                    color="forestgreen", alpha=0.8, capsize=3)
        axes[i].set_title(f"Direction: {direction}")
        axes[i].set_xlabel("Hour of Day")
        axes[i].set_ylabel("Headway (minutes)")
        axes[i].set_xticks(range(0, 24, 2))
    fig.suptitle("MBTA Red Line (Kendall/MIT): Average Headway by Hour\n(disruptions excluded)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "mbta_headway_by_hour.png", dpi=150)
    print(f"  Saved: {FIGURES / 'mbta_headway_by_hour.png'}")


def plot_mbta_interarrival_hist(mbta):
    """Histogram of MBTA inter-arrival times (by direction)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, direction in enumerate(["North", "South"]):
        subset = mbta[
            (mbta["direction"] == direction)
            & (~mbta["disruption"])
            & (mbta["interarrival_sec"].notna())
        ]
        iat = subset["interarrival_sec"]
        iat_clipped = iat[iat.between(0, iat.quantile(0.99))]
        mean_iat = iat_clipped.mean()
        axes[i].hist(iat_clipped / 60, bins=80, density=True, color="forestgreen",
                     alpha=0.7, edgecolor="white", linewidth=0.3)
        x = np.linspace(0, iat_clipped.max() / 60, 300)
        lam = 1.0 / (mean_iat / 60)
        axes[i].plot(x, lam * np.exp(-lam * x), "r-", linewidth=2,
                     label=f"Exp(λ={lam:.2f}/min)")
        axes[i].set_title(f"Direction: {direction}\nMean={mean_iat/60:.1f}min, CV={iat_clipped.std()/mean_iat:.2f}")
        axes[i].set_xlabel("Inter-arrival Time (minutes)")
        axes[i].set_ylabel("Density")
        axes[i].legend()
    fig.suptitle("MBTA Red Line (Kendall/MIT): Inter-arrival Time Distribution\n(disruptions excluded)",
                 fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "mbta_interarrival_hist.png", dpi=150)
    print(f"  Saved: {FIGURES / 'mbta_interarrival_hist.png'}")


def plot_bb_inventory(sid, sname):
    """Plot reconstructed inventory over a sample week."""
    inv = pd.read_parquet(PROCESSED / f"bb_inventory_{sid}.parquet")
    inv["time"] = pd.to_datetime(inv["time"])
    # Pick a sample week (first full week of October)
    start = pd.Timestamp("2025-10-06")
    end = pd.Timestamp("2025-10-13")
    week = inv[(inv["time"] >= start) & (inv["time"] < end)]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(week["time"], week["cumulative"], color="steelblue", linewidth=0.8)
    ax.fill_between(week["time"], week["cumulative"], alpha=0.3, color="steelblue")
    # Shade full-capacity periods
    if week["at_capacity"].any():
        full_periods = week[week["at_capacity"]]
        ax.scatter(full_periods["time"], full_periods["cumulative"],
                   color="red", s=5, alpha=0.5, label="At estimated capacity")
        ax.legend()
    ax.set_title(f"{sname} ({sid}): Estimated Dock Inventory (Oct 6–12, 2025)", fontweight="bold")
    ax.set_xlabel("Date/Time")
    ax.set_ylabel("Estimated Bikes at Station")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %m/%d %H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURES / f"bb_inventory_{sid}.png", dpi=150)
    print(f"  Saved: {FIGURES / f'bb_inventory_{sid}.png'}")


if __name__ == "__main__":
    print("Loading processed data...")
    bb, mbta = load_data()

    print("\n--- Bluebikes Visualizations ---")
    plot_bb_arrivals_by_hour(bb)
    plot_bb_arrivals_by_dow(bb)
    plot_bb_daily_arrivals(bb)
    plot_bb_interarrival_hist(bb)
    for sid, sname in BB_STATIONS.items():
        plot_bb_inventory(sid, sname)

    print("\n--- MBTA Visualizations ---")
    plot_mbta_headway_by_hour(mbta)
    plot_mbta_interarrival_hist(mbta)

    print("\nAll visualizations complete.")
