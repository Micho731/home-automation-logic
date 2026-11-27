import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "logic"))
import home  # noqa: E402

BITS4 = list(itertools.product((0, 1), repeat=4))


def test_gate_all_256_combinations():
    for p in BITS4:
        for k in BITS4:
            g, r = home.gate(p, k)
            assert g == int(p == k)          # green only for the right code
            assert r == 1 - g                # red otherwise, never both


def test_gate_default_password():
    opens = [k for k in BITS4 if home.gate(home.PASSWORD, k)[0]]
    assert opens == [home.PASSWORD]          # exactly one of 16 codes opens it


def test_runway_fills_and_repeats():
    seq = home.runway_sequence(a=1, steps=8)
    assert seq[:5] == [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1), (0, 0, 0)]
    assert seq[4:8] == seq[0:4]              # period of 4 clock ticks


def test_runway_unused_states_recover():
    for q in itertools.product((0, 1), repeat=3):
        seq = home.runway_sequence(start=q, a=1, steps=3)
        assert (0, 0, 0) in seq              # every state reaches the cycle within 3 ticks


def test_runway_switch_off_turns_lights_off():
    seq = home.runway_sequence(start=(1, 1, 1), a=0, steps=3)
    assert seq[-1] == (0, 0, 0)


def test_555_timing():
    c = home.clock_555()
    assert abs(c["f_hz"] - 0.716) < 0.01     # about one step every 1.4 s
    assert 0.5 < c["duty"] < 0.51


def test_parking_all_combinations():
    for s in itertools.product((0, 1), repeat=3):
        red, green = home.parking(s)
        assert red == s
        assert all(r + g == 1 for r, g in zip(red, green))   # exactly one LED per spot
