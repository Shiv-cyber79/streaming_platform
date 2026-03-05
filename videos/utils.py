import os
import subprocess
import json
from django.conf import settings
import shutil
ffprobe_path  = os.path.join(settings.BASE_DIR, "tools", "ffprobe.exe")
# print("FFprobe path:", ffprobe_path)
def get_video_duration(video_path):
    try:
        command = [
            ffprobe_path if ffprobe_path else "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        print("FFprobe stdout:", result.stdout)
        print("FFprobe stderr:", result.stderr)

        if result.returncode != 0:
            print("❌ FFprobe failed")
            return 0

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])

        print("🎯 Extracted duration:", duration)
        return int(duration)

    except Exception as e:
        print("Duration extraction error:", e)
        return 0