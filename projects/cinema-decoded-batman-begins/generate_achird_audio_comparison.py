#!/usr/bin/env python3
"""
Cinema Decoded: Batman Begins — Achird Voice Generator Master Script
Generates and masters two audio editions:
1. With emotions (expressive, tense, visceral, dramatic modulation per beat)
2. Without emotions (steady, objective, even, clean documentary narration)
Includes EBU R128 loudness normalization (-14 LUFS) and Whisper alignment check.
"""

import os
import sys
import wave
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

from google import genai
from google.genai import types

OUTPUT_DIR = REPO_ROOT / "output" / "audio_only"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_AUDIO_DIR = Path(__file__).resolve().parent / "audio"
PROJECT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# Scripts & Prompts
# -------------------------------------------------------------------------

SCRIPT_WITH_EMOTIONS = """[intense, gripping]
Notice how Batman was not built on fearlessness, but on the very terror that broke Bruce Wayne.
[dark, haunting]
As a boy, Bruce plunged into a collapsed well where a shrieking swarm of bats scarred his mind.
[somber, reflective]
His father taught him that falling is how we learn to rise, but the trauma remained trapped in the darkness.
[disciplined, razor-sharp]
Years later, Henri Ducard forces him to face the truth: you cannot destroy fear. To master your enemy, you have to become it.
[whispering, rising in awe]
Deep inside the cave, Bruce steps directly into the bat swarm. He stops running. He rises with them.
[chilling, ruthless resolve]
When Alfred asks why bats, Bruce gives the chilling answer: "Bats frighten me. It's time my enemies shared my dread."
[triumphant, iconic authority]
He didn't eliminate his childhood weakness. He inverted it into his armor, his weapon, and his permanent identity."""

PROMPT_WITH_EMOTIONS = f"""You are a master cinematic film essayist and dramatic voice actor.
Read the following script aloud using deep dramatic range, tension, and vivid vocal emotion.
Follow the bracketed emotional directions closely to color your tone, cadence, intensity, and pitch.
IMPORTANT: DO NOT say the bracketed directions aloud. Only speak the narrative words.

{SCRIPT_WITH_EMOTIONS}
"""

SCRIPT_WITHOUT_EMOTIONS = """Notice how Batman was not built on fearlessness, but on the very terror that broke Bruce Wayne.
As a boy, Bruce plunged into a collapsed well where a shrieking swarm of bats scarred his mind.
His father taught him that falling is how we learn to rise, but the trauma remained trapped in the darkness.
Years later, Henri Ducard forces him to face the truth: you cannot destroy fear. To master your enemy, you have to become it.
Deep inside the cave, Bruce steps directly into the bat swarm. He stops running. He rises with them.
When Alfred asks why bats, Bruce gives the chilling answer: "Bats frighten me. It's time my enemies shared my dread."
He didn't eliminate his childhood weakness. He inverted it into his armor, his weapon, and his permanent identity."""

PROMPT_WITHOUT_EMOTIONS = f"""Read aloud verbatim in a steady, even, neutral documentary voice:
{SCRIPT_WITHOUT_EMOTIONS}
"""

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)

def synthesize_achird_if_needed(prompt: str, raw_wav_path: str, temperature: float = 0.85):
    if os.path.exists(raw_wav_path) and os.path.getsize(raw_wav_path) > 100000:
        print(f"✅ Raw audio already exists: {raw_wav_path} ({os.path.getsize(raw_wav_path)} bytes)")
        return

    client = get_client()
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    ]
    config = types.GenerateContentConfig(
        temperature=temperature,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Achird")
            )
        )
    )

    print(f"[Gemini TTS] Requesting Achird voice (Temp: {temperature})...")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=contents,
        config=config
    )
    if resp.candidates and resp.candidates[0].content.parts:
        raw_data = resp.candidates[0].content.parts[0].inline_data.data
        os.makedirs(os.path.dirname(raw_wav_path), exist_ok=True)
        with wave.open(raw_wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(raw_data)
        print(f"✅ Generated raw audio ({len(raw_data)} bytes): {raw_wav_path}")
    else:
        raise RuntimeError("Gemini TTS response had no audio parts.")

def master_audio(input_wav: str, output_wav: str, output_mp3: str):
    """Normalize loudness to EBU R128 broadcast standard (-14 LUFS) and export WAV and MP3."""
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    os.makedirs(os.path.dirname(output_mp3), exist_ok=True)

    # Master WAV
    cmd_wav = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", input_wav,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "24000",
        "-c:a", "pcm_s16le",
        output_wav
    ]
    subprocess.run(cmd_wav, check=True)

    # Master MP3 (high-quality 320k)
    cmd_mp3 = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", output_wav,
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        output_mp3
    ]
    subprocess.run(cmd_mp3, check=True)

