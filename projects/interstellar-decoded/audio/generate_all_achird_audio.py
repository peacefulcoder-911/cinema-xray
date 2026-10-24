import os
import json
import wave
import time
from google import genai
from google.genai import types

env_path = "/Users/vinaybt/Downloads/interstellar-decoded/.env"
for line in open(env_path):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ[k] = v

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

script_json_path = "/Users/vinaybt/Downloads/interstellar-decoded/script/interstellar_script.json"
with open(script_json_path) as f:
    chapters = json.load(f)

audio_dir = "/Users/vinaybt/Downloads/interstellar-decoded/audio"
os.makedirs(audio_dir, exist_ok=True)

for ch in chapters:
    cid = ch["id"]
    out_wav = os.path.join(audio_dir, f"{cid}_achird.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 10000:
        print(f"Skipping {cid}, already exists: {out_wav}")
        continue

    print(f"\n--- Generating Achird Audio for: {ch['title']} ---")
    prompt_content = f"""Read the following narration for a high-end cinematic video essay.

# Audio Profile
A calm, intellectually compelling, cinematic science communicator and video essayist. 
Delivery is grounded, clear, deeply observant, and authoritative. 
Tone: Serious, fascinated by the universe, never rushed. Allow words room to breathe.
Accent: American (General).

# Director's Note
{ch['director_note']}

## Narration:
{ch['script']}
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_content)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=0.6,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Achird")
            )
        )
    )

    try:
        resp = client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=contents,
            config=config
        )

        part = resp.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            raw_data = part.inline_data.data
            with wave.open(out_wav, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(raw_data)
            print(f"✅ Generated {out_wav} ({len(raw_data)} bytes)")
        else:
            print(f"❌ Failed to get inline audio for {cid}")
    except Exception as e:
        print(f"❌ Error generating {cid}: {e}")

    time.sleep(1.0)

print("\nAll Achird chapter audio generations complete!")
