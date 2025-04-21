class FrameSelector:
    """
    A ComfyUI custom node that selects a specific number of frames from an interpolated image sequence
    to match a target FPS, without changing the duration of the original video.
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
    CATEGORY = "NIK/video"

    def select_frames(self, images, original_fps, target_fps, interpolation_multiplier):
        total_frames = len(images)

        # Calculate original duration
        duration_seconds = total_frames / (original_fps * interpolation_multiplier)

        # Calculate number of frames needed for final video
        final_frame_count = int(duration_seconds * target_fps)

        # Sample evenly across the interpolated frames
        step = total_frames / final_frame_count
        selected_indices = [round(i * step) for i in range(final_frame_count)]
        selected_indices = [min(i, total_frames - 1) for i in selected_indices]  # prevent out of bounds

        selected_images = [images[i] for i in selected_indices]
        return (selected_images,)

NODE_CLASS_MAPPINGS = {
    "FrameSelector": FrameSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameSelector": "🎞️ Frame Selector (Target FPS)"
}