def get_audio_info(file_path: str):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate",
        "-of", "json",
        file_path
    ]
    data = json.loads(subprocess.check_output(cmd).decode())["format"]
    dur = float(data["duration"])
    size_mb = float(data["size"]) / (1024 * 1024)
    kbps = int(data.get("bit_rate", 0)) // 1000
    return {"duration": dur, "size_mb": size_mb, "kbps": kbps}

def transcribe_audio(audio_path: str):
    import numpy as np
    from faster_whisper import WhisperModel

    cmd = ['ffmpeg', '-v', 'quiet', '-i', audio_path, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    audio_np = np.frombuffer(proc.stdout, np.int16).flatten().astype(np.float32) / 32768.0

    model = WhisperModel('base', device='cpu', compute_type='int8')
    segments, _ = model.transcribe(audio_np)
    lines = []
    for s in segments:
        lines.append(f"[{s.start:5.2f}s - {s.end:5.2f}s] {s.text.strip()}")
    return "\n".join(lines)

def main():
    print("======================================================================")
    print("🎙️ GEMINI ACHIRD VOICE: WITH EMOTIONS VS. WITHOUT EMOTIONS")
    print("======================================================================\n")

    # 1. WITH EMOTIONS
    print("--- STEP 1: Audio WITH Emotions ---")
    raw_with = str(OUTPUT_DIR / "batman_begins_achird_with_emotions_raw.wav")
    master_with_wav = str(OUTPUT_DIR / "batman_begins_achird_with_emotions.wav")
    master_with_mp3 = str(OUTPUT_DIR / "batman_begins_achird_with_emotions.mp3")

    synthesize_achird_if_needed(PROMPT_WITH_EMOTIONS, raw_with, temperature=0.90)
    master_audio(raw_with, master_with_wav, master_with_mp3)

    # Copy to project audio dir
    subprocess.run(["cp", master_with_wav, str(PROJECT_AUDIO_DIR / "batman_begins_achird_with_emotions.wav")], check=True)
    subprocess.run(["cp", master_with_mp3, str(PROJECT_AUDIO_DIR / "batman_begins_achird_with_emotions.mp3")], check=True)

    info_with = get_audio_info(master_with_mp3)
    print(f"✅ Audio WITH Emotions: {info_with['duration']:.2f}s | {info_with['size_mb']:.2f} MB")

    # 2. WITHOUT EMOTIONS
    print("\n--- STEP 2: Audio WITHOUT Emotions ---")
    raw_without = str(OUTPUT_DIR / "batman_begins_achird_without_emotions_raw.wav")
    master_without_wav = str(OUTPUT_DIR / "batman_begins_achird_without_emotions.wav")
    master_without_mp3 = str(OUTPUT_DIR / "batman_begins_achird_without_emotions.mp3")

    synthesize_achird_if_needed(PROMPT_WITHOUT_EMOTIONS, raw_without, temperature=0.80)
    master_audio(raw_without, master_without_wav, master_without_mp3)

    # Copy to project audio dir
    subprocess.run(["cp", master_without_wav, str(PROJECT_AUDIO_DIR / "batman_begins_achird_without_emotions.wav")], check=True)
    subprocess.run(["cp", master_without_mp3, str(PROJECT_AUDIO_DIR / "batman_begins_achird_without_emotions.mp3")], check=True)

    info_without = get_audio_info(master_without_mp3)
    print(f"✅ Audio WITHOUT Emotions: {info_without['duration']:.2f}s | {info_without['size_mb']:.2f} MB")

    # 3. Transcribe both to verify quality and confirm bracket tags weren't spoken
    print("\n--- STEP 3: Whisper Quality Verification ---")
    print("\n[Transcription: WITH Emotions]")
    transcript_with = transcribe_audio(master_with_wav)
    print(transcript_with)

    print("\n[Transcription: WITHOUT Emotions]")
    transcript_without = transcribe_audio(master_without_wav)
    print(transcript_without)

    # Save transcripts
    (OUTPUT_DIR / "transcript_with_emotions.txt").write_text(transcript_with, encoding="utf-8")
    (OUTPUT_DIR / "transcript_without_emotions.txt").write_text(transcript_without, encoding="utf-8")

    print("\n======================================================================")
    print("DELIVERABLES SUMMARY (Achird Voice Generator):")
    print("----------------------------------------------------------------------")
    print("1. WITH EMOTIONS:")
    print(f"   - MP3 (320 kbps): {master_with_mp3}")
    print(f"   - WAV (24 kHz Studio): {master_with_wav}")
    print(f"   - Duration: {info_with['duration']:.2f}s | Normalization: EBU R128 (-14 LUFS)")
    print("2. WITHOUT EMOTIONS:")
    print(f"   - MP3 (320 kbps): {master_without_mp3}")
    print(f"   - WAV (24 kHz Studio): {master_without_wav}")
    print(f"   - Duration: {info_without['duration']:.2f}s | Normalization: EBU R128 (-14 LUFS)")
    print("======================================================================")

if __name__ == "__main__":
    main()
