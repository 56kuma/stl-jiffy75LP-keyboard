"""
Jiffy75 (LP) split keyboard — back-to-back vertical stand ("Silver Spine").

Both halves stand on their SHORT edge (127.7 mm side down), case bottoms
facing each other, keycaps facing outward. A thin central blade (spine)
separates the two cases.

Stepped channel (fits the real cross-section of the board):
  - only the ~10 mm case edge touches the floor  -> narrow, deep CASE slot
  - keycaps overhang ~8-9 mm and float a few mm above the edge
                                                   -> raised, shallow CAP shelf

      outer wall | cap shelf | case slot | spine | case slot | cap shelf | wall
                 |___________|           |  ||   |           |___________|
                             |___________|  ||   |___________|

Design rule: Silver ratio (白銀比 / 大和比, 1 : sqrt(2)).
Every major dimension is taken from the ladder  S(k) = 200 / sqrt(2)^k :
    k : 0     1      2    3     4    5     6    7     8     9     10   11
    mm: 200  141.4  100  70.7  50   35.4  25   17.7  12.5  8.84  6.25 4.42

Usage:  python3 src/stand.py   ->  stl/jiffy75_stand.stl
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
# x: across (left/right), y: along the keyboard depth, z: up
L = S(1)              # 141.4  base length       L : W = 2 = sqrt(2)^2
W = S(3)              # 70.7   base width
H = S(7)              # 17.7   base height
CORNER_R = S(8)       # 12.5   plan corner radius (squircle)
TOP_FILLET = S(11)    # 4.42   top edge round-over
BOTTOM_CHAMFER = S(13)  # 2.21  45° shadow-line chamfer (floating look)

CASE_W = S(8)         # 12.5   case slot width   (> KB_CASE + clearance)
CASE_GAP = 0.75       # mm     spine face -> case back (case resting on the spine)
CAP_GAP = 1.0         # mm     keycap face -> outer wall
CAP_W = CASE_GAP + KB_CASE + KB_CAPS + CAP_GAP - CASE_W   # 8.75 keycap shelf width
CH_L = KB_DEPTH + 3.5  # 131.2  channel length (keyboard + clearance)
CH_DEPTH = S(8)       # 12.5   case slot depth (from top surface)
CAP_STEP = S(12)      # 3.125  shelf raised above the slot floor (< KB_CAP_LIFT)
CH_R = S(12)          # 3.125  channel corner radius
CH_CHAMFER = S(14)    # 1.56   lead-in chamfer at channel mouth

FIN_T = S(10)         # 6.25   spine thickness
FIN_L = S(2)          # 100    spine length          FIN_L : L = 1 : sqrt(2)
FIN_TOP = S(3)        # 70.7   spine top height from desk (= base width W)

FOOT_D = S(8)         # 12.5   rubber-foot recess diameter
FOOT_DEPTH = 1.0
FOOT_INSET = S(7)     # 17.7 / 12.5 (x uses smaller inset)

SEG_CORNER = 24
CH_W = CASE_W + CAP_W  # 21.25 total channel width per side
assert CASE_W > KB_CASE + 1
assert CAP_W > 0
assert CAP_STEP < KB_CAP_LIFT, "keycaps would hit the shelf"
assert 2 * CH_W + FIN_T < W - 2 * 6, "side walls too thin"
assert CH_L < L - 2 * 4, "end walls too thin"


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


# ---------------------------------------------------------------- parts
def body():
    zs, rings = [], []
    for i in range(5):                       # bottom 45° chamfer
        z = BOTTOM_CHAMFER * i / 4
        d = BOTTOM_CHAMFER - z
        zs.append(z)
        rings.append(squircle_rect(L / 2 - d, W / 2 - d, CORNER_R - d))
    z0 = H - TOP_FILLET
    for i in range(17):                      # wall + top round-over
        a = (math.pi / 2) * i / 16
        zs.append(z0 + TOP_FILLET * math.sin(a))
        d = TOP_FILLET * (1 - math.cos(a))
        rings.append(squircle_rect(L / 2 - d, W / 2 - d, CORNER_R - d))
    return loft(rings, zs)


def _cutter(hx, hy, z_floor, chamfer=True):
    """Squircle-rect cutter from z_floor up through the top (+ lead-in)."""
    ext = 2.0
    if not chamfer:
        return loft([squircle_rect(hx, hy, CH_R)] * 2, [z_floor, H + ext])
    zs = [z_floor, H - CH_CHAMFER]
    rings = [squircle_rect(hx, hy, CH_R), squircle_rect(hx, hy, CH_R)]
    for i in range(1, 5):
        g = (CH_CHAMFER + ext) * i / 4
        zs.append(H - CH_CHAMFER + g)
        rings.append(squircle_rect(hx + g, hy + g, CH_R + g))
    return loft(rings, zs)


def pocket():
    """Shallow shelf pocket spanning everything + two deep, narrow case slots.
    (Modelled with length along x, width along y; the spine is added later.)"""
    z_slot = H - CH_DEPTH
    shelf = _cutter(CH_L / 2, FIN_T / 2 + CH_W, z_slot + CAP_STEP)
    cuts = [shelf]
    for sy in (-1, 1):
        slot = _cutter(CH_L / 2, (FIN_T + CASE_W) / 2, z_slot, chamfer=False)
        slot.apply_translation((0, sy * (CASE_W / 2), 0))
        cuts.append(slot)
    return trimesh.boolean.union(cuts, engine="manifold")


def spine():
    """Thin blade with a fully rounded top and stadium-shaped plan."""
    hl, hw = FIN_L / 2, FIN_T / 2
    z_start = H - CH_DEPTH - 0.5               # overlap with floor
    z_round = FIN_TOP - hw
    zs = [z_start, z_round]
    rings = [stadium(hl, hw), stadium(hl, hw)]
    for i in range(1, 13):
        a = (math.pi / 2) * i / 12
        d = hw * (1 - math.cos(a))
        d = min(d, hw * 0.97)
        zs.append(z_round + hw * math.sin(a))
        rings.append(stadium(hl - d, hw - d))
    return loft(rings, zs)


def feet():
    cs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl = trimesh.creation.cylinder(radius=FOOT_D / 2,
                                            height=FOOT_DEPTH * 2, sections=64)
            cyl.apply_translation((sx * (L / 2 - S(7)), sy * (W / 2 - S(8)), 0))
            cs.append(cyl)
    return cs


def _rot_to_xy(m):
    """Parts are modelled with length along x; rotate so length runs along y."""
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, (0, 0, 1)))
    return m


def build():
    base = trimesh.boolean.difference([body(), pocket()] + feet(), engine="manifold")
    result = trimesh.boolean.union([base, spine()], engine="manifold")
    return _rot_to_xy(result)


def build_fit_test(length=S(6), height=S(5)):
    """Short slice of the full profile for a quick fit-check print."""
    full = build()
    box = trimesh.creation.box((W + 10, length, height))
    box.apply_translation((0, 0, height / 2 - 1))
    return trimesh.boolean.intersection([full, box], engine="manifold")


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
    print(f"case slot {CASE_W:.1f} (depth {CH_DEPTH:.1f}), cap shelf {CAP_W:.1f} "
          f"(+{CAP_STEP:.2f} step), length {CH_L:.1f}, "
          f"spine t={FIN_T:.2f} L={FIN_L:.1f} top={FIN_TOP:.1f}, "
          f"side wall={(W - 2*CH_W - FIN_T)/2:.2f}, end wall={(L-CH_L)/2:.2f}")
