import os
import wave
import sys
from google import genai
from google.genai import types
def _load_env():
    p = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"").strip("\x27"))
_load_env()

def generate_achird_audio(script_text: str, output_path: str) -> float:
    """Generates studio-quality Achird voiceover using Gemini TTS."""
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k")
    
    # If audio already generated and valid, return duration directly
    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        try:
            with wave.open(output_path, "rb") as wf:
                dur = wf.getnframes() / float(wf.getframerate())
                print(f"✅ Reusing existing voiceover: {output_path} ({dur:.2f}s)")
                return dur
        except Exception:
            pass

    client = genai.Client(api_key=api_key)
    model = "gemini-3.1-flash-tts-preview"

    prompt_content = f"""Read the following narration for a high-end Cinema X-Ray video essay.

# Audio Profile
A calm, authoritative, intellectually compelling cinematic storyteller and film analyst.
Delivery is grounded, clear, deeply observant, and charismatic. Zero theatrical pressure, just natural brilliance.
Tone: Fascinated by cinematic details, serious, fast-paced without dead air.
Accent: American (General).

## Script:
{script_text}"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_content)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=0.85,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Achird")
            )
        )
    )

    print(f"Connecting to Gemini TTS (Achird)...")
    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

    if not resp.candidates:
        raise RuntimeError("No candidates returned from Gemini TTS.")

    part = resp.candidates[0].content.parts[0]
    if part.inline_data and part.inline_data.data:
        raw_data = part.inline_data.data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(raw_data)
        
        frames = len(raw_data) // 2
        duration = frames / 24000.0
        print(f"✅ Audio generated: {output_path} ({duration:.2f}s)")
        return duration
    else:
        raise RuntimeError("No inline audio data returned.")

if __name__ == "__main__":
    test_script = "In Age of Ultron, when Steve Rogers barely nudged Thor's hammer, Thor's smile instantly vanished."
    generate_achird_audio(test_script, "/tmp/test_achird.wav")
