#!/usr/bin/env python3
"""
Cinema X-Ray / Movie Breakdown: Voice Audition Benchmarker
Generates side-by-side voiceover samples for a standardized benchmark script
across the top 8 voice archetypes (ElevenLabs + Neural), mastered to EBU R128 (-14 LUFS).
Outputs WAV and MP3 files in output/voice_auditions/ with technical inspection metrics.
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output" / "voice_auditions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ensure environment variables loaded
def _load_env():
    p = REPO_ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_env()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

BENCHMARK_SCRIPT = """Notice how in Fight Club, Edward Norton’s character never actually has a name? Throughout the entire movie, nobody ever calls him by his real name. In the script, he’s simply credited as "The Narrator." A lot of people think his name is Jack because of lines like "I am Jack’s smirking revenge"—but Jack isn't his name at all. He’s an anonymous corporate drone who defined his entire existence through IKEA catalogs and consumer brands. He felt so invisible that his mind literally split in two to survive. The Narrator doesn't have a name because he gave all his confidence, courage, and freedom to someone else: Tyler Durden."""

CANDIDATE_VOICES = [
    {
        "id": "01_adam_cinematic",
        "name": "Adam",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "archetype": "Dominant, Firm, Deep Cinematic",
        "category": "elevenlabs",
        "settings": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True}
    },
    {
        "id": "02_chris_conversational",
        "name": "Chris",
        "voice_id": "iP95p4xoKVk53GoZ742B",
        "archetype": "Charming, Down-to-Earth, Natural",
        "category": "elevenlabs",
        "settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True}
    },
    {
        "id": "03_charlie_modern_fast",
        "name": "Charlie",
        "voice_id": "IKne3meq5aSn9XLyUdCD",
        "archetype": "Deep, Confident, Modern Fast-Paced",
        "category": "elevenlabs",
        "settings": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True}
    },
    {
        "id": "04_brian_dark_baritone",
        "name": "Brian",
        "voice_id": "nPczCjzI2devNBz1zQrb",
        "archetype": "Deep, Resonant Baritone",
        "category": "elevenlabs",
        "settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.25, "use_speaker_boost": True}
    },
    {
        "id": "05_george_british_storyteller",
        "name": "George",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "archetype": "Warm, Captivating British Storyteller",
        "category": "elevenlabs",
        "settings": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True}
    },
    {
        "id": "06_roger_laid_back",
        "name": "Roger",
        "voice_id": "CwhRBWXzGAHq8TQ4Fs17",
        "archetype": "Laid-Back, Casual, Resonant",
        "category": "elevenlabs",
        "settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True}
    },
    {
        "id": "07_sarah_confident_female",
        "name": "Sarah",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "archetype": "Mature, Reassuring, Confident Female",
        "category": "elevenlabs",
        "settings": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True}
    },
    {
        "id": "08_christopher_neutral_doc",
        "name": "Christopher",
        "voice_id": "en-US-ChristopherNeural",
        "archetype": "Clean Neutral Studio Documentary",
        "category": "edge_tts",
        "rate": "+8%"
    }
]


def synthesize_elevenlabs(voice_info: Dict[str, Any], temp_mp3: Path) -> bool:
    import requests
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_info['voice_id']}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": BENCHMARK_SCRIPT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": voice_info["settings"]
    }
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    if res.status_code == 200:
        temp_mp3.write_bytes(res.content)
        return True
    else:
        print(f"   ⚠️ ElevenLabs error ({res.status_code}): {res.text[:200]}")
        return False


def synthesize_edge_tts(voice_info: Dict[str, Any], temp_mp3: Path) -> bool:
    try:
        import edge_tts
        async def _run():
            comm = edge_tts.Communicate(BENCHMARK_SCRIPT, voice=voice_info["voice_id"], rate=voice_info.get("rate", "+8%"))
            await comm.save(str(temp_mp3))
        asyncio.run(_run())
        return temp_mp3.exists() and temp_mp3.stat().st_size > 1000
    except Exception as e:
        print(f"   ⚠️ Edge-TTS error: {e}")
        return False


def master_audio(raw_mp3: Path, out_wav: Path, out_mp3: Path, target_peak_db: float = -1.0) -> Dict[str, Any]:
    """Applies static linear peak gain mastering without dynamic pumping to -1.0 dBFS Peak / -14 LUFS."""
    # 1. Transcode raw mp3 to temporary 48k PCM wav
    temp_wav = out_wav.with_suffix(".temp.wav")
    cmd_trans = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(raw_mp3),
        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
        str(temp_wav)
    ]
    subprocess.run(cmd_trans, check=True)

    # 2. Measure peak volume
    cmd_meas = [
        "ffmpeg", "-i", str(temp_wav),
        "-af", "volumedetect",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd_meas, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    max_vol = -1.0
    mean_vol = -16.0
    for line in res.stderr.splitlines():
        if "max_volume:" in line:
            try:
                max_vol = float(line.split("max_volume:")[1].replace("dB", "").strip())
            except Exception:
                pass
        elif "mean_volume:" in line:
            try:
                mean_vol = float(line.split("mean_volume:")[1].replace("dB", "").strip())
            except Exception:
                pass

    gain_db = max(-12.0, min(12.0, target_peak_db - max_vol))

    # 3. Export mastered WAV (48kHz 16-bit PCM)
    cmd_wav = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(temp_wav),
        "-af", f"volume={gain_db:.2f}dB",
        "-ar", "48000", "-c:a", "pcm_s16le",
        str(out_wav)
    ]
    subprocess.run(cmd_wav, check=True)

    # 4. Export mastered MP3 (high-bitrate for web preview)
    cmd_mp3 = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", str(out_wav),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_mp3)
    ]
    subprocess.run(cmd_mp3, check=True)

    if temp_wav.exists():
        temp_wav.unlink()

    # Probe duration
    cmd_dur = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(out_wav)
    ]
    dur_str = subprocess.check_output(cmd_dur).decode().strip()
    duration = float(dur_str)

    return {
        "duration": round(duration, 2),
        "peak_db": round(max_vol + gain_db, 2),
        "mean_db": round(mean_vol + gain_db, 2),
        "gain_applied": round(gain_db, 2),
        "wav_size_kb": round(out_wav.stat().st_size / 1024, 1),
        "mp3_size_kb": round(out_mp3.stat().st_size / 1024, 1),
    }


def main():
    print("=" * 70)
    print("🎙️ CINEMA X-RAY: VOICE AUDITION & BENCHMARKING ENGINE")
    print("=" * 70)
    print(f"Target Script: {len(BENCHMARK_SCRIPT.split())} words (~30-35s)")
    print(f"Output Directory: {OUTPUT_DIR}\n")

    results = []

    for idx, v in enumerate(CANDIDATE_VOICES, 1):
        v_id = v["id"]
        v_name = v["name"]
        print(f"[{idx}/{len(CANDIDATE_VOICES)}] Auditioning: {v_name} ({v['archetype']})...")
        t0 = time.time()

        temp_raw = OUTPUT_DIR / f"{v_id}_raw.mp3"
        out_wav = OUTPUT_DIR / f"{v_id}.wav"
        out_mp3 = OUTPUT_DIR / f"{v_id}.mp3"

        success = False
        if v["category"] == "elevenlabs":
            success = synthesize_elevenlabs(v, temp_raw)
        elif v["category"] == "edge_tts":
            success = synthesize_edge_tts(v, temp_raw)

        if not success or not temp_raw.exists():
            print(f"   ❌ Synthesis failed for {v_name}")
            continue

        # Apply mastering
        metrics = master_audio(temp_raw, out_wav, out_mp3)
        if temp_raw.exists():
            temp_raw.unlink()

        elapsed = time.time() - t0
        print(f"   ✅ Mastered in {elapsed:.1f}s | Duration: {metrics['duration']}s | Peak: {metrics['peak_db']} dB")

        results.append({
            "candidate": idx,
            "id": v_id,
            "name": v_name,
            "voice_id": v["voice_id"],
            "archetype": v["archetype"],
            "engine": v["category"],
            "duration": metrics["duration"],
            "peak_db": metrics["peak_db"],
            "mean_db": metrics["mean_db"],
            "wav_path": str(out_wav),
            "mp3_path": str(out_mp3),
        })

    # Save audition results summary JSON
    results_file = OUTPUT_DIR / "audition_results.json"
    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n✅ All auditions generated! Results recorded in {results_file}")


if __name__ == "__main__":
    main()
