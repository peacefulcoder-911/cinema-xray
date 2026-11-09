#!/usr/bin/env python3
"""
Runs forced acoustic speech alignment and compiles CenterBold ASS subtitles
for Spider-Man: Homecoming — The Contract That Created The Vulture.
Emphasizes selected psychological and narrative anchor phrases:
  - 'ONE CANCELLED CONTRACT'
  - 'REAL CREW, REAL PAYROLL'
  - 'DAMAGE CONTROL'
  - 'ALIEN TECH'
  - 'PROTECTING A PAYROLL'
  - 'BELIEVABLE MOTIVE'
"""

import os
import sys
import json
import wave
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles

PROJECT_DIR = Path(__file__).resolve().parent
AUDIO_PATH = PROJECT_DIR / "audio" / "vulture_origin_master.wav"
SCRIPT_PATH = PROJECT_DIR / "script.txt"
SUBTITLES_JSON = PROJECT_DIR / "subtitles.json"
SUBTITLES_ASS = PROJECT_DIR / "vulture_origin_subtitles.ass"

KEYWORD_HIGHLIGHTS = {
    "SALVAGE": "SALVAGE",
    "ALIEN": "ALIEN",
    "WEAPONS": "WEAPONS",
    "CANCELLED": "CANCELLED",
    "CONTRACT": "CONTRACT",
    "HOMECOMING": "HOMECOMING",
    "OPENING": "OPENING",
    "MINUTES": "MINUTES",
    "WRECKAGE": "WRECKAGE",
    "CREW": "CREW",
    "PAYROLL": "PAYROLL",
    "DAMAGE": "DAMAGE",
    "CONTROL": "CONTROL",
    "STARK'S": "STARK'S",
    "WAREHOUSE": "WAREHOUSE",
    "BUILDS": "BUILDS",
    "POWER": "POWER",
    "PROTECTING": "PROTECTING",
    "VILLAIN": "VILLAIN",
    "BELIEVABLE": "BELIEVABLE",
    "MOTIVE": "MOTIVE"
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

