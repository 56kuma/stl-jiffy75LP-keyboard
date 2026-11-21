"""Export stand + simple keyboard-half proxies for the three.js preview."""
import sys
from pathlib import Path
import trimesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import stand as st


def keyboard(height, side):
    """Half standing on its short edge; case back to the spine, keycaps outward.
    side = -1 (left channel) / +1 (right channel)."""
    floor = st.H - st.CH_DEPTH
    x_case = side * (st.FIN_T / 2 + 0.5 + st.KB_CASE / 2)
    case = trimesh.creation.box((st.KB_CASE, st.KB_DEPTH, height))
    case.apply_translation((x_case, 0, floor + height / 2))
    caps = trimesh.creation.box((9.0, st.KB_DEPTH - 6, height - 6))
    caps.apply_translation((x_case + side * (st.KB_CASE / 2 + 4.5), 0,
                            floor + height / 2))
    return trimesh.util.concatenate([case, caps])


if __name__ == "__main__":
    here = Path(__file__).parent
    keyboard(st.KB_LEFT_W, -1).export(here / "kbl.stl")
    keyboard(st.KB_RIGHT_W, +1).export(here / "kbr.stl")
    st.build().export(here / "stand.stl")
    print("exported")
