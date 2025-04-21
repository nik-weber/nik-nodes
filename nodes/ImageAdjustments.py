import cv2
import numpy as np
from typing import Any, Dict

class ImageAdjustments:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "brightness": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0}),
                "contrast": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0}),
                "saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0}),
                "sharpness": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0}),
                "hdr": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0}),
                "grain": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0}),
                "bloom": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "adjust_image"

    CATEGORY = "Image/Adjustments"

    def adjust_image(
        self,
        image: np.ndarray,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        sharpness: float = 1.0,
        hdr: float = 0.0,
        grain: float = 0.0,
        bloom: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Adjust image properties: brightness, contrast, saturation, sharpness, etc.
        """

        # Converter imagens em escala de cinza para RGB
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Convert to HSV for brightness and saturation adjustments
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)

        # Adjust brightness
        v = np.clip(v * brightness, 0, 255).astype(np.uint8)

        # Adjust saturation
        s = np.clip(s * saturation, 0, 255).astype(np.uint8)

        # Merge adjusted channels and convert back to BGR
        hsv_image = cv2.merge([h, s, v])
        adjusted_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        # Adjust contrast
        adjusted_image = cv2.convertScaleAbs(adjusted_image, alpha=contrast, beta=0)

        # Adjust sharpness
        if sharpness > 1.0:
            kernel = np.array([[0, -1, 0], [-1, 5 * sharpness, -1], [0, -1, 0]])
            adjusted_image = cv2.filter2D(adjusted_image, -1, kernel)

        # Add HDR effect (simple gamma correction)
        if hdr > 0.0:
            gamma = 1.0 - hdr
            look_up_table = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
            adjusted_image = cv2.LUT(adjusted_image, look_up_table)

        # Add grain effect
        if grain > 0.0:
            noise = np.random.normal(0, grain * 255, adjusted_image.shape).astype(np.uint8)
            adjusted_image = cv2.addWeighted(adjusted_image, 1.0, noise, grain, 0)

        # Add bloom effect
        if bloom > 0.0:
            blurred = cv2.GaussianBlur(adjusted_image, (0, 0), bloom * 10)
            adjusted_image = cv2.addWeighted(adjusted_image, 1.0, blurred, bloom, 0)

        return {"image": adjusted_image}


NODE_CLASS_MAPPINGS = {
    "ImageAdjustments": ImageAdjustments,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageAdjustments": "Image Adjustments",
}
