class FrameSelector:
    """
    A ComfyUI custom node that selects a specific number of frames from an interpolated image sequence
    to match a target FPS, without changing the duration of the original video.
    Ensures exact duration matching by repeating the last frame if needed.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "original_fps": ("INT", {"default": 24, "min": 1, "max": 240}),
                "target_fps": ("INT", {"default": 30, "min": 1, "max": 240}),
                "interpolation_multiplier": ("INT", {"default": 5, "min": 1, "max": 20})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("selected_images",)
    FUNCTION = "select_frames"
    CATEGORY = "NIK/NIK"

    def select_frames(self, images, original_fps, target_fps, interpolation_multiplier):
        total_frames = len(images)

        # Precise duration based on interpolated frame count
        duration = total_frames / (original_fps * interpolation_multiplier)

        # Exact number of frames required for output duration at target FPS
        exact_frame_count = duration * target_fps
        final_frame_count = round(exact_frame_count)

        # Compute step size to sample evenly across original frames
        step = total_frames / exact_frame_count

        # Generate frame indices ensuring we end with the exact last frame
        indices = [round(i * step) for i in range(final_frame_count - 1)]
        indices.append(total_frames - 1)  # Force exact last frame match

        # Clamp values to be within bounds
        indices = [min(i, total_frames - 1) for i in indices]

        # Select frames
        selected_images = [images[i] for i in indices]
        return (selected_images,)

NODE_CLASS_MAPPINGS = {
    "FrameSelector": FrameSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameSelector": "🎞️ Frame Selector (Target FPS)"
}
