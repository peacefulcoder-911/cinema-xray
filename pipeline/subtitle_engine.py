import os
import json
import re
from datetime import timedelta
from google import genai
def _load_env():
    p = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"").strip("\x27"))
_load_env()

def format_ass_time(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    centis = int(round((td.total_seconds() - int(td.total_seconds())) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_timed_subtitles(audio_path: str, script_text: str, total_duration: float, cache_json_path: str = None) -> list:
    """Uses Gemini to transcribe exact phrase timestamps for high-retention subtitle cards."""
    if cache_json_path and os.path.exists(cache_json_path) and os.path.getsize(cache_json_path) > 10:
        try:
            with open(cache_json_path, "r", encoding="utf-8") as f:
                cards = json.load(f)
                if cards and len(cards) > 5:
                    print(f"✅ Loaded cached subtitle timing cards ({len(cards)} cards)")
                    return cards
        except Exception:
            pass

    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k")
    client = genai.Client(api_key=api_key)
    
    print("Uploading audio to Gemini for speech-alignment...")
    uploaded = client.files.upload(file=audio_path)

    prompt = f"""Listen carefully to this audio file (total duration: {total_duration:.2f} seconds).
The transcript is:
"{script_text}"

Return a JSON array of rapid subtitle cards (2 to 4 words per card max) with exact start and end timestamps in seconds.
Select one punchy keyword in each card for 'highlight'.

Output JSON format strictly:
[
  {{"start": 0.00, "end": 1.40, "text": "IN AGE OF ULTRON,", "highlight": "ULTRON"}},
  ...
]
Return ONLY raw JSON, no markdown codeblocks."""

    try:
        resp = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[uploaded, prompt]
        )
        raw_text = resp.text.strip()
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-z]*\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)
        cards = json.loads(raw_text)
        if cache_json_path:
            with open(cache_json_path, "w", encoding="utf-8") as f:
                json.dump(cards, f, indent=2)
        return cards
    except Exception as e:
        print(f"Gemini subtitle alignment fallback: {e}")
        # Proportional fallback
        words = script_text.upper().split()
        chunk_size = 3
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        time_per_chunk = total_duration / max(len(chunks), 1)
        cards = []
        for idx, ch in enumerate(chunks):
            start = idx * time_per_chunk
            end = min((idx + 1) * time_per_chunk, total_duration)
            cards.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "text": " ".join(ch),
                "highlight": ch[-1] if ch else ""
            })
        if cache_json_path:
            with open(cache_json_path, "w", encoding="utf-8") as f:
                json.dump(cards, f, indent=2)
        return cards

def build_ass_subtitles(cards: list, output_ass_path: str):
    """Creates a Center Bold Stroke ASS subtitle file."""
    # Alignment 5 = Middle Center
    # Font: Arial Black, Size 76, Outline 10, Shadow 4
    ass_template = """[Script Info]
Title: Cinema X-Ray Center Bold Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterBold,Arial Black,76,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,10,4,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for item in cards:
        start_str = format_ass_time(item["start"])
        end_str = format_ass_time(item["end"])
        raw_text = item["text"].upper()
        highlight_word = item.get("highlight", "").upper().strip(",.!?\"'")

        if highlight_word and highlight_word in raw_text:
            # Highlight with electric gold
            colored_word = f"{{\\c&H0000E5FF&}}{highlight_word}{{\\c&H00FFFFFF&}}"
            styled_text = raw_text.replace(highlight_word, colored_word, 1)
        else:
            styled_text = raw_text

        events.append(f"Dialogue: 0,{start_str},{end_str},CenterBold,,0,0,0,,{styled_text}")

    full_ass = ass_template + "\n".join(events) + "\n"
    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(full_ass)
    print(f"✅ Center Bold subtitles generated: {output_ass_path}")
    return output_ass_path
