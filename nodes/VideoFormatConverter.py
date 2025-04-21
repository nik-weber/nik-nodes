import os, subprocess, cv2

class VideoFormatConverter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path":   ("STRING", {"multiline": False, "default": ""}),
                "output_path":  ("STRING", {"multiline": False, "default": ""}),
                "output_name":  ("STRING", {"multiline": False, "default": "converted"}),
                "video_format": (["avi", "mov", "mkv", "mp4"], {"default": "mp4"}),
                "codec":        (["av1", "h264", "h264(NVENC)", "hevc", "hevc(NVENC)"], {"default": "h264"}),
                "quality":      ("INT", {"default": 18, "min": 5, "max": 40, "step": 1}),
                "frame_rate":   ("INT", {"default": 30, "min": 1, "max": 240}),
                "audio_codec":  (["copy", "aac", "mp3"], {"default": "aac"})
            }
        }

    RETURN_TYPES  = ("STRING", "DICT")
    RETURN_NAMES  = ("output_file", "video_info")
    FUNCTION      = "convert"
    CATEGORY      = "N!K/video"

    def convert(
        self, video_path, output_path, output_name,
        video_format, codec, quality, frame_rate, audio_codec
    ):
        if not os.path.isfile(video_path):
            raise FileNotFoundError("video_path not found")

        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, f"{output_name}.{video_format}")

        codec_map = {
            "h264(NVENC)": "h264_nvenc",
            "hevc(NVENC)": "hevc_nvenc",
            "hevc": "libx265",
            "av1":  "libaom-av1"
        }
        codec_cli = codec_map.get(codec, codec)

        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-c:v", codec_cli,
            "-crf", str(quality),
            "-r", str(frame_rate),
            "-c:a", audio_codec,
            output_file
        ]
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            raise RuntimeError(run.stderr.strip())

        cap = cv2.VideoCapture(output_file)
        info = {
            "fps":          cap.get(cv2.CAP_PROP_FPS),
            "frames":       int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width":        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height":       int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration_sec": int(cap.get(cv2.CAP_PROP_FRAME_COUNT))/cap.get(cv2.CAP_PROP_FPS)
        }
        cap.release()
        return (output_file, info)

NODE_CLASS_MAPPINGS = {"VideoFormatConverter": VideoFormatConverter}
NODE_DISPLAY_NAME_MAPPINGS = {"VideoFormatConverter": "🧪 Video Format Converter"}
