#!/usr/bin/env python3
"""
Generate millisecond-accurate word timestamps and CenterBold ASS subtitles for Limitless.
Highlights critical psychological keywords in cinematic yellow (&H0000E5FF&):
INTELLIGENCE, AMBITION, CONTROL, DEPENDENCY, JUDGMENT, WISDOM, DANGEROUS, NZT48, CLARITY.
"""

import os
import json
import subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

BASE_DIR = Path(__file__).resolve().parent
AUDIO_FILE = BASE_DIR / "audio" / "limitless_achird_master.wav"
WORDS_JSON = BASE_DIR / "subtitles.json"
ASS_FILE = BASE_DIR / "limitless_subtitles.ass"

KEYWORD_TARGETS = {
    "INTELLIGENCE", "AMBITION", "CONTROL", "DEPENDENCY",
    "JUDGMENT", "WISDOM", "DANGEROUS", "NZT48", "NZT",
    "CLARITY", "CONSEQUENCES", "POSSIBILITIES", "OPTIONS",
    "POWERFUL", "SMARTER", "DECIDE"
}

def format_ass_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    csecs = int(round((seconds - int(seconds)) * 100))
    if csecs >= 100:
        csecs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{csecs:02d}"

def clean_word(w: str) -> str:
    return "".join(c for c in w if c.isalnum()).upper()

def main():
    print(f"Loading master audio: {AUDIO_FILE}")
    if not AUDIO_FILE.exists():
        raise FileNotFoundError(f"Missing {AUDIO_FILE}")

    # Decode audio to 16kHz mono PCM buffer
    pcm_cmd = [
        "ffmpeg", "-v", "quiet",
        "-i", str(AUDIO_FILE),
        "-f", "s16le", "-ac", "1", "-ar", "16000", "-"
    ]
    proc = subprocess.run(pcm_cmd, stdout=subprocess.PIPE, check=True)
    audio_np = np.frombuffer(proc.stdout, np.int16).flatten().astype(np.float32) / 32768.0

    print("Transcribing with faster-whisper (word_timestamps=True)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_np, word_timestamps=True)

    words_data = []
    events = []

    for seg in segments:
        seg_words = list(seg.words)
        if not seg_words:
            continue

        for w in seg_words:
            wt = w.word.strip()
            if wt:
                words_data.append({
                    "word": wt,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3)
                })

        # Group words into 3-4 word phrases for punchy vertical Shorts subtitles
        chunk_size = 3
        for i in range(0, len(seg_words), chunk_size):
            chunk = seg_words[i:i + chunk_size]
            c_start = chunk[0].start
            c_end = chunk[-1].end
            
            # Format text with yellow keyword styling
            styled_tokens = []
            for item in chunk:
                raw_w = item.word.strip()
                norm = clean_word(raw_w)
                if norm in KEYWORD_TARGETS:
                    # Highlight keyword in yellow (&H0000E5FF& in BGR)
                    styled_tokens.append(f"{{\\c&H0000E5FF&}}{raw_w.upper()}{{\\c&H00FFFFFF&}}")
                else:
                    styled_tokens.append(raw_w.upper())

            chunk_text = " ".join(styled_tokens)
            events.append((c_start, c_end, chunk_text))

    # Save subtitles.json
    with open(WORDS_JSON, "w", encoding="utf-8") as f:
        json.dump(words_data, f, indent=2)
    print(f"Saved {len(words_data)} aligned words to {WORDS_JSON}")

    # Build ASS subtitle file
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterBold,Arial Black,76,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,5,60,60,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_lines = [ass_header.strip()]
    for st, en, txt in events:
        start_str = format_ass_time(st)
        end_str = format_ass_time(en)
        ass_lines.append(f"Dialogue: 0,{start_str},{end_str},CenterBold,,0,0,0,,{txt}")

    with open(ASS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines) + "\n")
    print(f"Saved CenterBold ASS subtitles to {ASS_FILE} ({len(events)} events)")

if __name__ == "__main__":
    main()

