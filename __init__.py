# __init__.py  ── ComfyUI‑NIK‑Nodes

# ── imports ──────────────────────────────────────────────────────────
from .FrameSelector import FrameSelector
from .ImageAdjustments import ImageAdjustments
from .ImagePicker import ImagePicker
from .SubtitleNode import SubtitleNode
from .FPSMagic import FPSMagic
from .VideoPicker import VideoPicker

# ── registry ─────────────────────────────────────────────────────────
NODE_CLASS_MAPPINGS = {
    "FrameSelector":         FrameSelector,
    "ImageAdjustments":      ImageAdjustments,
    "ImagePicker":           ImagePicker,
    "SubtitleNode":          SubtitleNode,
    "FPSMagic":              FPSMagic,
    "VideoPicker":           VideoPicker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameSelector":        "🎞️ Frame Selector (Target FPS)",
    "ImageAdjustments":     "🧪 Image Adjustments",
    "ImagePicker":          "🧪 Image Picker",
    "SubtitleNode":         "🧪 Caption Generator",
    "FPSMagic":             "🧪 FPS Magic",
    "VideoPicker":          "🧪 Video Picker",
}

__all__ = list(NODE_CLASS_MAPPINGS.keys())

# ---- banner ----
print(
    "\033[92m" + r"""
███╗   ██╗   ██╗  ██╗  ██╗
████╗  ██║   ██║  ██║ ██╔╝
██╔██╗ ██║   ██║  █████╔╝
██║╚██╗██║   ╚═╝  ██╔═██╗
██║ ╚████║   ██╗  ██║  ██╗
╚═╝  ╚═══╝   ╚═╝  ╚═╝  ╚═╝

         N ! K  NODES  LOADED  ✅
""" + "\033[0m"
)
