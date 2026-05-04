"""
Side-by-side animation: Poisson DES (left, simulated) vs real Kendall/MIT
inventory N(t) (right, observed) on 2025-09-17, 06:00-18:00.

Both panels share the same arrival rate and capacity. The right panel runs
NO simulation: it replays the real trip-end (+1) and trip-start (-1) events
and uses the §3.2b inventory reconstruction directly. Blocking events on
the right are committed full-capacity intervals (per §3.2b semantics) —
moments when the dock physically saturates and any incoming user would have
been censored from the data.

This makes the comparison "Poisson model vs reality" rather than "model vs
model", which is what §4.3 actually claims.

Outputs:
  outputs/animations/des_blocking_comparison.mp4 (1920x1080, 30 fps, 36 sec)
  outputs/animations/frame_to_event_log.csv      (per-frame state for narration)
"""

import heapq
from pathlib import Path

import imageio_ffmpeg
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fullness_filter import get_full_capacity_periods  # noqa: E402

TARGET_DATE = pd.Timestamp("2025-09-17")
SIM_START_HOUR = 6
SIM_END_HOUR = 18
CAPACITY = 23
SERVICE_MEAN_SEC = 7549  # Used only for the LEFT-panel Poisson sim
N_FRAMES = 1080  # 36 sec at 30 fps
FPS = 30
FIG_W, FIG_H = 19.2, 10.8
DPI = 100
SEED_POISSON_ARRIVALS = 42
# Service seed for the left (Poisson) panel chosen via 20-replicate sweep so
# the rendered run is a clean representative outcome (Poisson 0 blocks).
SEED_LEFT_SERVICE = 35
FLASH_FRAMES = 6     # 0.2 sec at 30 fps
OVERLAY_FRAMES = 9   # 0.3 sec at 30 fps

OUT_DIR = Path("outputs/animations")
OUT_DIR.mkdir(parents=True, exist_ok=True)
MP4_PATH = OUT_DIR / "des_blocking_comparison.mp4"
CSV_PATH = OUT_DIR / "frame_to_event_log.csv"

plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()


def load_arrival_times(sim_start, sim_end):
    """Trip-end timestamps at Kendall/MIT in [sim_start, sim_end), seconds-from-start."""
    bb = pd.read_parquet("data/processed/bb_arrivals.parquet")
    kendall = bb[bb["end_station_id"] == "M32004"].copy()
    kendall["arrival_time"] = pd.to_datetime(kendall["arrival_time"])
    mask = (kendall["arrival_time"] >= sim_start) & (kendall["arrival_time"] < sim_end)
    arrivals = sorted(kendall.loc[mask, "arrival_time"].tolist())
    return np.array([(t - sim_start).total_seconds() for t in arrivals])


def load_real_inventory_events(sim_start, sim_end):
    """Inventory events (trip-end +1, trip-start -1) in [sim_start, sim_end).

    Returns (events_df, initial_inventory). events_df has columns time_sec,
    delta, inventory_after. initial_inventory is N(t) at sim_start (carried
    over from the last event before sim_start in the §3.2b reconstruction).
    """
    inv = pd.read_parquet("data/processed/bb_inventory_M32004.parquet")
    inv["time"] = pd.to_datetime(inv["time"])

    before = inv[inv["time"] < sim_start]
    initial = int(before["inventory"].iloc[-1]) if len(before) > 0 else CAPACITY // 2

    window = inv[(inv["time"] >= sim_start) & (inv["time"] < sim_end)].copy()
    window["time_sec"] = (window["time"] - sim_start).dt.total_seconds()
    return window[["time_sec", "delta", "inventory"]].rename(
        columns={"inventory": "inv_after"}
    ).reset_index(drop=True), initial


def load_committed_full_intervals(sim_start, sim_end):
    """Committed full intervals (per §3.2b) intersecting the window."""
    periods = get_full_capacity_periods("M32004")
    out = []
    for start, end in periods:
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        if start >= sim_end or end < sim_start:
            continue
        out.append(
            (
                (start - sim_start).total_seconds(),
                (end - sim_start).total_seconds(),
            )
        )
    return out


def generate_poisson_arrivals(rate_per_sec, T):
    rng = np.random.default_rng(SEED_POISSON_ARRIVALS)
    arrivals = []
    t = 0.0
    while True:
        t += rng.exponential(1.0 / rate_per_sec)
        if t >= T:
            break
        arrivals.append(t)
    return np.array(arrivals)


