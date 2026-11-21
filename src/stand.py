"""
Jiffy75 (LP) split keyboard — back-to-back vertical stand ("Silver Rack").

Both halves stand on their SHORT edge (127.7 mm side down), case bottoms
facing each other, keycaps facing outward.

Structure (rack style):
  - thin plate with chamfered (octagonal) corners
  - low rails: one central spine rib + two end stops
  - shallow grooves beside the spine: only the ~10 mm case edge sits in them,
    the keycaps float above the plate top
  - six slim posts: two on the spine (case backs lean on them) and two on each
    outer side (1 mm away from the keycap faces); tapered with gable tips

      post │ plate (keycaps float) │ groove │ spine+post │ groove │ plate │ post
           │_______________________│        │    ||      │        │_______│
                                   │________│    ||      │________│

Design rule: Silver ratio (白銀比 / 大和比, 1 : sqrt(2)).
Major dimensions come from the ladder  S(k) = 200 / sqrt(2)^k :
    k : 1      2    3     4    5     6    7     8     9     10   11    12
    mm: 141.4  100  70.7  50   35.4  25   17.7  12.5  8.84  6.25 4.42  3.125

Usage:  python3 src/stand.py   ->  stl/jiffy75_stand.stl (+ fit test)
"""
import math
from pathlib import Path

import numpy as np
import trimesh

R2 = math.sqrt(2.0)


def S(k: float) -> float:
    """Silver-ratio ladder."""
    return 200.0 / R2 ** k


# ---------------------------------------------------------------- keyboard
KB_LEFT_W = 156.4     # mm  left half width  (becomes height when stood up)
KB_RIGHT_W = 176.1    # mm  right half width (becomes height when stood up)
KB_DEPTH = 127.7      # mm  front-back depth (this edge sits on the stand)
KB_CASE = 10.5        # mm  case edge thickness (measured ~10 mm)
KB_CAPS = 9.0         # mm  keycap overhang beyond the case (measured ~8-9 mm)
KB_CAP_LIFT = 4.0     # mm  keycaps start this far above the standing edge

# ---------------------------------------------------------------- stand
# Modelled with x = across (left/right), y = along keyboard depth, z = up.
L = S(1)              # 141.4  plate length          L : W = 2 = sqrt(2)^2
W = S(3)              # 70.7   plate width
H = S(9)              # 8.84   plate thickness
CORNER_C = S(9)       # 8.84   corner chamfer (octagonal plate)
EDGE_C = S(14)        # 1.56   small chamfer on plate top / bottom edges

FIN_T = S(10)         # 6.25   spine thickness
CASE_GAP = 0.75       # mm     spine face -> case back
CASE_W = S(8)         # 12.5   groove width for the case edge
GROOVE_D = S(12)      # 3.125  groove depth (< KB_CAP_LIFT so keycaps float)
CAP_GAP = 1.0         # mm     keycap face -> outer post
CH_L = KB_DEPTH + 3.5  # 131.2 inner length between the end stops

RAIL_H = S(10)        # 6.25   rail height above plate
RAIL_T = S(11)        # 4.42   end-stop thickness
RAIL_R = S(14)        # 1.56   rail top round-over

POST_TOP = S(3)       # 70.7   post height from desk (= plate width)
POST_Y = S(5)         # 35.4   post position along y (+/-); spacing = 70.7 = W
POST_BASE_H = S(7)    # 17.7   height of the wider pedestal part
OUT_T0, OUT_T1 = S(10), S(12)   # 6.25 -> 3.125  outer post thickness (x)
OUT_D = S(10)                   # 6.25           outer post depth (y)
CEN_T0, CEN_T1 = S(10), S(11)   # 6.25 -> 4.42   centre post thickness (x)
CEN_D = S(8)                    # 12.5           centre post depth (y)
PED = S(14)                     # 1.56           pedestal step

FOOT_D = S(8)         # 12.5   rubber-foot recess diameter
FOOT_DEPTH = 1.0

SEG_CORNER = 24

