import subprocess
import json

def get_video_duration(video_path):
    try:
        command = [
            "ffprobe",  # important: use ffprobe, not ffmpeg
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("FFprobe error:", result.stderr)
            return 0

        data = json.loads(result.stdout)
        print("FFprobe output:", data['format'])
        duration = float(data["format"]["duration"])
        return int(duration)

    except Exception as e:
        print("Duration extraction error:", e)
        return 0