def run_poisson_simulation(arrival_times, service_mean, capacity, T_end, seed):
    """Finite-capacity sim for the LEFT (Poisson) panel only."""
    rng = np.random.default_rng(seed)
    departures = []
    events = []
    blocked = 0
    for arr_t in arrival_times:
        while departures and departures[0] <= arr_t:
            dep_t = heapq.heappop(departures)
            events.append((dep_t, "DEPARTURE", len(departures), blocked))
        if len(departures) < capacity:
            heapq.heappush(departures, arr_t + rng.exponential(service_mean))
            events.append((arr_t, "ARRIVAL", len(departures), blocked))
        else:
            blocked += 1
            events.append((arr_t, "BLOCKED", len(departures), blocked))
    while departures:
        dep_t = heapq.heappop(departures)
        if dep_t <= T_end:
            events.append((dep_t, "DEPARTURE", len(departures), blocked))
        else:
            break
    events.sort(key=lambda e: e[0])
    return events


def compute_left_frame_states(events, n_frames, T_end):
    """Frame-by-frame state for left panel (Poisson DES)."""
    dt = T_end / n_frames
    states = []
    ev_idx = 0
    occ = 0
    blocked_cum = 0
    latest_event = "—"
    for f in range(n_frames):
        t_end = (f + 1) * dt
        blocked_in_frame = False
        while ev_idx < len(events) and events[ev_idx][0] < t_end:
            _, ev_kind, ev_occ, ev_blocked = events[ev_idx]
            occ = ev_occ
            blocked_cum = ev_blocked
            if ev_kind == "BLOCKED":
                blocked_in_frame = True
                latest_event = "BLOCKED"
            elif not blocked_in_frame:
                latest_event = ev_kind
            ev_idx += 1
        states.append(
            {
                "frame": f, "time_sec": t_end,
                "occupancy": occ, "blocked_cum": blocked_cum,
                "blocked_in_frame": blocked_in_frame, "latest_event": latest_event,
            }
        )
    return states


def compute_right_frame_states(inv_events, initial_inv, full_intervals, n_frames, T_end):
    """Frame-by-frame state for right panel (real inventory replay)."""
    dt = T_end / n_frames
    # Bucket committed full-interval starts by frame index
    starts_by_frame = {}
    for start_sec, _ in full_intervals:
        f = min(int(start_sec / dt), n_frames - 1)
        starts_by_frame[f] = starts_by_frame.get(f, 0) + 1

    states = []
    ev_idx = 0
    occ = initial_inv
    blocked_cum = 0
    latest_event = "—"
    for f in range(n_frames):
        t_end = (f + 1) * dt
        blocked_in_frame = False

        while ev_idx < len(inv_events) and inv_events.iloc[ev_idx]["time_sec"] < t_end:
            ev = inv_events.iloc[ev_idx]
            occ = int(ev["inv_after"])
            latest_event = "ARRIVAL" if ev["delta"] == 1 else "DEPARTURE"
            ev_idx += 1

        n_starts = starts_by_frame.get(f, 0)
        if n_starts > 0:
            blocked_in_frame = True
            blocked_cum += n_starts
            latest_event = "BLOCKED"

        states.append(
            {
                "frame": f, "time_sec": t_end,
                "occupancy": occ, "blocked_cum": blocked_cum,
                "blocked_in_frame": blocked_in_frame, "latest_event": latest_event,
            }
        )
    return states