# derived
X_CASE_IN = FIN_T / 2                       # groove inner edge
X_CASE_OUT = FIN_T / 2 + CASE_W             # groove outer edge
X_POST_IN = FIN_T / 2 + CASE_GAP + KB_CASE + KB_CAPS + CAP_GAP   # 24.375
CH_W = X_POST_IN - FIN_T / 2                # compatibility (channel width)
CH_DEPTH = GROOVE_D                         # compatibility (floor = H - CH_DEPTH)

assert CASE_W > KB_CASE + 1
assert GROOVE_D < KB_CAP_LIFT, "keycaps would hit the plate"
assert X_POST_IN > X_CASE_OUT
assert X_POST_IN + OUT_T0 + PED < W / 2, "outer posts overhang the plate"
assert CH_L / 2 + RAIL_T < L / 2


# ---------------------------------------------------------------- helpers
def squircle_rect(hx, hy, r, n=4.0, seg=SEG_CORNER):
    """Rounded rectangle whose corners are superellipse quadrants
    (continuous-curvature, 'Apple style'). Fixed point count -> loftable."""
    r = max(r, 1e-3)
    pts = []
    centers = [(hx - r, hy - r, 0), (-hx + r, hy - r, 1),
               (-hx + r, -hy + r, 2), (hx - r, -hy + r, 3)]
    for cx, cy, q in centers:
        for i in range(seg):
            t = (q + i / (seg - 1)) * math.pi / 2
            c, s = math.cos(t), math.sin(t)
            x = cx + r * math.copysign(abs(c) ** (2 / n), c)
            y = cy + r * math.copysign(abs(s) ** (2 / n), s)
            pts.append((x, y))
    return np.array(pts)


def stadium(hl, hw, seg=SEG_CORNER):
    """Stadium (slot) outline: half-length hl, half-width hw."""
    pts = []
    for cx, a0 in ((hl - hw, -math.pi / 2), (-hl + hw, math.pi / 2)):
        for i in range(seg):
            t = a0 + math.pi * i / (seg - 1)
            pts.append((cx + hw * math.cos(t), hw * math.sin(t)))
    return np.array(pts)


