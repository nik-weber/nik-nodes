from typing import List, Tuple
import math

class FPSMagic:
    """
    Resamples a list of image frames from source_fps to target_fps while keeping
    perceived duration. Optionally force the duration (seconds).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "source_fps": ("INT",   {"default": 24, "min": 1, "max": 240}),
                "target_fps": ("INT",   {"default": 30, "min": 1, "max": 240}),
                "duration":   ("FLOAT", {"default": 0.0, "min": 0.0,
                                         "step": 0.001, "precision": 3}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "video_info")
    FUNCTION     = "convert_fps"
    CATEGORY     = "NIK/NIK"

    def convert_fps(self,
                    images: List,
                    source_fps: int,
                    target_fps: int,
                    duration: float = 0.0
                    ) -> Tuple[List, str]:

        in_frames = len(images)
        dur = duration if duration > 0.0 else in_frames / source_fps

        # required frame count to keep duration
        out_frames_exact = dur * target_fps
        out_frames = max(1, round(out_frames_exact))
        step = in_frames / out_frames_exact

        idxs = [min(round(i * step), in_frames - 1) for i in range(out_frames)]
        images_out = [images[i] for i in idxs]

        info = (f"{source_fps}→{target_fps} fps | "
                f"{in_frames}→{len(images_out)} frames | "
                f"{dur:.3f}s")

        return images_out, info
