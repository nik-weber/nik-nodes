import os
import re
import numpy as np
from PIL import Image, ImageOps
import torch

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

class ImagePicker:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": ""}),
                "image_number": ("INT", {"default": 1, "min": 1}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "filename")
    FUNCTION = "pick_image"
    CATEGORY = "N!K Nodes"

    def pick_image(self, directory_path, image_number, unique_id=None, extra_pnginfo=None):
        if not directory_path or not os.path.exists(directory_path):
            raise ValueError("Directory not found")

        supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
        files = [f for f in os.listdir(directory_path)
                 if os.path.splitext(f)[1].lower() in supported_formats]

        if not files:
            raise ValueError("No images found in directory")

        files = sorted(files, key=natural_sort_key)

        total_files = len(files)
        current_index = (image_number - 1) % total_files
        image_path = os.path.join(directory_path, files[current_index])

        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
        image = image.convert('RGB')
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)
        image = image.unsqueeze(0)

        filename = os.path.splitext(files[current_index])[0]
        return (image, filename)

    @classmethod
    def IS_CHANGED(cls, image_number, **kwargs):
        return image_number

# Registro para o ComfyUI
NODE_CLASS_MAPPINGS = {
    "ImagePicker": ImagePicker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePicker": "🧪 Image Picker"
}
