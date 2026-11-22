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

      post │ plate (keycaps float) │ groove (case + feet zone) │ plate │ post
           │_______________________│        spine+post         │_______│
                                   │___________||______________│

  The case backs have 5 mm feet near both ends of the standing edge. The case
  backs are held 5.25 mm from the centre so the feet pass each other, and the
  spine rail / centre posts stay clear of the last ~32 mm at the +y end
  (the -y end keeps the spine rail up to the end stop).

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
KB_DEPTH = 128.0      # mm  front-back depth (measured 128 mm; this edge sits on the stand)
KB_CASE = 10.5        # mm  case edge thickness (measured ~10 mm)
KB_CAPS = 9.0         # mm  keycap overhang beyond the case (measured ~8-9 mm)
KB_CAP_LIFT = 4.0     # mm  keycaps start this far above the standing edge
FOOT_H = 5.0          # mm  foot block protrusion from the case back (measured)
FOOT_L = 20.0         # mm  foot length along the standing edge (measured 5 x 20)
FOOT_W = 5.0          # mm  foot size perpendicular to the standing edge
FOOT_CLR = 0.5        # mm  clearance between the two halves' feet (centre)

# ---------------------------------------------------------------- stand
# Modelled with x = across (left/right), y = along keyboard depth, z = up.
L = S(1)              # 141.4  plate length          L : W = 2 = sqrt(2)^2
W = S(3)              # 70.7   plate width
H = S(9)              # 8.84   plate thickness
CORNER_C = S(9)       # 8.84   corner chamfer (octagonal plate)
EDGE_C = S(14)        # 1.56   small chamfer on plate top / bottom edges

CASE_GAP = 0.75       # mm     centre post face -> case back
CASE_W = S(8)         # 12.5   groove width for the case edge
GROOVE_D = S(12)      # 3.125  groove depth (< KB_CAP_LIFT so keycaps float)
CAP_GAP = 1.0         # mm     keycap face -> outer post
CH_L = KB_DEPTH + 1.0  # 129.0 groove length = inner length between the end stops

RAIL_H = S(10)        # 6.25   rail height above plate
RAIL_T = S(11)        # 4.42   end-stop thickness
RAIL_R = S(14)        # 1.56   rail top round-over

POST_TOP = S(3)       # 70.7   post height from desk (= plate width)
POST_Y = S(6)         # 25     post position along y (+/-); spacing = 50 = S(4)
POST_BASE_H = S(7)    # 17.7   height of the wider pedestal part
OUT_T0, OUT_T1 = S(10), S(12)   # 6.25 -> 3.125  outer post thickness (x)
OUT_D = S(10)                   # 6.25           outer post depth (y)
TAPER = S(10) - S(11)           # 1.83           post taper (silver-ladder step)
CEN_D = S(8)                    # 12.5           centre post depth (y)
PED = S(14)                     # 1.56           pedestal step

FOOT_D = S(8)         # 12.5   rubber-foot recess diameter
FOOT_DEPTH = 1.0

SEG_CORNER = 24

# derived
# Case backs sit FOOT_H + FOOT_CLR/2 from the centre, so the feet near both
# ends of the standing edge pass each other freely (feet act as spacers).
X_BACK = FOOT_H + FOOT_CLR / 2                       # 5.25  case back
FIN_T = 2 * (X_BACK - CASE_GAP)                      # 9.0   spine / centre post
CEN_T0, CEN_T1 = FIN_T, FIN_T - TAPER                # 9.0 -> 7.17
X_CASE_OUT = X_BACK + KB_CASE + (CASE_W - KB_CASE - CASE_GAP)   # groove outer edge
X_POST_IN = X_BACK + KB_CASE + KB_CAPS + CAP_GAP     # 25.75 outer post face
CH_W = X_POST_IN - FIN_T / 2                # compatibility (channel width)
CH_DEPTH = GROOVE_D                         # compatibility (floor = H - CH_DEPTH)
SPINE_Y = POST_Y + CEN_D / 2 + PED          # spine rail ends at the centre posts
FEET_ZONE = CH_L / 2 - SPINE_Y               # free length at the feet end
SPINE_FULL_END = -1   # this end (-y / +y) keeps the spine rail up to the end stop;
                      # the other end stays open for the feet

