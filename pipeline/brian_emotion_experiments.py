#!/usr/bin/env python3
"""
Cinema X-Ray / Movie Breakdown: Brian Voice & Emotion Benchmarking
Synthesizes side-by-side comparative audios with Brian (nPczCjzI2devNBz1zQrb):
  1. Script 1 (Dark Knight) WITH emotion tags in parentheses
  2. Script 1 (Dark Knight) CLEAN without brackets, sculpted via punctuation & dynamic parameters
  3. Script 2 (Interstellar) WITH emotion tags in parentheses
  4. Script 2 (Interstellar) CLEAN without brackets, sculpted via punctuation & dynamic parameters
  5. Script 2 (Interstellar) FULL CINEMATIC MIX (Brian + Sub-Bass Tension Bed + Precision Audio Mastering)
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "output" / "voice_experiments"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load API key
def _get_key():
    p = REPO_ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("ELEVENLABS_API_KEY")

KEY = _get_key()
BRIAN_ID = "nPczCjzI2devNBz1zQrb"

# SCRIPT 1: The Dark Knight
SCRIPT_1_WITH_PARENS = """Notice how in The Dark Knight, the Joker never actually tries to kill Batman? (hushed, intense)
In the interrogation room, when Batman beats him against the wall, the Joker doesn't flinch—he laughs. (disturbed, breathless)
He literally tells him: "You complete me." (chilling imitation)
A lot of people think the Joker wants chaos. But his real target was never Gotham. (building urgency)
It was Batman’s morality. (firm, deliberate)
The Joker knows that if Batman kills just one person, the entire symbol collapses. (dramatic revelation)
He wasn't trying to win a fight. He was trying to prove that even Gotham's purest hero... is just one bad day away from becoming a monster. (grim, lingering payoff)"""

SCRIPT_1_CLEAN = """Notice how in The Dark Knight, the Joker never actually tries to kill Batman?
In the interrogation room, when Batman beats him against the wall, the Joker doesn't flinch—he laughs.
He literally tells him: "You complete me."
A lot of people think the Joker wants chaos. But his real target was never Gotham.
It was Batman’s morality.
The Joker knows that if Batman kills just one person—even him—the entire symbol collapses.
He wasn't trying to win a fight.
He was trying to prove that even Gotham's purest hero... is just one bad day away from becoming a monster."""

# SCRIPT 2: Interstellar
SCRIPT_2_WITH_PARENS = """Did you know that in Interstellar, the background music is actually a ticking stopwatch? (intriguing, curious)
Every single time you hear that sharp wooden tick on Miller's Planet, exactly one point four seconds has passed. (precise, informative)
And here is the terrifying detail: (sudden dread)
Each of those ticks equals an entire full day back on Earth. (grim realization)
While Cooper takes three steps through the water, another morning and night has passed for his children. (emotional weight)
By the time they escape that giant wave, twenty-three years have vanished. (heavy, tragic)
Hans Zimmer didn't just compose a soundtrack. He turned the passage of time... into a relentless death clock. (powerful, resonant payoff)"""

SCRIPT_2_CLEAN = """Did you know that in Interstellar, the background music is actually a ticking stopwatch?
Every single time you hear that sharp wooden tick on Miller's Planet, exactly one point four seconds has passed.
And here is the terrifying detail...
Each of those ticks equals an entire full day back on Earth.
While Cooper takes three steps through the knee-deep water, another morning and night has vanished for his children.
By the time they escape that single wave—twenty-three years are gone.
Hans Zimmer didn't just compose a soundtrack.
He turned time itself... into a relentless death clock."""


