#!/usr/bin/env python3
"""
Cinema Decoded: Interstellar Ticking Clock — Voice Synthesis & Whisper Alignment
Synthesizes native fast Achird voiceover via Gemini TTS and generates word timestamps.
"""

import os
import sys
import wave
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

from google import genai
from google.genai import types

PROJECT_DIR = Path(__file__).resolve().parent
SCRATCH_DIR = PROJECT_DIR / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

SCRIPT_TEXT = """Listen closely to the soundtrack on Miller's planet.
Every single tick you hear in Hans Zimmer's score is exactly 1.25 seconds apart.
That is not a random tempo.
Because of Gargantua's extreme gravity, one hour on this planet equals seven years on Earth.
If you do the math, exactly 1.25 seconds equals an entire Earth day passing by.
With every single click of the clock, Cooper is losing another full day of his daughter's life.
By the time they escape the mountain wave and return to the ship, twenty-three years, four months, and eight days have vanished.
The ticking was never just music.
It was a countdown of Cooper's lost parenthood."""

PROMPT = f"""Read the following script in a fast, brisk, energetic, neutral documentary voice.
No dramatic pauses, no theatrical acting, and zero dead air between sentences.
Deliver each sentence smoothly with brisk pacing and flat, objective confidence:

{SCRIPT_TEXT}"""

def main():
    print("======================================================================")
    print("🎙️ GENERATING INTERSTELLAR TICKING CLOCK NARRATION (ACHIRD VOICE)")
    print("======================================================================")

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=PROMPT)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=0.80,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Achird")
            )
        )
    )

    raw_wav = str(SCRATCH_DIR / "raw_achird.wav")
    print("[Gemini TTS] Requesting Achird voice generation...")
    resp = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=contents,
        config=config
    )

    if not resp.candidates or not resp.candidates[0].content.parts:
        raise RuntimeError("No audio returned from Gemini TTS")

    raw_data = resp.candidates[0].content.parts[0].inline_data.data
    with wave.open(raw_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(raw_data)

    print(f"✅ Raw audio generated: {raw_wav} ({len(raw_data)} bytes)")

    # Loudness normalization to -14 LUFS
    norm_wav = str(SCRATCH_DIR / "voice_normalized.wav")
    cmd_norm = [
        "ffmpeg", "-y", "-v", "quiet",
        "-i", raw_wav,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "24000",
        norm_wav
    ]
    subprocess.run(cmd_norm, check=True)

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", norm_wav]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    print(f"✅ Voice normalized: {dur:.2f}s")

    # Word-level Whisper timestamps
    print("\n[Whisper] Extracting millisecond-accurate word timestamps...")
    import numpy as np
    from faster_whisper import WhisperModel

    pcm_cmd = ["ffmpeg", "-v", "quiet", "-i", norm_wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    proc = subprocess.run(pcm_cmd, stdout=subprocess.PIPE, check=True)
    audio_np = np.frombuffer(proc.stdout, np.int16).flatten().astype(np.float32) / 32768.0

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_np, word_timestamps=True)

    words = []
    for s in segments:
        for w in s.words:
            wt = w.word.strip()
            if wt:
                words.append({"word": wt, "start": round(w.start, 2), "end": round(w.end, 2)})

    words_file = SCRATCH_DIR / "words.json"
    words_file.write_text(json.dumps(words, indent=2), encoding="utf-8")
    print(f"✅ Extracted {len(words)} words saved to {words_file}")

    for s in segments:
        print(f"[{s.start:5.2f}s - {s.end:5.2f}s] {s.text}")

if __name__ == "__main__":
    main()