assert CASE_W > KB_CASE + 1
assert GROOVE_D < KB_CAP_LIFT, "keycaps would hit the plate"
assert X_POST_IN > X_CASE_OUT
assert FEET_ZONE >= FOOT_L + 5, "not enough room for the feet at the ends"
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
    zs, rings = [H - GROOVE_D - 0.5, H + RAIL_H - RAIL_R], []
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
    z0 = H - GROOVE_D - 0.5
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
    """One wide groove: both case edges + the feet zone between them."""
    g = loft([rect(-X_CASE_OUT, X_CASE_OUT, -CH_L / 2, CH_L / 2)] * 2,
             [H - GROOVE_D, H + 1])
    return [g]


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
    ya, yb = sorted((SPINE_FULL_END * (CH_L / 2 + 0.1), -SPINE_FULL_END * SPINE_Y))
    adds = [rail(-FIN_T / 2, FIN_T / 2, ya, yb)]
    for s in (-1, 1):                              # end stops
        y0, y1 = sorted((s * CH_L / 2, s * (CH_L / 2 + RAIL_T)))
        adds.append(rail(-X_POST_IN, X_POST_IN, y0, y1))
    for y in (-POST_Y, POST_Y):
        adds.append(post(0, 1, CEN_T0, CEN_T1, CEN_D, y, False))
        for s in (-1, 1):
            adds.append(post(s * X_POST_IN, s, OUT_T0, OUT_T1, OUT_D, y, True))
    return trimesh.boolean.union([base] + adds, engine="manifold")


FIT_FLOOR = 1.2       # mm  floor kept under the groove in the fit test
FIT_ABOVE = 8.0       # mm  post height kept above the plate (keycaps start at +0.9)
FIT_RIM = 1.5         # mm  material kept around the lightening windows


def build_fit_test():
    """Light, fast fit-check print of one end of the stand:
    end stop + feet zone + one row of posts.
      - only the functional height is kept (posts cut FIT_ABOVE above the plate)
      - the bottom is removed, leaving FIT_FLOOR under the groove
      - windows are cut where nothing touches the keyboard
    """
    full = build()
    y0, y1 = POST_Y - CEN_D / 2 - PED - 2, L / 2 + 1
    z0 = H - GROOVE_D - FIT_FLOOR
    z1 = H + FIT_ABOVE
    box = trimesh.creation.box((W + 10, y1 - y0, z1 - z0))
    box.apply_translation((0, (y0 + y1) / 2, (z0 + z1) / 2))
    t = trimesh.boolean.intersection([full, box], engine="manifold")

    # lightening windows (through the whole remaining thickness)
    yw0 = POST_Y + max(OUT_D, CEN_D) / 2 + PED + FIT_RIM     # past the posts
    yw1 = CH_L / 2 - FIT_RIM                                  # before end stop
    wins = []
    for sx in (-1, 1):   # plate under the floating keycaps
        xa, xb = X_CASE_OUT + FIT_RIM, X_POST_IN - FIT_RIM
        wins.append((sx * (xa + xb) / 2, xb - xa))
    xc = X_BACK - FIT_RIM                                     # feet zone (centre)
    wins.append((0.0, 2 * xc))
    for cx, wx in wins:
        w = trimesh.creation.box((wx, yw1 - yw0, 100))
        w.apply_translation((cx, (yw0 + yw1) / 2, 0))
        t = trimesh.boolean.difference([t, w], engine="manifold")

    t.apply_translation((0, -(y0 + y1) / 2, -z0))
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
    print(f"case back x=±{X_BACK:.2f}, centre post {CEN_T0:.2f}->{CEN_T1:.2f}, "
          f"spine rail y=±{SPINE_Y:.2f}, feet zone {FEET_ZONE:.1f} mm/end, "
          f"groove x=±{X_CASE_OUT:.2f}")
    print(f"groove {CASE_W:.2f} x {GROOVE_D:.3f} deep, outer post inner face "
          f"x=±{X_POST_IN:.3f}, posts at y=±{POST_Y:.1f}")
