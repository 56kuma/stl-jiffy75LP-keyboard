"""Export stand + simple keyboard-half proxies for the three.js preview."""
import math, sys
from pathlib import Path
import trimesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import stand as st


def keyboard(width, y_mouth):
    """Keyboard-half proxy (case 11mm + keycaps) standing in a slot."""
    case = trimesh.creation.box((width, 11.0, st.KB_DEPTH))
    caps = trimesh.creation.box((width - 6, 9.0, st.KB_DEPTH - 6))
    caps.apply_translation((0, -10.0, 0))
    kb = trimesh.util.concatenate([case, caps])
    kb.apply_translation((0, st.SLOT_W / 2 - 6.0, st.KB_DEPTH / 2))
    kb.apply_translation((0, 0, -st.SLOT_DEPTH / math.cos(st.LEAN) + 2.2))
    kb.apply_transform(trimesh.transformations.rotation_matrix(-st.LEAN, (1, 0, 0)))
    kb.apply_translation((0, y_mouth, st.H))
    return kb


if __name__ == "__main__":
    here = Path(__file__).parent
    g = st.SLOT_W * 2 + st.DIVIDER
    keyboard(st.KB_LEFT_W, -g / 2 + st.SLOT_W / 2).export(here / "kbl.stl")
    keyboard(st.KB_RIGHT_W, g / 2 - st.SLOT_W / 2).export(here / "kbr.stl")
    st.build().export(here / "stand.stl")
    print("exported")
