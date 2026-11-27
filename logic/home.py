"""Reference model of the three home-automation circuits.

Each function mirrors the gate-level design in the README, so the tests can check
every input combination and the runway light sequence.
"""
from __future__ import annotations

PASSWORD = (1, 1, 0, 1)          # set on the hidden DIP switch (P3 P2 P1 P0)


# ---------------------------------------------------------------- gate (code lock)
def gate(p: tuple[int, int, int, int], k: tuple[int, int, int, int]) -> tuple[int, int]:
    """4-bit comparator. p = password on the DIP switch, k = code on the 4 toggle switches.
    Each XOR is 1 where a bit differs; the three ORs combine them into 'mismatch';
    a NOR used as an inverter gives 'match'.  Returns (green, red)."""
    diff = [pi ^ ki for pi, ki in zip(p, k)]
    mismatch = (diff[0] | diff[1]) | (diff[2] | diff[3])
    green = int(not (mismatch | mismatch))           # NOR with both inputs tied together
    red = mismatch
    return green, red


# ---------------------------------------------------------------- runway lights
def runway_next(q: tuple[int, int, int], a: int) -> tuple[int, int, int]:
    """Next state of the 3 D flip-flops (Q2 Q1 Q0).
    While the gate is open (A = 1) the lights fill 000 -> 001 -> 011 -> 111 and start again.
        D0 = A . /Q2      D1 = Q0 . /Q2      D2 = Q1 . /Q2
    """
    q2, q1, q0 = q
    nq2 = 1 - q2
    return (q1 & nq2, q0 & nq2, a & nq2)


def runway_sequence(start=(0, 0, 0), a=1, steps=8):
    seq, q = [start], start
    for _ in range(steps):
        q = runway_next(q, a)
        seq.append(q)
    return seq


def clock_555(ra: float = 1e3, rb: float = 100e3, c: float = 10e-6) -> dict:
    """555 astable: f = 1.44 / ((RA + 2 RB) C), high time 0.693 (RA + RB) C, low time 0.693 RB C."""
    th = 0.693 * (ra + rb) * c
    tl = 0.693 * rb * c
    return {"f_hz": 1.44 / ((ra + 2 * rb) * c), "t_high_s": th, "t_low_s": tl,
            "period_s": th + tl, "duty": th / (th + tl)}


# ---------------------------------------------------------------- parking spots
def parking(occupied: tuple[int, int, int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Each spot: red = occupied (R = S), green = free (G = /S, one inverter)."""
    red = tuple(occupied)
    green = tuple(1 - s for s in occupied)
    return red, green