def loft(rings, zs):
    """Watertight solid lofted through closed rings (same point count)."""
    n = len(rings[0])
    verts, faces = [], []
    for ring, z in zip(rings, zs):
        verts += [(x, y, z) for x, y in ring]
    for k in range(len(rings) - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            faces += [(a + i, a + j, b + j), (a + i, b + j, b + i)]
    # caps (fan from centroid)
    for k, flip in ((0, True), (len(rings) - 1, False)):
        c = len(verts)
        cx, cy = rings[k].mean(axis=0)
        verts.append((cx, cy, zs[k]))
        base = k * n
        for i in range(n):
            j = (i + 1) % n
            f = (c, base + i, base + j)
            faces.append(f[::-1] if flip else f)
    m = trimesh.Trimesh(np.array(verts), np.array(faces), process=True)
    m.fix_normals()
    return m


def octagon(hx, hy, c):
    """Rectangle with 45° chamfered corners (8 points, loftable)."""
    return np.array([(hx, -hy + c), (hx, hy - c), (hx - c, hy), (-hx + c, hy),
                     (-hx, hy - c), (-hx, -hy + c), (-hx + c, -hy), (hx - c, -hy)])


def rect(x0, x1, y0, y1):
    return np.array([(x1, y0), (x1, y1), (x0, y1), (x0, y0)])


# ---------------------------------------------------------------- parts
def plate():
    k = math.sqrt(2) - 1           # chamfer shrink per unit inset
    zs, rings = [], []
    for z, d in ((0, EDGE_C), (EDGE_C, 0), (H - EDGE_C, 0), (H, EDGE_C)):
        zs.append(z)
        rings.append(octagon(W / 2 - d, L / 2 - d, CORNER_C - d * k))
    return loft(rings, zs)


def rail(x0, x1, y0, y1):
    """Low rail with rounded top edges (squircle section)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    r = min(hx, hy) * 0.999
    zs, rings = [H - 0.5, H + RAIL_H - RAIL_R], []
    rings += [squircle_rect(hx, hy, r) + (cx, cy)] * 2
    for i in range(1, 7):
        a = (math.pi / 2) * i / 6
        d = min(RAIL_R * (1 - math.cos(a)), r * 0.95)
        zs.append(H + RAIL_H - RAIL_R + RAIL_R * math.sin(a))
        rings.append(squircle_rect(hx - d, hy - d, r - d) + (cx, cy))
    return loft(rings, zs)


def post(x_in, side, t0, t1, d, y, keep_inner_face):
    """Tapered post with a pedestal and a gable (ridge) tip.
    x_in : x of the face that touches the keyboard (or centre if symmetric)."""
    z0 = H - 0.5
    tip = d / 2                                   # 45° gable

    def ring(t, dd, ped=0.0):
        if keep_inner_face:                       # outer post: flat inner face
            xa, xb = x_in, x_in + side * (t + ped)
        else:                                     # centre post: symmetric
            xa, xb = -(t / 2), t / 2
        x0, x1 = min(xa, xb), max(xa, xb)
        return rect(x0, x1, y - dd / 2 - ped, y + dd / 2 + ped)

    t_ped = t0 + (t1 - t0) * (POST_BASE_H - H) / (POST_TOP - tip - H)
    zs = [z0, POST_BASE_H, POST_BASE_H, POST_TOP - tip, POST_TOP]
    rings = [ring(t0, d, PED), ring(t_ped, d, PED), ring(t_ped, d),
             ring(t1, d), ring(t1, 0.6)]
    return loft(rings, zs)


def grooves():
    cuts = []
    for s in (-1, 1):
        x0, x1 = sorted((s * (X_CASE_IN - 0.01), s * X_CASE_OUT))
        g = loft([rect(x0, x1, -CH_L / 2, CH_L / 2)] * 2, [H - GROOVE_D, H + 1])
        cuts.append(g)
    return cuts


def feet():
    cs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl = trimesh.creation.cylinder(radius=FOOT_D / 2,
                                            height=FOOT_DEPTH * 2, sections=64)
            cyl.apply_translation((sx * (W / 2 - S(8)), sy * (L / 2 - S(7)), 0))
            cs.append(cyl)
    return cs


def build():
    base = trimesh.boolean.difference([plate()] + grooves() + feet(),
                                      engine="manifold")
    adds = [rail(-FIN_T / 2, FIN_T / 2, -CH_L / 2 - 0.1, CH_L / 2 + 0.1)]
    for s in (-1, 1):                              # end stops
        y0, y1 = sorted((s * CH_L / 2, s * (CH_L / 2 + RAIL_T)))
        adds.append(rail(-X_POST_IN, X_POST_IN, y0, y1))
    for y in (-POST_Y, POST_Y):
        adds.append(post(0, 1, CEN_T0, CEN_T1, CEN_D, y, False))
        for s in (-1, 1):
            adds.append(post(s * X_POST_IN, s, OUT_T0, OUT_T1, OUT_D, y, True))
    return trimesh.boolean.union([base] + adds, engine="manifold")


def build_fit_test(length=S(6), height=S(5)):
    """Short slice through one row of posts for a quick fit-check print."""
    full = build()
    box = trimesh.creation.box((W + 10, length, height))
    box.apply_translation((0, POST_Y, height / 2 - 1))
    t = trimesh.boolean.intersection([full, box], engine="manifold")
    t.apply_translation((0, -POST_Y, 0))
    return t


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "stl"
    out.mkdir(exist_ok=True)
    m = build()
    p = out / "jiffy75_stand.stl"
    m.export(p)
    ext = m.bounds[1] - m.bounds[0]
    print(f"wrote {p}")
    print(f"watertight={m.is_watertight}  volume={m.volume/1000:.1f} cm3")
    print(f"size = {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm")
    t = build_fit_test()
    t.export(out / "jiffy75_stand_fit_test.stl")
    print(f"fit test watertight={t.is_watertight} "
          f"size={' x '.join(f'{v:.1f}' for v in t.bounds[1]-t.bounds[0])}")
    print(f"groove {CASE_W:.2f} x {GROOVE_D:.3f} deep, outer post inner face "
          f"x=±{X_POST_IN:.3f}, posts at y=±{POST_Y:.1f}")
