"""Export stand + simple keyboard-half proxies for the three.js preview."""
import sys
from pathlib import Path
import trimesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import stand as st


def keyboard(height, side, depth=st.KB_DEPTH):
    """Half standing on its short edge; case back to the spine, keycaps outward.
    side = -1 (left channel) / +1 (right channel)."""
    floor = st.H - st.CH_DEPTH
    x_case = side * (st.FIN_T / 2 + st.CASE_GAP + st.KB_CASE / 2)
    case = trimesh.creation.box((st.KB_CASE, depth, height))
    case.apply_translation((x_case, 0, floor + height / 2))
    cap_h = height - 2 * st.KB_CAP_LIFT
    caps = trimesh.creation.box((st.KB_CAPS, depth - 6, cap_h))
    caps.apply_translation((x_case + side * (st.KB_CASE + st.KB_CAPS) / 2, 0,
                            floor + st.KB_CAP_LIFT + cap_h / 2))
    parts = [case, caps]
    if depth >= st.KB_DEPTH:                      # feet near both ends
        for sy in (-1, 1):
            f = trimesh.creation.box((st.FOOT_H, st.FOOT_L, st.FOOT_W))
            f.apply_translation((side * (st.X_BACK - st.FOOT_H / 2),
                                 sy * (depth / 2 - st.FOOT_L / 2 - 2),
                                 floor + 1 + st.FOOT_W / 2))
            parts.append(f)
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    here = Path(__file__).parent
    keyboard(st.KB_LEFT_W, -1).export(here / "kbl.stl")
    keyboard(st.KB_RIGHT_W, +1).export(here / "kbr.stl")
    st.build().export(here / "stand.stl")
    st.build_fit_test().export(here / "fit.stl")
    keyboard(12, -1).export(here / "kbl_low.stl")   # short proxies: top view
    keyboard(12, +1).export(here / "kbr_low.stl")
    keyboard(60, -1, st.S(6) - 4).export(here / "kbl_cut.stl")
    keyboard(60, +1, st.S(6) - 4).export(here / "kbr_cut.stl")
    print("exported")
