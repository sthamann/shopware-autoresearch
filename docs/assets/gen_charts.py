#!/usr/bin/env python3
"""Generate all result charts for RESEARCH_RESULTS as PNGs.

Reproducible: re-run after new waves to refresh figures.
    python3 docs/assets/gen_charts.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

OUT = Path(__file__).resolve().parent

# ---- Palette ---------------------------------------------------------------
INK = "#12233A"        # dark navy
BLUE = "#189EFF"       # Shopware blue
GREEN = "#17B26A"      # verified
RED = "#F04438"        # failed
AMBER = "#F79009"      # planned
SLATE = "#64748B"      # neutral
GRID = "#E4E9F0"
BG = "#FFFFFF"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "font.size": 12,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "axes.edgecolor": GRID,
    "axes.linewidth": 1.0,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 1.0,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.25,
})


def _no_top_right(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save(fig, name):
    path = OUT / name
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    print(f"wrote {path}")


# ---------------------------------------------------------------------------
# 1. Performance landscape — horizontal bars, p95 @ 100k
# ---------------------------------------------------------------------------
def performance_landscape():
    data = [
        ("Admin Grid (query-only)", 71, GREEN),
        ("Store API Product List", 96, GREEN),
        ("Category Listing", 186, GREEN),
        ("Home /  (deferred)", 199, GREEN),
        ("Listing CMS (deferred)", 200, GREEN),
        ("Admin Search (standard)", 316, AMBER),
        ("Widget async load", 1598, RED),
    ]
    data.sort(key=lambda d: d[1])
    labels = [d[0] for d in data]
    vals = [d[1] for d in data]
    colors = [d[2] for d in data]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(labels, vals, color=colors, height=0.62, zorder=3)
    ax.set_xlim(0, 1750)
    ax.set_xlabel("p95 latency (ms) — lower is better")
    ax.set_title("Performance Landscape @ 100,000 products",
                 fontsize=15, fontweight="bold", pad=14, loc="left")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + 18, bar.get_y() + bar.get_height() / 2,
                f"{v} ms", va="center", ha="left", fontweight="bold", fontsize=11)
    ax.axvline(500, color=SLATE, ls="--", lw=1.2, zorder=2)
    ax.text(505, 6.3, "500 ms target", color=SLATE, fontsize=10, style="italic")
    _no_top_right(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    save(fig, "01-performance-landscape.png")


# ---------------------------------------------------------------------------
# 2. Before / after — dramatic drops (log scale)
# ---------------------------------------------------------------------------
def before_after():
    items = [
        ("Home  /", 3199, 199),
        ("Listing CMS", 1681, 200),
        ("Admin search", 316, 71),
    ]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = range(len(items))
    w = 0.36
    before = [i[1] for i in items]
    after = [i[2] for i in items]
    b1 = ax.bar([i - w / 2 for i in x], before, width=w, color=RED, label="before", zorder=3)
    b2 = ax.bar([i + w / 2 for i in x], after, width=w, color=GREEN, label="after", zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(30, 5000)
    ax.set_xticks(list(x))
    ax.set_xticklabels([i[0] for i in items], fontweight="bold")
    ax.set_ylabel("p95 latency (ms, log)")
    ax.set_title("Before / After — the three biggest breakthroughs",
                 fontsize=15, fontweight="bold", pad=14, loc="left")
    for bar, v in zip(b1, before):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.05, f"{v}", ha="center",
                va="bottom", fontsize=10, color=RED, fontweight="bold")
    for bar, v in zip(b2, after):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.05, f"{v}", ha="center",
                va="bottom", fontsize=10, color=GREEN, fontweight="bold")
    for i, (label, bef, aft) in enumerate(items):
        pct = round((1 - aft / bef) * 100)
        ax.annotate(f"\u2212{pct}%", xy=(i, aft * 0.55), ha="center",
                    fontsize=13, fontweight="bold", color=INK)
    ax.legend(frameon=False, loc="upper right")
    _no_top_right(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    save(fig, "02-before-after.png")


# ---------------------------------------------------------------------------
# 3. Wave results — stacked bars (verified / failed)
# ---------------------------------------------------------------------------
def wave_results():
    waves = ["Boot", "W1", "W2", "W3", "W4", "W5", "W6"]
    verified = [4, 1, 0, 1, 3, 2, 1]
    failed = [0, 5, 4, 3, 2, 2, 2]
    fig, ax = plt.subplots(figsize=(10, 5.0))
    x = range(len(waves))
    b1 = ax.bar(x, verified, color=GREEN, label="Verified", zorder=3)
    b2 = ax.bar(x, failed, bottom=verified, color=RED, label="Failed", zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(waves, fontweight="bold")
    ax.set_ylabel("Number of claims")
    ax.set_title("Results per optimization wave",
                 fontsize=15, fontweight="bold", pad=14, loc="left")
    for i in x:
        if verified[i]:
            ax.text(i, verified[i] / 2, str(verified[i]), ha="center", va="center",
                    color="white", fontweight="bold")
        if failed[i]:
            ax.text(i, verified[i] + failed[i] / 2, str(failed[i]), ha="center",
                    va="center", color="white", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    _no_top_right(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    save(fig, "03-wave-results.png")


# ---------------------------------------------------------------------------
# 4. Overall status donut
# ---------------------------------------------------------------------------
def status_donut():
    sizes = [12, 18, 3]
    labels = ["Verified\n12", "Failed\n18", "Planned\n3"]
    colors = [GREEN, RED, AMBER]
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.42, edgecolor=BG, linewidth=3))
    ax.text(0, 0.15, "33", ha="center", va="center", fontsize=34, fontweight="bold", color=INK)
    ax.text(0, -0.22, "total claims", ha="center", va="center", fontsize=12, color=SLATE)
    for w, lab, col in zip(wedges, labels, colors):
        ang = (w.theta2 + w.theta1) / 2
        import math
        xx = 1.15 * math.cos(math.radians(ang))
        yy = 1.15 * math.sin(math.radians(ang))
        ax.text(xx, yy, lab, ha="center", va="center", fontsize=12,
                fontweight="bold", color=col)
    ax.set_title("Claim status (ground truth: registry.csv)",
                 fontsize=15, fontweight="bold", pad=6)
    save(fig, "04-status-donut.png")


# ---------------------------------------------------------------------------
# 5. Claims per strand — stacked horizontal
# ---------------------------------------------------------------------------
def per_strand():
    strands = ["Infra", "Strand 2\nAPI", "Strand 1\nRequest", "Strand 3\nScale"]
    verified = [1, 1, 4, 6]
    failed = [0, 3, 8, 6]
    planned = [0, 0, 2, 1]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    b1 = ax.barh(strands, verified, color=GREEN, label="Verified", zorder=3)
    b2 = ax.barh(strands, failed, left=verified, color=RED, label="Failed", zorder=3)
    left2 = [v + f for v, f in zip(verified, failed)]
    b3 = ax.barh(strands, planned, left=left2, color=AMBER, label="Planned", zorder=3)
    for i, s in enumerate(strands):
        if verified[i]:
            ax.text(verified[i] / 2, i, verified[i], ha="center", va="center",
                    color="white", fontweight="bold")
        if failed[i]:
            ax.text(verified[i] + failed[i] / 2, i, failed[i], ha="center", va="center",
                    color="white", fontweight="bold")
        if planned[i]:
            ax.text(left2[i] + planned[i] / 2, i, planned[i], ha="center", va="center",
                    color="white", fontweight="bold")
    ax.set_xlabel("Number of claims")
    ax.set_title("Claims per research strand",
                 fontsize=15, fontweight="bold", pad=14, loc="left")
    ax.legend(frameon=False, loc="lower right", ncol=3)
    _no_top_right(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    save(fig, "05-per-strand.png")


# ---------------------------------------------------------------------------
# 6. Cumulative verified over waves (area)
# ---------------------------------------------------------------------------
def cumulative():
    waves = ["Boot", "W1", "W2", "W3", "W4", "W5", "W6"]
    ver = [4, 1, 0, 1, 3, 2, 1]
    cum = []
    t = 0
    for v in ver:
        t += v
        cum.append(t)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = range(len(waves))
    ax.fill_between(x, cum, color=BLUE, alpha=0.18, zorder=2)
    ax.plot(x, cum, color=BLUE, lw=3, marker="o", markersize=8,
            markerfacecolor="white", markeredgewidth=2.5, markeredgecolor=BLUE, zorder=3)
    for i, v in zip(x, cum):
        ax.text(i, v + 0.5, str(v), ha="center", fontweight="bold", color=BLUE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(waves, fontweight="bold")
    ax.set_ylabel("Verified claims (cumulative)")
    ax.set_ylim(0, 15)
    ax.set_title("Cumulative verified wins across waves",
                 fontsize=15, fontweight="bold", pad=14, loc="left")
    _no_top_right(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    save(fig, "06-cumulative.png")


if __name__ == "__main__":
    performance_landscape()
    before_after()
    wave_results()
    status_donut()
    per_strand()
    cumulative()
    print("all charts done")
