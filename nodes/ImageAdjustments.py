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
    CATEGORY = "NIK/NIK"

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
        # Converter imagens em escala de cinza para RGB
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Ajustes de brilho e saturação
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        v = np.clip(v * brightness, 0, 255).astype(np.uint8)
        s = np.clip(s * saturation, 0, 255).astype(np.uint8)
        hsv_image = cv2.merge([h, s, v])
        adjusted_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        # Contraste
        adjusted_image = cv2.convertScaleAbs(adjusted_image, alpha=contrast, beta=0)

        # Nitidez
        if sharpness > 1.0:
            kernel = np.array([[0, -1, 0], [-1, 5 * sharpness, -1], [0, -1, 0]])
            adjusted_image = cv2.filter2D(adjusted_image, -1, kernel)

        # HDR (correção de gama)
        if hdr > 0.0:
            gamma = 1.0 - hdr
            look_up_table = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
            adjusted_image = cv2.LUT(adjusted_image, look_up_table)

        # Grão
        if grain > 0.0:
            noise = np.random.normal(0, grain * 255, adjusted_image.shape).astype(np.uint8)
            adjusted_image = cv2.addWeighted(adjusted_image, 1.0, noise, grain, 0)

        # Bloom
        if bloom > 0.0:
            blurred = cv2.GaussianBlur(adjusted_image, (0, 0), bloom * 10)
            adjusted_image = cv2.addWeighted(adjusted_image, 1.0, blurred, bloom, 0)

        return {"image": adjusted_image}

# Registro para o ComfyUI
NODE_CLASS_MAPPINGS = {
    "ImageAdjustments": ImageAdjustments,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageAdjustments": "🧪 Image Adjustments",
}
