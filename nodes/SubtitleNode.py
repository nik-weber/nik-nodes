import sys
import os
import math
import copy
import torch
import numpy as np
import tempfile
import wave
import re
from PIL import Image, ImageDraw, ImageFont

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kwargs: x

try:
    import whisper
    from moviepy import AudioFileClip
except ModuleNotFoundError as e:
    raise e

class SubtitleNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_frames": ("IMAGE", {"forcePin": True}),
                "audio": ("AUDIO", {"forcePin": True})
            },
            "optional": {
                "fps": ("INT", {"default": 30, "min": 1, "max": 240, "step": 1, "forcePin": False}),
                "font_path": ("STRING", {"default": "C:/Windows/Fonts/BebasNeue-Regular.ttf", "forcePin": False}),
                "font_size": ("INT", {"default": 100, "min": 10, "max": 400, "forcePin": False}),
                "font_color": ("STRING", {"default": "#FFFFFF", "forcePin": False}),
                "stroke_color": ("STRING", {"default": "#000000", "forcePin": False}),
                "stroke_width": ("INT", {"default": 4, "min": 0, "max": 20, "forcePin": False}),
                "y_pos_percent": ("INT", {"default": 50, "min": 0, "max": 100, "forcePin": False}),
                "text_case": (["uppercase", "lowercase", "normal"], {"forcePin": False})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_subtitles"
    CATEGORY = "N!K Nodes"

    def generate_subtitles(
        self,
        video_frames,
        audio,
        fps=30,
        font_path="C:/Windows/Fonts/Arial.ttf",
        font_size=60,
        font_color="#FFFFFF",
        stroke_color="#000000",
        stroke_width=2,
        y_pos_percent=50,
        text_case="normal"
    ):
        audio_path = self.resolve_audio(audio)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)
        words = []
        for seg in result.get("segments", []):
            for w in seg.get("words", []):
                txt = w["word"].strip()
                if txt:
                    words.append({"word": txt, "start": w["start"], "end": w["end"]})
        if not words:
            torch.cuda.empty_cache()
            return (video_frames,)
        if isinstance(video_frames, dict) and "samples" in video_frames:
            out_frames = copy.deepcopy(video_frames)
            frames_tensor = out_frames["samples"]
        else:
            out_frames = copy.deepcopy(video_frames)
            frames_tensor = out_frames
        sample_frame = frames_tensor[0]
        if sample_frame.dim() != 3:
            torch.cuda.empty_cache()
            return (out_frames,)
        if sample_frame.shape[0] == 3:
            mode = "CHW"
        elif sample_frame.shape[-1] == 3:
            mode = "HWC"
        else:
            torch.cuda.empty_cache()
            return (out_frames,)
        num_frames = frames_tensor.shape[0]
        for i in tqdm(range(num_frames)):
            t = i / fps
            active_words = [w["word"] for w in words if w["start"] <= t < w["end"]]
            if not active_words:
                continue
            line = " ".join(active_words)
            line = re.sub(r"[^\w\s]", "", line)
            if text_case == "uppercase":
                line = line.upper()
            elif text_case == "lowercase":
                line = line.lower()
            if mode == "CHW":
                pil_img = self.tensor_to_pil_CHW(frames_tensor[i])
                pil_img = self.draw_subtitle(pil_img, line, font_path, font_size, font_color, stroke_color, stroke_width, y_pos_percent)
                frames_tensor[i] = self.pil_to_tensor_CHW(pil_img)
            else:
                pil_img = self.tensor_to_pil_HWC(frames_tensor[i])
                pil_img = self.draw_subtitle(pil_img, line, font_path, font_size, font_color, stroke_color, stroke_width, y_pos_percent)
                frames_tensor[i] = self.pil_to_tensor_HWC(pil_img)
        audio_dur = self.get_audio_duration(audio_path, frames_tensor.shape[0], fps)
        video_dur = frames_tensor.shape[0] / fps
        if video_dur < audio_dur:
            needed = int(math.ceil(audio_dur * fps)) - frames_tensor.shape[0]
            if mode == "CHW":
                c, h, w = frames_tensor[0].shape
                black = torch.full((c, h, w), -1.0)
            else:
                h, w, c = frames_tensor[0].shape
                black = torch.full((h, w, c), -1.0)
            black = black.unsqueeze(0).repeat(needed, 1, 1, 1)
            frames_tensor = torch.cat([frames_tensor, black], dim=0)
        if isinstance(out_frames, dict) and "samples" in out_frames:
            out_frames["samples"] = frames_tensor
        else:
            out_frames = frames_tensor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return (out_frames,)

    def resolve_audio(self, audio_dict):
        if "filename" in audio_dict and audio_dict["filename"]:
            fname = audio_dict["filename"]
            if not os.path.isabs(fname):
                base = os.path.join(os.path.dirname(sys.argv[0]), "input")
                possible = os.path.join(base, fname)
                if os.path.exists(possible):
                    return possible
            return fname
        data = audio_dict.get("binary") or audio_dict.get("data")
        if data:
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.write(data)
            tmp_path = tmp.name
            tmp.close()
            return tmp_path
        wave_data = audio_dict.get("waveform")
        sr = audio_dict.get("sample_rate")
        if wave_data is not None and sr is not None:
            wave_np = wave_data.detach().cpu().numpy() if isinstance(wave_data, torch.Tensor) else np.array(wave_data)
            wave_np = np.squeeze(wave_np)
            wave_int16 = np.int16(wave_np * 32767)
            if wave_int16.ndim == 1:
                n_channels = 1
            elif wave_int16.ndim == 2:
                n_channels = wave_int16.shape[0]
                wave_int16 = wave_int16.T
            else:
                raise ValueError("Unexpected waveform shape.")
            tmpw = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmpw_path = tmpw.name
            tmpw.close()
            with wave.open(tmpw_path, "w") as wf:
                wf.setnchannels(n_channels)
                wf.setsampwidth(2)
                wf.setframerate(int(sr))
                wf.writeframes(wave_int16.tobytes())
            return tmpw_path
        raise FileNotFoundError("No valid audio found.")

    def get_audio_duration(self, audio_path, frame_count, fps):
        try:
            clip = AudioFileClip(audio_path)
            dur = clip.duration
            clip.close()
            return dur
        except:
            return frame_count / fps

    def tensor_to_pil_CHW(self, frame_tensor):
        f = frame_tensor.detach().cpu().float().clamp(-1, 1)
        f = (f * 0.5 + 0.5) * 255.0
        f = f.round().byte().permute(1, 2, 0)
        arr = f.numpy()
        return Image.fromarray(arr, "RGB")

    def pil_to_tensor_CHW(self, pil_img):
        arr = np.array(pil_img)
        t = torch.from_numpy(arr).float().permute(2, 0, 1)
        t = t / 255.0
        return (t - 0.5) / 0.5

    def tensor_to_pil_HWC(self, frame_tensor):
        f = frame_tensor.detach().cpu().float().clamp(-1, 1)
        f = (f * 0.5 + 0.5) * 255.0
        f = f.round().byte()
        arr = f.numpy()
        return Image.fromarray(arr, "RGB")

    def pil_to_tensor_HWC(self, pil_img):
        arr = np.array(pil_img)
        t = torch.from_numpy(arr).float()
        t = t / 255.0
        return (t - 0.5) / 0.5

    def draw_subtitle(self, pil_img, text, font_path, font_size, font_color, stroke_color, stroke_width, y_pos_percent):
        draw = ImageDraw.Draw(pil_img)
        font = ImageFont.truetype(font_path, font_size)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except AttributeError:
            tw, th = draw.textsize(text, font=font)
        x = (pil_img.width - tw) // 2
        y = int((1 - (y_pos_percent / 100.0)) * (pil_img.height - th))
        if stroke_width > 0:
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        draw.text((x, y), text, font=font, fill=font_color)
        return pil_img

# Registro para o ComfyUI
NODE_CLASS_MAPPINGS = {
    "SubtitleNode": SubtitleNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SubtitleNode": "🧪 Caption Generator"
}
