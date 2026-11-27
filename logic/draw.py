"""Draw the schematics and the runway timing diagram into media/."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import schemdraw.logic as lg
import home

MEDIA = Path(__file__).resolve().parents[1] / "media"
schemdraw.config(fontsize=11, lw=1.3)


def gate():
    d = schemdraw.Drawing(show=False)
    xors = []
    for i, y in enumerate([0, -2.2, -4.4, -6.6]):
        b = 3 - i
        x = d.add(lg.Xor().at((2.5, y)).anchor("in1").right())
        d.add(elm.Line().at(x.in1).left(1.2))
        d.add(elm.Dot(open=True).label(f"P{b}", loc="left"))
        d.add(elm.Line().at(x.in2).left(1.2))
        d.add(elm.Dot(open=True).label(f"K{b}", loc="left"))
        xors.append(x)
    o1 = d.add(lg.Or().right().anchor("in1").at((xors[0].out[0] + 1.6, xors[0].out[1] - 0.9)))
    d.add(elm.Wire("-|").at(xors[0].out).to(o1.in1))
    d.add(elm.Wire("-|").at(xors[1].out).to(o1.in2))
    o2 = d.add(lg.Or().right().anchor("in1").at((xors[2].out[0] + 1.6, xors[2].out[1] - 0.9)))
    d.add(elm.Wire("-|").at(xors[2].out).to(o2.in1))
    d.add(elm.Wire("-|").at(xors[3].out).to(o2.in2))
    o3 = d.add(lg.Or().right().anchor("in1").at((o1.out[0] + 1.6, (o1.out[1] + o2.out[1]) / 2 + 0.5)))
    d.add(elm.Wire("-|").at(o1.out).to(o3.in1))
    d.add(elm.Wire("-|").at(o2.out).to(o3.in2))
    m = (o3.out[0] + 0.8, o3.out[1])
    d.add(elm.Line().at(o3.out).to(m))
    d.add(elm.Dot().at(m).label("mismatch", loc="top"))
    n = d.add(lg.Nor().right().anchor("in1").at((m[0] + 1.2, m[1] + 1.2)))
    d.add(elm.Wire("|-").at(m).to(n.in1))
    d.add(elm.Line().at(n.in1).to(n.in2) if False else elm.Wire("-|").at((n.in1[0] - 0.3, n.in1[1])).to(n.in2))
    d.add(elm.Line().at(n.out).right(0.6))
    d.add(elm.Resistor().right(1.4).label("220 Ω", loc="top"))
    d.add(elm.LED().right(1.2).label("green", loc="top"))
    d.add(elm.Line().right(0.3))
    d.add(elm.Ground())
    d.add(elm.Line().at(m).down(1.6))
    d.add(elm.Line().right(3.0))
    d.add(elm.Resistor().right(1.4).label("220 Ω", loc="top"))
    d.add(elm.LED().right(1.2).label("red", loc="top"))
    d.add(elm.Line().right(0.3))
    d.add(elm.Ground())
    d.add(elm.Label().at((6.0, -8.4)).label(
        "P3–P0: password on the hidden DIP switch (1101).  K3–K0: code on the 4 toggle switches.\n"
        "Every switch input has a 1 kΩ pull-down resistor to 0 V, so an open switch reads 0."))
    d.save(str(MEDIA / "sch_gate.svg"))


def parking():
    d = schemdraw.Drawing(show=False)
    for i, y in enumerate([0, -3.8, -7.6]):
        d.add(elm.Dot(open=True).at((0, y)).label("5 V", loc="left"))
        d.add(elm.Switch().right(1.6).label(f"S{i+1} (spot {i+1})", loc="top"))
        n = d.here
        d.add(elm.Dot())
        d.add(elm.Resistor().at(n).down(1.4).label("1 kΩ", loc="top"))
        d.add(elm.Ground())
        d.add(elm.Line().at(n).right(1.0))
        p = d.here
        d.add(elm.Dot())
        d.add(elm.Line().at(p).up(0.8))
        d.add(elm.Line().right(2.6))
        d.add(elm.Resistor().right(1.4).label("220 Ω", loc="top"))
        d.add(elm.LED().right(1.2).label("red", loc="top"))
        d.add(elm.Line().right(0.3))
        d.add(elm.Ground())
        d.add(elm.Line().at(p).down(0.6))
        inv = d.add(lg.Not().right().anchor("in1").at((p[0], p[1] - 0.6)))
        d.add(elm.Line().at(inv.out).right().tox(p[0] + 2.6))
        d.add(elm.Resistor().right(1.4).label("220 Ω", loc="bottom"))
        d.add(elm.LED().right(1.2).label("green", loc="bottom"))
        d.add(elm.Line().right(0.3))
        d.add(elm.Ground())
    d.add(elm.Label().at((4.0, -10.4)).label("Per spot: red = S (taken),  green = /S (free): one inverter of a 74LS04"))
    d.save(str(MEDIA / "sch_parking.svg"))


def runway():
    d = schemdraw.Drawing(show=False)
    names = ["Q0", "Q1", "Q2"]
    ffs = []
    for i in range(3):
        f = d.add(elm.Ic(pins=[elm.IcPin(name="D", side="left", slot="2/2"),
                               elm.IcPin(name=">", side="left", slot="1/2"),
                               elm.IcPin(name="Q", side="right", slot="2/2"),
                               elm.IcPin(name="Q̄", side="right", slot="1/2")],
                         size=(1.6, 2.0), label=f"FF{i}").at((5.6 * i + 3.4, 0)))
        ffs.append(f)
    ands = []
    for i, f in enumerate(ffs):
        a = d.add(lg.And(inputs=2).right().anchor("out").at((f.D[0] - 0.6, f.D[1])))
        d.add(elm.Line().at(a.out).to(f.D))
        ands.append(a)
    # inputs of the ANDs
    d.add(elm.Line().at(ands[0].in1).left(0.6))
    d.add(elm.Dot(open=True).label("A (gate open)", loc="left"))
    for i in (1, 2):
        q_prev = ffs[i - 1].Q
        d.add(elm.Wire("-|").at(q_prev).to((ands[i].in1[0] - 0.4, ands[i].in1[1])))
        d.add(elm.Line().at((ands[i].in1[0] - 0.4, ands[i].in1[1])).to(ands[i].in1))
    # /Q2 bus to every AND second input
    q2b = ffs[2].pins[3] if False else ffs[2].absanchors["Q̄"] if "Q̄" in ffs[2].absanchors else None
    yb = -2.6
    d.add(elm.Line().at(ffs[2].absanchors["Q̄"]).right(0.5))
    d.add(elm.Line().down().toy(yb))
    d.add(elm.Line().left().tox(ands[0].in2[0] - 0.3))
    for a in ands:
        d.add(elm.Line().at((a.in2[0] - 0.3, yb)).up().toy(a.in2[1]))
        d.add(elm.Line().right(0.3))
        d.add(elm.Dot().at((a.in2[0] - 0.3, yb)))
    d.add(elm.Label().at((ffs[2].absanchors["Q̄"][0] + 1.3, yb + 0.3)).label("/Q2", fontsize=10))
    # clock bus
    yc = -3.4
    d.add(elm.Dot(open=True).at((0.2, yc)).label("CLK (555, 0.72 Hz)", loc="left"))
    d.add(elm.Line().at((0.2, yc)).right().tox(ffs[2].absanchors[">"][0] - 0.3))
    for f in ffs:
        c = f.absanchors[">"]
        d.add(elm.Line().at((c[0] - 0.3, yc)).up().toy(c[1]))
        d.add(elm.Line().right(0.3))
        d.add(elm.Dot().at((c[0] - 0.3, yc)))
    for i, f in enumerate(ffs):
        q = f.Q
        d.add(elm.Line().at(q).up(1.4))
        d.add(elm.Label().at((q[0] + 0.15, q[1] + 1.9)).label(f"{names[i]} → 2 lamp LEDs", fontsize=9, halign="left"))
    d.add(elm.Label().at((8.0, -4.6)).label("3 D flip-flops (74LS74), 3 AND gates (74LS08).   D0 = A·/Q2    D1 = Q0·/Q2    D2 = Q1·/Q2   (lights fill 000 → 001 → 011 → 111, then restart)"))
    d.save(str(MEDIA / "sch_runway.svg"))


def timing():
    seq = home.runway_sequence(a=1, steps=12)
    t = list(range(len(seq)))
    fig, axs = plt.subplots(4, 1, figsize=(8, 3.6), sharex=True, dpi=150)
    clk = [i % 2 for i in range(2 * len(seq))]
    axs[0].step([x / 2 for x in range(len(clk))], clk, where="post", color="#6a6f7a")
    axs[0].set_ylabel("CLK", rotation=0, ha="right", va="center")
    for k, ax in enumerate(axs[1:]):
        ax.step(t, [q[2 - k] for q in seq], where="post", lw=2, color=["#2f6db0", "#2f8f6b", "#c08a1e"][k])
        ax.set_ylabel(f"Q{k}", rotation=0, ha="right", va="center")
    for ax in axs:
        ax.set_yticks([]); ax.set_ylim(-0.2, 1.3)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
    axs[-1].set_xlabel("clock ticks (1 tick ≈ 1.4 s)")
    axs[0].set_title("Runway lights with the gate open: 1, 2, 3 pairs lit, then restart", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(MEDIA / "runway_timing.png", bbox_inches="tight")


def to_png():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(device_scale_factor=2)
        for f in sorted(MEDIA.glob("sch_*.svg")):
            pg.goto(f.resolve().as_uri())
            pg.query_selector("svg").screenshot(path=str(f.with_suffix(".png")))
        b.close()


if __name__ == "__main__":
    gate(); parking(); runway(); timing(); to_png()
    print("done")
