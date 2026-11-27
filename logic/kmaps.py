"""Draw the Karnaugh maps of the runway and parking logic into media/.

Every cell is computed from the logic model in home.py (the same functions the
tests check), and the outlined group is the product term used in the circuit.

    python logic/kmaps.py
"""
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from home import parking, runway_next  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "media"
GRAY2 = [(0, 0), (0, 1), (1, 1), (1, 0)]
INK, MUTED, GRID = "#1f2328", "#59636e", "#8c959f"
GROUP = "#2a6fdb"


def draw_kmap(ax, title, row_names, col_names, rows, cols, value, group, equation):
    """rows / cols: lists of variable tuples in Gray order; value(r, c) -> 0/1;
    group: (row_start, row_end, col_start, col_end), inclusive, contiguous."""
    nr, nc = len(rows), len(cols)
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            v = value(r, c)
            ax.add_patch(plt.Rectangle((j, nr - 1 - i), 1, 1, fill=False, ec=GRID, lw=1))
            ax.text(j + 0.5, nr - 1 - i + 0.5, str(v), ha="center", va="center",
                    fontsize=15, color=INK if v else "#9aa3ad", weight="bold" if v else "normal")
    for j, c in enumerate(cols):
        ax.text(j + 0.5, nr + 0.25, "".join(map(str, c)), ha="center", va="center", fontsize=11, color=MUTED)
    for i, r in enumerate(rows):
        ax.text(-0.3, nr - 1 - i + 0.5, "".join(map(str, r)), ha="center", va="center", fontsize=11, color=MUTED)
    ax.text(-0.3, nr + 0.25, f"{row_names} \\ {col_names}", ha="right", va="center", fontsize=10, color=MUTED)
    r0, r1, c0, c1 = group
    ax.add_patch(FancyBboxPatch((c0 + 0.1, nr - 1 - r1 + 0.1), c1 - c0 + 0.8, r1 - r0 + 0.8,
                                boxstyle="round,pad=0,rounding_size=0.25", fill=False, ec=GROUP, lw=2.5))
    ax.text(-1.6, nr + 0.95, title, ha="left", va="center", fontsize=13, color=INK)
    ax.text(nc / 2, -0.45, equation, ha="center", va="center", fontsize=14, color=GROUP, weight="bold")
    ax.set_xlim(-1.6, nc + 0.1)
    ax.set_ylim(-0.8, nr + 1.25)
    ax.set_aspect("equal")
    ax.axis("off")


def runway_kmaps():
    rows = GRAY2                       # Q2 A
    cols = GRAY2                       # Q1 Q0
    def nxt(r, c, k):
        (q2, a), (q1, q0) = r, c
        return runway_next((q2, q1, q0), a)[k]     # returns (D2, D1, D0)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), facecolor="white")
    draw_kmap(axes[0], "D0 (pair 1)", "Q2 A", "Q1 Q0", rows, cols, lambda r, c: nxt(r, c, 2),
              (1, 1, 0, 3), "D0 = A · Q̄2")
    draw_kmap(axes[1], "D1 (pair 2)", "Q2 A", "Q1 Q0", rows, cols, lambda r, c: nxt(r, c, 1),
              (0, 1, 1, 2), "D1 = Q0 · Q̄2")
    draw_kmap(axes[2], "D2 (pair 3)", "Q2 A", "Q1 Q0", rows, cols, lambda r, c: nxt(r, c, 0),
              (0, 1, 2, 3), "D2 = Q1 · Q̄2")
    fig.tight_layout()
    fig.savefig(OUT / "kmaps_runway.png", dpi=150, facecolor="white")
    plt.close(fig)


def parking_kmaps():
    rows = [(0,), (1,)]                # S1
    cols = GRAY2                       # S2 S3
    def out(r, c, kind):
        s = (r[0], c[0], c[1])
        red, green = parking(s)
        return (red if kind == "R" else green)[0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.0), facecolor="white")
    draw_kmap(axes[0], "R1 (spot 1 red)", "S1", "S2 S3", rows, cols, lambda r, c: out(r, c, "R"),
              (1, 1, 0, 3), "R1 = S1")
    draw_kmap(axes[1], "G1 (spot 1 green)", "S1", "S2 S3", rows, cols, lambda r, c: out(r, c, "G"),
              (0, 0, 0, 3), "G1 = S̄1")
    fig.tight_layout()
    fig.savefig(OUT / "kmaps_parking.png", dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    runway_kmaps()
    parking_kmaps()
    print("K-maps written to", OUT)
