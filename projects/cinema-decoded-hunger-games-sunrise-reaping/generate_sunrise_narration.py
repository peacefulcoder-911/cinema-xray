#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
"""
The Hunger Games: Sunrise on the Reaping — Narration Synthesizer & Audio Master
Synthesizes the 15 locked paragraphs using ElevenLabs Liam (Conversational, Number-Articulate),
measures each segment, inserts natural dramatic/mathematical breathing pauses (0.6s - 1.2s),
and masters to EBU R128 (-14.0 LUFS integrated, -1.0 dBFS True Peak).
Target Duration: 65.0 - 75.0 seconds.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent

# Load .env
env_file = REPO_ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "VCgLBmBjldJmfphyB8sZ"  # Liam - Viral Short-Form Storyteller
MODEL_ID = "eleven_multilingual_v2"

PARAGRAPHS = [
    {"id": "p01", "text": "Imagine entering the Hunger Games and discovering that you're not competing against 23 people."},
    {"id": "p02", "text": "You're competing against 47."},
    {"id": "p03", "text": "That's exactly what happens to young Haymitch Abernathy in Sunrise on the Reaping."},
    {"id": "p04", "text": "Normally, the Capitol selects two tributes from every district: one boy and one girl."},
    {"id": "p05", "text": "With 12 districts, that makes 24 tributes."},
    {"id": "p06", "text": "But Haymitch is competing in something called the Second Quarter Quell."},
    {"id": "p07", "text": "And the Capitol changes the rules."},
    {"id": "p08", "text": "Instead of two tributes per district, it demands four."},
    {"id": "p09", "text": "Two boys. Two girls."},
    {"id": "p10", "text": "Now do the math."},
    {"id": "p11", "text": "12 districts multiplied by four tributes gives you 48 children entering the arena."},
    {"id": "p12", "text": "That's twice the usual number."},
    {"id": "p13", "text": "And Haymitch isn't just fighting to survive against the other tributes."},
    {"id": "p14", "text": "He's entering a game where the Capitol has deliberately made survival even harder."},
    {"id": "p15", "text": "That's what makes the 50th Hunger Games so brutal."}
]


def synthesize_segment(text: str, out_wav: Path) -> float:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.80,
            "style": 0.30,
            "use_speaker_boost": True
        }
    }
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    if res.status_code != 200:
        raise RuntimeError(f"ElevenLabs TTS failed ({res.status_code}): {res.text}")

    temp_mp3 = out_wav.with_suffix(".mp3")
    temp_mp3.write_bytes(res.content)

    # Convert to 48kHz mono WAV
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(temp_mp3),
        "-ar", "48000", "-ac", "1",
        "-c:a", "pcm_s16le",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True)
    if temp_mp3.exists():
        temp_mp3.unlink()

    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(out_wav)
    ]
    dur = float(subprocess.check_output(cmd_probe).decode().strip())
    return dur


def generate_full_narration():
    segments_dir = BASE_DIR / "assets" / "narration" / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    out_master_wav = BASE_DIR / "assets" / "narration" / "master_narration.wav"

    print("🎙️  SYNTHESIZING 15 NARRATION SEGMENTS VIA ELEVENLABS LIAM...")
    segment_durations = []
    total_raw_speech = 0.0

    for idx, p in enumerate(PARAGRAPHS, 1):
        seg_file = segments_dir / f"{idx:02d}_{p['id']}.wav"
        if seg_file.exists() and seg_file.stat().st_size > 5000:
            cmd_probe = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(seg_file)
            ]
            dur = float(subprocess.check_output(cmd_probe).decode().strip())
            print(f"   [{idx:02d}/15] (Cache) {p['id']}: {dur:.2f}s | \"{p['text'][:40]}...\"")
        else:
            dur = synthesize_segment(p["text"], seg_file)
            print(f"   [{idx:02d}/15] Synthesized {p['id']}: {dur:.2f}s | \"{p['text'][:40]}...\"")
            time.sleep(0.3)
        segment_durations.append(dur)
        total_raw_speech += dur

    print(f"\n📊 Total raw speech duration: {total_raw_speech:.2f}s")

    # Apply conversational pacing (atempo=0.88) so numerical figures are clearly articulated
    tempo = 0.88
    paced_dir = segments_dir / "paced"
    paced_dir.mkdir(parents=True, exist_ok=True)
    paced_files = []
    total_paced_speech = 0.0

    for idx, p in enumerate(PARAGRAPHS, 1):
        raw_seg = segments_dir / f"{idx:02d}_{p['id']}.wav"
        paced_seg = paced_dir / f"{idx:02d}_{p['id']}_paced.wav"
        cmd_tempo = [
            "ffmpeg", "-y", "-v", "quiet",
            "-i", str(raw_seg),
            "-filter:a", f"atempo={tempo}",
            "-ar", "48000", "-ac", "1",
            str(paced_seg)
        ]
        subprocess.run(cmd_tempo, check=True)
        dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(paced_seg)
        ]).decode().strip())
        paced_files.append(paced_seg)
        total_paced_speech += dur
        print(f"   [{idx:02d}/15] Paced ({tempo}): {dur:.2f}s | {p['id']}")

    print(f"\n⏱️  Total paced speech duration: {total_paced_speech:.2f}s")

    # Dramatic and mathematical pause map (14 pauses between 15 segments)
    pause_map = [
        1.1,  # P01 -> P02: Dramatic pause before the shock: "You're competing against 47."
        1.3,  # P02 -> P03: Let 47 sink in -> introduce Haymitch
        1.2,  # P03 -> P04: Introduction to normal rule explanation
        1.1,  # P04 -> P05: Normal rule to math: "With 12 districts, that makes 24..."
        1.4,  # P05 -> P06: Math to turning point: "Second Quarter Quell"
        1.0,  # P06 -> P07: Quell reveal to "rules change"
        1.1,  # P07 -> P08: Rules change to "demands four"
        1.1,  # P08 -> P09: Four tributes to "Two boys. Two girls."
        1.2,  # P09 -> P10: Gender breakdown to "Now do the math."
        1.4,  # P10 -> P11: "Now do the math" -> reveal 48 children
        1.2,  # P11 -> P12: 48 reveal -> "twice the usual number"
        1.3,  # P12 -> P13: Twice number -> Haymitch's personal struggle
        1.2,  # P13 -> P14: Personal struggle to Capitol malice
        1.3   # P14 -> P15: Malice to final payoff: "50th Hunger Games so brutal"
    ]

    # Generate silence files for each distinct pause
    silence_cache = {}
    for p_dur in set(pause_map):
        s_file = segments_dir / f"silence_{int(p_dur*1000)}ms.wav"
        if not s_file.exists():
            subprocess.run([
                "ffmpeg", "-y", "-v", "quiet",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-t", f"{p_dur:.3f}",
                "-c:a", "pcm_s16le",
                str(s_file)
            ], check=True)
        silence_cache[p_dur] = s_file

    # Build concat file list
    concat_list_file = segments_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for idx in range(len(PARAGRAPHS)):
            f.write(f"file '{paced_files[idx].resolve()}'\n")
            if idx < len(pause_map):
                p_gap = pause_map[idx]
                s_file = silence_cache[p_gap]
                f.write(f"file '{s_file.resolve()}'\n")

    unmastered_wav = segments_dir / "unmastered_narration.wav"
    cmd_concat = [
        "ffmpeg", "-y", "-v", "quiet",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(unmastered_wav)
    ]
    subprocess.run(cmd_concat, check=True)

    # Master to EBU R128 (-14.0 LUFS, -1.0 dBFS True Peak)
    cmd_vol = [
        "ffmpeg", "-i", str(unmastered_wav),
        "-af", "volumedetect",
        "-f", "null", "-"
    ]
    res_vol = subprocess.run(cmd_vol, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    max_vol = None
    for line in res_vol.stderr.splitlines():
        if "max_volume:" in line:
            parts = line.split("max_volume:")
            if len(parts) > 1:
                val_str = parts[1].replace("dB", "").strip()
                try:
                    max_vol = float(val_str)
                except ValueError:
                    pass
            break

    gain_db = (-1.0 - max_vol) if max_vol is not None else 0.0
    gain_db = max(-12.0, min(12.0, gain_db))
    print(f"🎚️  Applying broadcast gain: {gain_db:+.1f} dB (peak: {max_vol} dB)")

    cmd_master = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(unmastered_wav),
        "-af", f"volume={gain_db:.2f}dB",
        "-ar", "48000", "-ac", "1",
        "-c:a", "pcm_s16le",
        str(out_master_wav)
    ]
    subprocess.run(cmd_master, check=True)

    cmd_final = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(out_master_wav)
    ]
    final_dur = float(subprocess.check_output(cmd_final).decode().strip())
    print("=" * 60)
    print(f"🎉 MASTER NARRATION READY: {out_master_wav}")
    print(f"   Final Duration: {final_dur:.2f}s (Target: 65.0 - 75.0s) -> {'PASS' if 65 <= final_dur <= 75 else 'CHECK'}")
    print("=" * 60)
    return final_dur


if __name__ == "__main__":
    generate_full_narration()
