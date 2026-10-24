import os
import wave
from google import genai
from google.genai import types

def generate():
    env_path = "/Users/vinaybt/Downloads/marvel-decoded/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

    api_key = os.environ.get("GEMINI_API_KEY")
    default_key = "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k"
    if not api_key or not api_key.startswith("AIza"):
        api_key = default_key

    client = genai.Client(api_key=api_key)
    model = "gemini-3.1-flash-tts-preview"

    script_text = (
        "In Age of Ultron, Captain America moves Thor's hammer an inch, then immediately stops. "
        "Five years later in Endgame, Mjolnir flies straight into his hand. "
        "Why couldn't he lift it before? He could. "
        "Psychologists call it Status Preservation. "
        "The second Mjolnir budged, Steve saw the panic in Thor's eyes. "
        "Lifting it would have publicly humiliated the God of Thunder in front of his team. "
        "So Steve let go. "
        "In Endgame, Thor was seconds from dying. Ego didn't matter anymore. "
        "True worthiness was never about flexing power. "
        "It was knowing when to hold back."
    )

    # Clean text to single seamless line with no artificial linebreaks
    transcript_text = " ".join(script_text.split())

    # Exact fast energetic prompt from "The Day Caveman Discovered Fire"
    prompt_content = f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
A young, casual YouTube storyteller. The voice is completely effortless, slightly dry, and relaxed. Zero pressure, no dramatic acting, just a smooth, natural speaking voice.

# Director's note
Style: Flat affect, minimal pitch variation, dry delivery. Pace: Fast, energetic, no dead air. Sentences overlap slightly. Accent: American (General).

## Scene:
A casual bedroom studio. A young guy is calmly explaining a cool history topic to his audience with a relaxed, dry delivery.

## Sample Context:
Smooth, modern YouTube essay style. The delivery is extremely casual, flat, and effortless. The speaker drops all theatrical pressure and just talks normally, like a real person having a calm conversation.

## Transcript:
{transcript_text}"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_content)],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.9,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Achird"
                )
            )
        ),
    )

    print("Generating fast voiceover with Gemini Achird...")
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    part = response.candidates[0].content.parts[0]
    if part.inline_data and part.inline_data.data:
        raw_audio = part.inline_data.data
        out_wav = "/Users/vinaybt/Downloads/marvel-decoded/audio/voiceover_fast.wav"
        with wave.open(out_wav, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(raw_audio)

        frames = len(raw_audio) // 2
        dur = frames / 24000.0
        print(f"Success! Fast voiceover saved to: {out_wav}")
        print(f"Duration: {dur:.2f} seconds")
        return out_wav, dur
    else:
        raise RuntimeError("No audio data returned")

if __name__ == "__main__":
    generate()
