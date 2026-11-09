#!/usr/bin/env python3
"""
Runs forced Whisper acoustic speech alignment and compiles CenterBold ASS subtitles
for The Incredibles Short.
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles

PROJECT_DIR = Path(__file__).resolve().parent
AUDIO_PATH = PROJECT_DIR / "audio" / "incredibles_achird_master.wav"
SCRIPT_PATH = PROJECT_DIR / "script.txt"
SUBTITLES_JSON = PROJECT_DIR / "subtitles.json"
SUBTITLES_ASS = PROJECT_DIR / "incredibles_subtitles.ass"

def main():
    print("=" * 70)
    print("📝 GENERATING TIMED SUBTITLES VIA FASTER-WHISPER FOR THE INCREDIBLES")
    print("=" * 70)
    
    script_text = SCRIPT_PATH.read_text(encoding="utf-8").strip()
    
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(AUDIO_PATH)]
    actual_dur = float(subprocess.check_output(cmd).decode().strip())
    print(f"Master audio duration: {actual_dur:.2f}s")
    
    # 1. Run Whisper forced alignment
    cards = generate_timed_subtitles(
        audio_path=str(AUDIO_PATH),
        script_text=script_text,
        total_duration=actual_dur,
        cache_json_path=str(SUBTITLES_JSON),
        force_refresh=True,
        video_format="SHORT_45_SEC"
    )
    print(f"✅ Generated {len(cards)} timed subtitle cards.")
    
    # 2. Build ASS subtitle file
    ass_path = build_ass_subtitles(
        cards=cards,
        output_ass_path=str(SUBTITLES_ASS),
        video_format="SHORT_45_SEC"
    )
    print(f"✅ CenterBold ASS Subtitles generated: {ass_path}")

if __name__ == "__main__":
    main()

