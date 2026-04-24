"""
Phase 3 Visualizations: Error quantification and comparison plots
Steps 3.2a.7, 3.3.1–3.3.4
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

FIGURES = Path("outputs/figures")
FIGURES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (12, 6),
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def plot_wq_comparison():
    """
    Step 3.3.4: Visualize Wq comparison across models and arrival processes.
    """
    # Data from Phase 3 simulation output (see phase3_simulation.py logs).
    # Keep values synchronised with main.tex Table 2 and appendix Table B.4.
    systems = {
        "BB Kendall T\n(M/M/c, c=23)": {
            "Analytical\n(Poisson)": 0.82,
            "DES\nExponential": 1.42,
            "DES\nEmpirical": 9.35,
            "DES\nWeibull": 10.56,
        },
        "MBTA North\n(M/M/1)": {
            "Analytical\n(Poisson)": 20.05,
            "DES\nExponential": 20.49,
            "DES\nEmpirical": 4.22,
            "DES\nLog-normal": 4.35,
        },
        "MBTA South\n(M/M/1)": {
            "Analytical\n(Poisson)": 10.74,
            "DES\nExponential": 10.91,
            "DES\nEmpirical": 0.93,
            "DES\nLog-normal": 1.03,
        },
    }

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    colors = {
        "Analytical\n(Poisson)": "#d62728",
        "DES\nExponential": "#ff7f0e",
        "DES\nEmpirical": "#2ca02c",
        "DES\nWeibull": "#1f77b4",
        "DES\nLog-normal": "#1f77b4",
    }

    for ax, (sys_name, data) in zip(axes, systems.items()):
        labels = list(data.keys())
        values = list(data.values())
        bar_colors = [colors.get(l, "gray") for l in labels]

        bars = ax.bar(range(len(labels)), values, color=bar_colors, edgecolor="white", width=0.7)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Avg Wait Time Wq (seconds)")
        ax.set_title(sys_name)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f"{val:.1f}s", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Average Wait Time (Wq): Poisson vs Reality",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(FIGURES / "phase3_wq_comparison.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase3_wq_comparison.png'}")
    plt.close()


def plot_blocking_comparison():
    """
    Blocking probability comparison: Erlang B vs DES vs Observed.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = [
        "Erlang B\n(analytical)",
        "DES\nExponential",
        "DES\nEmpirical",
        "DES\nWeibull",
        "Observed\nFullness Rate",
    ]
    kendall = [0.068, 0.098, 0.543, 0.462, 3.735]

    x = np.arange(len(categories))
    bars = ax.bar(x, kendall, color=["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4", "#7f7f7f"],
                  edgecolor="white", width=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("Blocking / Fullness Rate (%)")
    ax.set_title("Kendall T (c=23): Predicted vs Observed Blocking Probability",
                 fontsize=13, fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 20)

    for bar, val in zip(bars, kendall):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.2,
                f"{val:.2f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.axhline(y=3.735, color="#7f7f7f", linestyle="--", alpha=0.5, linewidth=1)
    ax.text(4.4, 4.5, "Observed: 3.73%", fontsize=9, color="#7f7f7f")

    fig.tight_layout()
    fig.savefig(FIGURES / "phase3_blocking_comparison.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase3_blocking_comparison.png'}")
    plt.close()


def plot_error_summary():
    """
    Step 3.3.3–3.3.4: Relative error summary table as a figure.
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis("off")

    headers = ["System", "Model", "Metric", "Poisson\nPrediction", "Empirical\nDES", "Relative\nError", "Direction"]
    rows = [
        ["BB Kendall T", "M/M/c", "Wq (sec)", "0.8", "9.4", "−91%", "Underestimates"],
        ["BB Kendall T", "M/M/c", "W (min)", "122.8", "123.0", "−0.2%", "≈ Correct"],
        ["BB Kendall T", "M/M/c/c", "Block %", "0.07%", "0.54%", "−87%", "Underestimates"],
        ["BB Kendall T", "M/M/c/c", "vs Observed", "0.07%", "3.73%*", "−98%", "Underestimates"],
        ["BB MIT Vassar", "M/M/c/c", "vs Observed", "≈0%", "2.88%*", "−100%", "Underestimates"],
        ["MBTA North", "M/M/1", "Wq (sec)", "20.1", "4.2", "+376%", "Overestimates"],
        ["MBTA North", "M/M/1", "W (sec)", "98.8", "83.0", "+19%", "Overestimates"],
        ["MBTA South", "M/M/1", "Wq (sec)", "10.7", "0.9", "+1,050%", "Overestimates"],
        ["MBTA South", "M/M/1", "W (sec)", "69.5", "59.8", "+16%", "Overestimates"],
    ]

    table = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.5)

    # Color header
    for j in range(len(headers)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Color error column
    for i in range(1, len(rows) + 1):
        err = rows[i-1][5]
        direction = rows[i-1][6]
        if "Underestimates" in direction:
            table[i, 5].set_facecolor("#FFC7CE")
            table[i, 6].set_facecolor("#FFC7CE")
        elif "Overestimates" in direction:
            table[i, 5].set_facecolor("#C6EFCE")
            table[i, 6].set_facecolor("#C6EFCE")

    ax.set_title("Poisson Assumption Error Summary\n* Observed fullness rate (not from DES)",
                 fontsize=13, fontweight="bold", pad=20)
    fig.tight_layout()
    fig.savefig(FIGURES / "phase3_error_summary.png", dpi=150, bbox_inches="tight")
    print(f"  Saved: {FIGURES / 'phase3_error_summary.png'}")
    plt.close()


if __name__ == "__main__":
    print("Generating Phase 3 visualizations...")
    plot_wq_comparison()
    plot_blocking_comparison()
    plot_error_summary()
    print("\nDone.")
