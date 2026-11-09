#!/usr/bin/env python3
"""
Runs forced acoustic speech alignment and compiles CenterBold ASS subtitles
for The Matrix: Why Cypher Chooses The Lie.
Emphasizes selected psychological anchor phrases:
  - 'THE STEAK IS FAKE'
  - 'HE KNOWS THE TRUTH'
  - 'IGNORANCE IS BLISS'
  - 'IS THE TRUTH WORTH IT?'
"""

import os
import sys
import json
import wave
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles, format_ass_time

PROJECT_DIR = Path(__file__).resolve().parent
AUDIO_PATH = PROJECT_DIR / "audio" / "matrix_cypher_master.wav"
SCRIPT_PATH = PROJECT_DIR / "script.txt"
SUBTITLES_JSON = PROJECT_DIR / "subtitles.json"
SUBTITLES_ASS = PROJECT_DIR / "matrix_cypher_subtitles.ass"

KEYWORD_HIGHLIGHTS = {
    "FAKE": "FAKE",
    "STEAK": "STEAK",
    "ILLUSION": "ILLUSION",
    "DECISION": "DECISION",
    "IGNORANCE": "IGNORANCE",
    "BLISS": "BLISS",
    "ANSWER": "ANSWER",
    "SUFFERING": "SUFFERING",
    "TRUTH": "TRUTH",
    "LIE": "LIE"
}

def main():
    print("=" * 70)
    print("📝 GENERATING TIMED SUBTITLES VIA ACOUSTIC ALIGNMENT")
    print("=" * 70)
    
    with wave.open(str(AUDIO_PATH), "rb") as wf:
        total_duration = wf.getnframes() / wf.getframerate()
    print(f"Total audio duration: {total_duration:.2f}s")
    
    script_text = SCRIPT_PATH.read_text(encoding="utf-8").strip()
    
    # 1. Run alignment
    cards = generate_timed_subtitles(
        audio_path=str(AUDIO_PATH),
        script_text=script_text,
        total_duration=total_duration,
        cache_json_path=str(SUBTITLES_JSON),
        force_refresh=True,
        video_format="SHORT_45_SEC"
    )
    print(f"✅ Generated {len(cards)} timed subtitle cards.")

    # Post-process highlights for key phrases
    for c in cards:
        words = c["text"].upper().split()
        for w in words:
            cleaned = w.strip(",.!?\"'")
            if cleaned in KEYWORD_HIGHLIGHTS:
                c["highlight"] = cleaned
                break
                
    # Add final impact card: "WOULD YOU CHOOSE THE TRUTH?" from 43.5s to 46.0s
    cards.append({
        "start": 43.20,
        "end": round(total_duration - 0.2, 2),
        "text": "WOULD YOU CHOOSE THE TRUTH?",
        "highlight": "TRUTH"
    })
    
    with open(SUBTITLES_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "video_format": "SHORT_45_SEC",
            "total_cards": len(cards),
            "cards": cards
        }, f, indent=2)
    
    # 2. Build ASS subtitle file
    ass_path = build_ass_subtitles(
        cards=cards,
        output_ass_path=str(SUBTITLES_ASS),
        video_format="SHORT_45_SEC"
    )
    print(f"✅ CenterBold ASS Subtitles generated: {ass_path}")

if __name__ == "__main__":
    main()

