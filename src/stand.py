"""
Jiffy75 (LP) split keyboard vertical stand generator.

Design rule: Silver ratio (白銀比 / 大和比, 1 : sqrt(2)).
Every major dimension is taken from the ladder  S(k) = 200 / sqrt(2)^k :
    k : 0     1      2    3     4    5     6    7     8     9     10
    mm: 200  141.4  100  70.7  50   35.4  25   17.7  12.5  8.84  6.25 ...
The slot lean angle is also silver-derived: atan(1 / (4*sqrt(2))) ≈ 10.0°.

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
KB_LEFT_W = 156.4     # mm  (left half width)
KB_RIGHT_W = 176.1    # mm  (right half width)
KB_DEPTH = 127.7      # mm  (front-back; becomes height when stood up)
KB_THICK_MAX = 23.0   # mm  (case + keycaps)

# ---------------------------------------------------------------- stand
W = S(0)              # 200   overall width
D = S(2)              # 100   overall depth          W:D = 2 = sqrt(2)^2
H = S(6)              # 25    overall height         D:H = 4 = sqrt(2)^4
CORNER_R = S(7)       # 17.7  plan corner radius (squircle)
TOP_FILLET = S(10)    # 6.25  top edge round-over
BOTTOM_CHAMFER = S(13)  # 2.21  45° shadow-line chamfer (floating look)

SLOT_W = S(6)         # 25    slot width  (> KB_THICK_MAX + clearance)
SLOT_DEPTH = S(7)     # 17.7  vertical slot depth
SLOT_END_MARGIN = S(9)  # 8.84 margin at slot ends
SLOT_L = W - 2 * SLOT_END_MARGIN   # 182.3 (> 176.1 + clearance)
DIVIDER = S(8)        # 12.5  wall between the two slots
SLOT_CHAMFER = S(14)  # 1.56  lead-in chamfer at slot mouth
LEAN = math.atan(1.0 / (4 * R2))   # ≈10.02°

FOOT_D = S(8)         # 12.5  rubber-foot recess diameter
FOOT_DEPTH = 1.0
FOOT_INSET = S(7)     # 17.7

SEG_CORNER = 24       # points per corner
assert SLOT_L > KB_RIGHT_W + 4
assert SLOT_W > KB_THICK_MAX + 1


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


# ---------------------------------------------------------------- body
def body():
    zs, rings = [], []
    # bottom 45° chamfer
    for i in range(5):
        z = BOTTOM_CHAMFER * i / 4
        d = BOTTOM_CHAMFER - z
        zs.append(z)
        rings.append(squircle_rect(W / 2 - d, D / 2 - d, CORNER_R - d))
    # vertical wall then top round-over
    z0 = H - TOP_FILLET
    for i in range(0, 17):
        a = (math.pi / 2) * i / 16
        z = z0 + TOP_FILLET * math.sin(a)
        d = TOP_FILLET * (1 - math.cos(a))
        if i == 16:
            d = min(d, CORNER_R * 0.9)
        zs.append(z)
        rings.append(squircle_rect(W / 2 - d, D / 2 - d, CORNER_R - d))
    return loft(rings, zs)


def slot_cutter(y_center):
    """Leaning stadium slot with lead-in chamfer, mouth centred at y_center."""
    ext = 2.0                       # poke out above top
    depth_axis = SLOT_DEPTH / math.cos(LEAN)
    zs, rings = [], []
    # local frame: z along slot axis, 0 = bottom, top = depth_axis+ext
    zs.append(0.0)
    rings.append(stadium(SLOT_L / 2, SLOT_W / 2))
    zc = depth_axis - SLOT_CHAMFER
    zs.append(zc)
    rings.append(stadium(SLOT_L / 2, SLOT_W / 2))
    for i in range(1, 5):
        t = i / 4
        z = zc + (SLOT_CHAMFER + ext) * t
        g = (SLOT_CHAMFER + ext) * t
        zs.append(z)
        rings.append(stadium(SLOT_L / 2 + g, SLOT_W / 2 + g))
    c = loft(rings, zs)
    # put the mouth centre (z = depth_axis) at origin, lean back about X
    c.apply_translation((0, 0, -depth_axis))
    rot = trimesh.transformations.rotation_matrix(-LEAN, (1, 0, 0))
    c.apply_transform(rot)
    c.apply_translation((0, y_center, H))
    return c


def feet():
    cs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl = trimesh.creation.cylinder(radius=FOOT_D / 2,
                                            height=FOOT_DEPTH * 2, sections=64)
            cyl.apply_translation((sx * (W / 2 - FOOT_INSET),
                                   sy * (D / 2 - FOOT_INSET), 0))
            cs.append(cyl)
    return cs


def build():
    # slot mouths centred as a group in depth (y: -front .. +back)
    group = SLOT_W * 2 + DIVIDER
    y_front = -group / 2 + SLOT_W / 2
    y_back = group / 2 - SLOT_W / 2
    solid = body()
    cutters = [slot_cutter(y_front), slot_cutter(y_back)] + feet()
    result = trimesh.boolean.difference([solid] + cutters, engine="manifold")
    return result


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
    print(f"slot L={SLOT_L:.1f} W={SLOT_W:.1f} depth={SLOT_DEPTH:.1f} "
          f"lean={math.degrees(LEAN):.2f} deg")