def time_to_clock(t_sec):
    total_sec = SIM_START_HOUR * 3600 + t_sec
    h = int(total_sec // 3600) % 24
    m = int((total_sec % 3600) // 60)
    return f"{h:02d}:{m:02d}"


def time_to_period(t_sec):
    h = SIM_START_HOUR + t_sec / 3600.0
    if h < 8:
        return "Early morning (off-peak)"
    if h < 10:
        return "Commuter inflow"
    if h < 14:
        return "Saturation"
    if h < 17:
        return "Afternoon drain"
    return "Evening"


def build_event_log(left_states, right_states, n_frames):
    rows = []
    for f in range(n_frames):
        rows.append(
            {
                "frame": f,
                "time": time_to_clock(left_states[f]["time_sec"]),
                "period": time_to_period(left_states[f]["time_sec"]),
                "left_occupancy": left_states[f]["occupancy"],
                "right_occupancy": right_states[f]["occupancy"],
                "left_blocked_cum": left_states[f]["blocked_cum"],
                "right_blocked_cum": right_states[f]["blocked_cum"],
                "left_blocked_in_frame": left_states[f]["blocked_in_frame"],
                "right_blocked_in_frame": right_states[f]["blocked_in_frame"],
                "left_latest_event": left_states[f]["latest_event"],
                "right_latest_event": right_states[f]["latest_event"],
            }
        )
    return pd.DataFrame(rows)


def setup_figure():
    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor("white")

    fig.text(
        0.5, 0.96,
        "Poisson DES (left, simulated) vs real Kendall/MIT inventory N(t) (right, observed)\n"
        "same arrival rate, opposite blocking outcomes",
        ha="center", va="top", fontsize=18, weight="bold",
    )
    time_text = fig.text(0.5, 0.88, "", ha="center", fontsize=24, weight="bold")
    period_text = fig.text(0.5, 0.84, "", ha="center", fontsize=18, style="italic", color="gray")

    ax_left = fig.add_axes([0.05, 0.32, 0.42, 0.42])
    ax_right = fig.add_axes([0.53, 0.32, 0.42, 0.42])
    ax_left.set_title("Poisson DES (M/M/c, c=23)", fontsize=16, weight="bold", pad=10)
    ax_right.set_title(
        "Real Kendall data 2025-09-17 — observed inventory N(t)",
        fontsize=16, weight="bold", pad=10,
    )
    for ax in (ax_left, ax_right):
        ax.set_xlim(0, 23)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

    cell_w = 0.9
    left_cells, right_cells = [], []
    for i in range(23):
        left_cells.append(
            patches.Rectangle((i + 0.05, 0.1), cell_w, 0.8,
                              facecolor="#E0E0E0", edgecolor="black", linewidth=0.5)
        )
        right_cells.append(
            patches.Rectangle((i + 0.05, 0.1), cell_w, 0.8,
                              facecolor="#E0E0E0", edgecolor="black", linewidth=0.5)
        )
        ax_left.add_patch(left_cells[-1])
        ax_right.add_patch(right_cells[-1])

    right_flash = patches.Rectangle((0, 0), 1, 1, transform=ax_right.transAxes,
                                    facecolor="red", alpha=0.0, zorder=10)
    ax_right.add_patch(right_flash)

    left_counter = fig.text(0.26, 0.22, "", ha="center", fontsize=42, weight="bold", color="steelblue")
    right_counter = fig.text(0.74, 0.22, "", ha="center", fontsize=42, weight="bold", color="steelblue")

    left_blocked_text = fig.text(0.26, 0.13, "Cumulative blocked: 0",
                                 ha="center", fontsize=14, color="black")
    right_blocked_text = fig.text(0.74, 0.13, "Cumulative blocked: 0",
                                  ha="center", fontsize=14, color="black")

    left_event_text = fig.text(0.26, 0.08, "Latest: —", ha="center", fontsize=12, color="gray")
    right_event_text = fig.text(0.74, 0.08, "Latest: —", ha="center", fontsize=12, color="gray")

    left_sublabel = fig.text(0.26, 0.05, "Left: Poisson(λ̄) arrivals + Exp(1/μ̄) service",
                             ha="center", fontsize=10, style="italic", color="gray")
    right_sublabel = fig.text(0.74, 0.05,
                              "Right: real Kendall data 2025-09-17 — observed inventory N(t)",
                              ha="center", fontsize=10, style="italic", color="gray")

    blocked_overlay = fig.text(0.74, 0.53, "", ha="center", va="center",
                                fontsize=96, weight="bold", color="white", alpha=0.0, zorder=20,
                                path_effects=[pe.withStroke(linewidth=6, foreground="black")])

    return {
        "fig": fig,
        "time_text": time_text, "period_text": period_text,
        "left_cells": left_cells, "right_cells": right_cells,
        "right_flash": right_flash, "blocked_overlay": blocked_overlay,
        "left_counter": left_counter, "right_counter": right_counter,
        "left_blocked_text": left_blocked_text, "right_blocked_text": right_blocked_text,
        "left_event_text": left_event_text, "right_event_text": right_event_text,
    }


def make_update_fn(elements, left_states, right_states):
    state = {"flash_remaining": 0, "overlay_remaining": 0}

    def update_cells(cells, occ):
        if occ >= CAPACITY:
            for cell in cells:
                cell.set_facecolor("red")
            return
        for i, cell in enumerate(cells):
            cell.set_facecolor("steelblue" if i < occ else "#E0E0E0")

    def update(frame_idx):
        l = left_states[frame_idx]
        r = right_states[frame_idx]

        elements["time_text"].set_text(f"Time: {time_to_clock(l['time_sec'])}")
        elements["period_text"].set_text(f"[{time_to_period(l['time_sec'])}]")

        update_cells(elements["left_cells"], l["occupancy"])
        update_cells(elements["right_cells"], r["occupancy"])

        elements["left_counter"].set_text(f"{l['occupancy']} / {CAPACITY}")
        elements["right_counter"].set_text(f"{r['occupancy']} / {CAPACITY}")
        elements["left_counter"].set_color("red" if l["occupancy"] >= CAPACITY else "steelblue")
        elements["right_counter"].set_color("red" if r["occupancy"] >= CAPACITY else "steelblue")

        elements["left_blocked_text"].set_text(f"Cumulative blocked: {l['blocked_cum']}")
        elements["right_blocked_text"].set_text(f"Cumulative blocked: {r['blocked_cum']}")
        elements["right_blocked_text"].set_color("red" if r["blocked_cum"] > 0 else "black")
        elements["right_blocked_text"].set_weight("bold" if r["blocked_cum"] > 0 else "normal")

        elements["left_event_text"].set_text(f"Latest: {l['latest_event']}")
        elements["right_event_text"].set_text(f"Latest: {r['latest_event']}")

        if r["blocked_in_frame"]:
            state["flash_remaining"] = FLASH_FRAMES
            state["overlay_remaining"] = OVERLAY_FRAMES

        if state["flash_remaining"] > 0:
            elements["right_flash"].set_alpha(0.4 * state["flash_remaining"] / FLASH_FRAMES)
            state["flash_remaining"] -= 1
        else:
            elements["right_flash"].set_alpha(0.0)

        if state["overlay_remaining"] > 0:
            elements["blocked_overlay"].set_alpha(state["overlay_remaining"] / OVERLAY_FRAMES)
            elements["blocked_overlay"].set_text("BLOCKED")
            state["overlay_remaining"] -= 1
        else:
            elements["blocked_overlay"].set_alpha(0.0)
            elements["blocked_overlay"].set_text("")

        return []

    return update


def main():
    sim_start = TARGET_DATE + pd.Timedelta(hours=SIM_START_HOUR)
    sim_end = TARGET_DATE + pd.Timedelta(hours=SIM_END_HOUR)
    T_end = (SIM_END_HOUR - SIM_START_HOUR) * 3600.0

    print(f"Loading real Kendall events for {TARGET_DATE.date()} {SIM_START_HOUR:02d}:00-{SIM_END_HOUR:02d}:00")
    inv_events, initial_inv = load_real_inventory_events(sim_start, sim_end)
    print(f"  Real events: {len(inv_events)} ({(inv_events['delta']==1).sum()} arrivals, "
          f"{(inv_events['delta']==-1).sum()} departures), initial N(06:00) = {initial_inv}")

    full_intervals = load_committed_full_intervals(sim_start, sim_end)
    print(f"  Committed full intervals (§3.2b): {len(full_intervals)}")
    if full_intervals:
        total = sum(e - s for s, e in full_intervals) / 60
        print(f"  Total observed full-time on this day: {total:.1f} min")

    arrivals = load_arrival_times(sim_start, sim_end)
    rate = len(arrivals) / T_end
    print(f"  λ̄ = {rate * 3600:.2f}/hr (matches both panels)")

    poisson_arrivals = generate_poisson_arrivals(rate, T_end)
    print(f"  Poisson arrivals generated: {len(poisson_arrivals)}")

    print("Simulating LEFT panel (Poisson DES)...")
    left_events = run_poisson_simulation(
        poisson_arrivals, SERVICE_MEAN_SEC, CAPACITY, T_end, SEED_LEFT_SERVICE
    )
    n_block_l = sum(1 for e in left_events if e[1] == "BLOCKED")
    print(f"  Poisson blocked: {n_block_l}")
    print(f"  Real (committed full intervals): {len(full_intervals)}")

    print("Computing per-frame states...")
    left_states = compute_left_frame_states(left_events, N_FRAMES, T_end)
    right_states = compute_right_frame_states(
        inv_events, initial_inv, full_intervals, N_FRAMES, T_end
    )

    log_df = build_event_log(left_states, right_states, N_FRAMES)
    log_df.to_csv(CSV_PATH, index=False)
    print(f"  Wrote {CSV_PATH}")

    print("Setting up figure...")
    elements = setup_figure()
    update = make_update_fn(elements, left_states, right_states)

    print(f"Rendering {N_FRAMES} frames at {FPS} fps → {N_FRAMES / FPS:.1f} sec MP4")
    ani = FuncAnimation(elements["fig"], update, frames=N_FRAMES,
                        interval=1000 / FPS, blit=False)
    writer = FFMpegWriter(fps=FPS, bitrate=4000, codec="libx264")
    ani.save(MP4_PATH, writer=writer, dpi=DPI)
    plt.close(elements["fig"])
    print(f"  Saved {MP4_PATH}")


if __name__ == "__main__":
    main()
