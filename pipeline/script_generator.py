import os
import json
import re
from google import genai

def _load_env():
    p = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_env()

def generate_cinematic_script(topic: str = None) -> dict:
    """
    Generates a high-retention, intellectually compelling Cinema X-Ray script (40-55 seconds).
    Follows the 4-part viral cinema essay framework:
    1. The Observable Detail / Anomaly (0-8s)
    2. The Central Question / Paradox (8-16s)
    3. The Narrative Rule / Lore Investigation (16-35s)
    4. The Mind-Bending Realization / Emotional Payoff (35-50s)
    """
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k")
    client = genai.Client(api_key=api_key)

    if not topic:
        topic = "A hidden detail or character decision in a major blockbuster that changes the entire meaning of the movie"

    system_prompt = """You are the master lead writer for 'Cinema X-Ray', the #1 viral movie analysis and film explainer channel.
Your scripts are fast-paced, highly analytical, sharp, respectful of lore, and psychologically deep.
Never use generic filler like 'Hey guys welcome back' or 'Like and subscribe'. Start immediately with the visual anomaly.
The narration must take exactly 40 to 50 seconds when spoken at 150 words per minute (around 110-130 words total)."""

    user_prompt = f"""Topic: {topic}

Generate a Cinema X-Ray script. Return strictly a JSON object:
{{
  "title": "Short punchy episode title",
  "hook": "Opening hook sentence",
  "script": "Full continuous narration text for voiceover (110-130 words)",
  "visual_cues": [
    {{"time_est": "0-10s", "shot": "Description of matching movie visual"}},
    {{"time_est": "10-25s", "shot": "Description of matching movie visual"}},
    {{"time_est": "25-45s", "shot": "Description of matching movie visual"}}
  ]
}}
Return ONLY valid raw JSON."""

    resp = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[system_prompt, user_prompt]
    )
    raw = resp.text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n", "", raw)
        raw = re.sub(r"\n```$", "", raw)
    data = json.loads(raw)
    return data

if __name__ == "__main__":
    res = generate_cinematic_script("The Dark Knight hospital explosion scene detail")
    print("Generated Title:", res.get("title"))
    print("Script Preview:", res.get("script")[:100])
