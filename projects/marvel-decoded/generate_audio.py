import os
import wave
from google import genai
from google.genai import types

def generate_voiceover():
    # 1. Load .env
    env_path = "/Users/vinaybt/Downloads/marvel-decoded/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment.")

    client = genai.Client(api_key=api_key)

    script_text = """In Age of Ultron, Captain America pulls Thor's hammer, moves it an inch... and immediately gives up.
Five years later in Endgame, Mjolnir flies straight into his hand.

Did Steve suddenly become worthy? No. He was always worthy.

Psychologists call this Status Preservation: the deliberate choice to downplay your ability to protect someone else's identity.

Look closely at the party scene.
The exact millisecond Mjolnir budges, Steve sees the panic in Thor's eyes.
Lifting that hammer wouldn't just prove Steve's strength. It would destroy Thor's entire sense of self in front of his team.
So Steve lets go.

In Endgame, there's no ego left to protect.
Thor is seconds away from being killed.
The hammer didn't answer Steve because he finally became strong enough.
It answered because true worthiness isn't showing your power.
It's knowing when to hold back."""

    # Save the script text
    script_file = "/Users/vinaybt/Downloads/marvel-decoded/script/marvel_decoded_script.md"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write("# Marvel Decoded: Why Captain America Was Always Worthy\n\n" + script_text + "\n")

    prompt_content = f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
A cinematic video essayist and cultural analyst. The delivery is confident, relaxed, and thoughtful. Not overly dramatic, but engaging and compelling, like a top YouTube video essay.

# Director's note
Style: Clear, observant, engaging, thoughtful pacing. Give slight pauses around key revelations. Accent: American (General).

## Transcript:
{script_text}
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_content)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.8,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Achird"
                )
            )
        ),
    )

    print("Generating audio with Gemini TTS (Achird)...")
    response = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=contents,
        config=generate_content_config,
    )

    part = response.candidates[0].content.parts[0]
    if part.inline_data and part.inline_data.data:
        raw_audio = part.inline_data.data
        out_wav = "/Users/vinaybt/Downloads/marvel-decoded/audio/voiceover.wav"
        with wave.open(out_wav, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(raw_audio)
        print(f"Audio generated successfully: {out_wav}")
        return out_wav
    else:
        raise Exception("Failed to retrieve audio data from Gemini.")

if __name__ == "__main__":
    generate_voiceover()