def synthesize_elevenlabs(text: str, settings: dict, out_mp3: Path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{BRIAN_ID}"
    headers = {"xi-api-key": KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": settings
    }
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    if res.status_code == 200:
        out_mp3.write_bytes(res.content)
        return True
    else:
        print(f"Error {res.status_code}: {res.text[:200]}")
        return False


def master_voice(in_mp3: Path, out_wav: Path, out_mp3: Path, target_peak_db: float = -1.0) -> dict:
    temp_wav = out_wav.with_suffix(".temp.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(in_mp3), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(temp_wav)], check=True)
    
    res = subprocess.run(["ffmpeg", "-i", str(temp_wav), "-af", "volumedetect", "-f", "null", "-"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    max_vol = -1.0
    for line in res.stderr.splitlines():
        if "max_volume:" in line:
            try:
                max_vol = float(line.split("max_volume:")[1].replace("dB", "").strip())
            except Exception:
                pass
    
    gain_db = max(-12.0, min(12.0, target_peak_db - max_vol))
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(temp_wav), "-af", f"volume={gain_db:.2f}dB", "-ar", "48000", "-c:a", "pcm_s16le", str(out_wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(out_wav), "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)], check=True)
    if temp_wav.exists():
        temp_wav.unlink()

    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_wav)]
    dur = float(subprocess.check_output(cmd).decode().strip())
    return {"duration": round(dur, 2), "peak_db": round(max_vol + gain_db, 2)}


def create_cinematic_mix(vocal_wav: Path, out_mixed_mp3: Path, duration: float):
    """Mixes Brian's voice with a subtle atmospheric sub-bass tension drone and Hans Zimmer-style pulse."""
    # Synthesize clean 55Hz cinematic sub-bass + low-passed pink noise rumble
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=f=52:d={duration:.2f},volume=0.08,lowpass=f=110",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration:.2f}:c=pink:r=48000:a=0.015,lowpass=f=350,volume=0.12",
        "-i", str(vocal_wav),
        "-filter_complex",
        f"[0:a][1:a]amix=inputs=2:duration=first[drone];"
        f"[2:a]volume=1.20[vocal];"
        f"[drone][vocal]amix=inputs=2:duration=first:dropout_transition=2,"
        f"afade=t=out:st={duration - 0.50:.2f}:d=0.50[outa]",
        "-map", "[outa]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_mixed_mp3)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def main():
    print("=" * 70)
    print("🎬 BRIAN VOICE & EMOTION EXPERIMENTAL BENCHMARK")
    print("=" * 70)

    experiments = [
        {
            "id": "01_dark_knight_with_brackets",
            "title": "Dark Knight (With Emotional Brackets)",
            "text": SCRIPT_1_WITH_PARENS,
            "settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True},
            "desc": "Literal brackets inserted: (hushed), (chilling imitation), (dramatic revelation)"
        },
        {
            "id": "02_dark_knight_clean_sculpted",
            "title": "Dark Knight (Clean Punctuation & Emotion Sculpting)",
            "text": SCRIPT_1_CLEAN,
            "settings": {"stability": 0.36, "similarity_boost": 0.78, "style": 0.45, "use_speaker_boost": True},
            "desc": "Clean script without brackets; emotional range boosted via stability=0.36, style=0.45, em-dashes and pauses"
        },
        {
            "id": "03_interstellar_with_brackets",
            "title": "Interstellar (With Emotional Brackets)",
            "text": SCRIPT_2_WITH_PARENS,
            "settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True},
            "desc": "Literal brackets inserted: (intriguing), (sudden dread), (grim realization)"
        },
        {
            "id": "04_interstellar_clean_sculpted",
            "title": "Interstellar (Clean Punctuation & Emotion Sculpting)",
            "text": SCRIPT_2_CLEAN,
            "settings": {"stability": 0.34, "similarity_boost": 0.80, "style": 0.50, "use_speaker_boost": True},
            "desc": "Clean script without brackets; higher dynamic range via stability=0.34, style=0.50, ellipses and cadence control"
        }
    ]

    results = []

    for idx, exp in enumerate(experiments, 1):
        print(f"\n[{idx}/4] Generating {exp['title']}...")
        t_raw = OUT_DIR / f"{exp['id']}_raw.mp3"
        out_wav = OUT_DIR / f"{exp['id']}.wav"
        out_mp3 = OUT_DIR / f"{exp['id']}.mp3"

        if synthesize_elevenlabs(exp["text"], exp["settings"], t_raw):
            m = master_voice(t_raw, out_wav, out_mp3)
            if t_raw.exists():
                t_raw.unlink()
            print(f"   ✅ Mastered: {out_mp3.name} ({m['duration']}s, Peak {m['peak_db']} dB)")
            results.append({**exp, **m, "mp3_path": str(out_mp3), "wav_path": str(out_wav)})

    # Generate 5th sample: Full Cinematic Audio Mix (Brian + Atmospheric Score)
    print("\n[5/5] Generating Full Cinematic Master Mix (Brian + Atmospheric Sub-Bass Bed)...")
    clean_interstellar_wav = OUT_DIR / "04_interstellar_clean_sculpted.wav"
    mixed_mp3 = OUT_DIR / "05_interstellar_brian_cinematic_mix.mp3"
    if clean_interstellar_wav.exists():
        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(clean_interstellar_wav)]
        dur = float(subprocess.check_output(dur_cmd).decode().strip())
        create_cinematic_mix(clean_interstellar_wav, mixed_mp3, dur)
        print(f"   ✅ Created Cinematic Atmosphere Mix: {mixed_mp3.name} ({dur:.2f}s)")
        results.append({
            "id": "05_interstellar_brian_cinematic_mix",
            "title": "Interstellar (Full Cinematic Tension Mix)",
            "desc": "Brian's voice layered over sub-bass atmospheric tension drone (zero forbidden whooshes/risers)",
            "duration": dur,
            "mp3_path": str(mixed_mp3),
            "wav_path": str(clean_interstellar_wav)
        })

    results_file = OUT_DIR / "brian_experiment_results.json"
    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n🎉 All experiment audio tracks generated in {OUT_DIR}!")


if __name__ == "__main__":
    main()
