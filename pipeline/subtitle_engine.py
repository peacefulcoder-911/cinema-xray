import os
import json
import re
import subprocess
from datetime import timedelta
from pathlib import Path

def _load_env():
    p = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_env()

def format_ass_time(seconds: float) -> str:
    td = timedelta(seconds=float(seconds))
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    centis = int(round((td.total_seconds() - int(td.total_seconds())) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def align_with_whisper(audio_path: str, script_text: str) -> list:
    """Performs millisecond-accurate forced speech alignment using faster-whisper and ffmpeg."""
    import numpy as np
    from faster_whisper import WhisperModel

    # 1. Detect exact initial speech onset via ffmpeg silence detection
    sil_cmd = ['ffmpeg', '-i', audio_path, '-af', 'silencedetect=noise=-28dB:d=0.15', '-f', 'null', '-']
    sil_res = subprocess.run(sil_cmd, stderr=subprocess.PIPE, text=True)
    first_sound = 0.0
    for line in sil_res.stderr.splitlines():
        if 'silence_end:' in line:
            m = re.search(r'silence_end:\s*([0-9.]+)', line)
            if m:
                first_sound = float(m.group(1))
                break

    # 2. Decode audio to 16kHz mono PCM s16le via ffmpeg pipe (bypasses PyAV metadata bug)
    cmd = ['ffmpeg', '-v', 'quiet', '-i', audio_path, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    audio_np = np.frombuffer(proc.stdout, np.int16).flatten().astype(np.float32) / 32768.0

    print("🎙️  Running faster-whisper acoustic word alignment...")
    model = WhisperModel('base', device='cpu', compute_type='int8')
    segments, info = model.transcribe(audio_np, word_timestamps=True, initial_prompt=script_text)

    words = []
    for segment in segments:
        for word in segment.words:
            w = word.word.strip()
            if w:
                words.append({
                    'word': w,
                    'start': float(round(word.start, 2)),
                    'end': float(round(word.end, 2))
                })

    if not words:
        return []

    # Clamp first word start to actual sound onset so no premature display
    if words[0]['start'] < first_sound:
        words[0]['start'] = float(round(first_sound, 2))

    # 3. Group words into high-retention rapid cards (2-3 words)
    # Break strictly on pauses (>=0.18s), punctuation, or max duration
    cards_words = []
    current = []

    def should_break(curr, next_w, gap):
        if not curr:
            return False
        if gap >= 0.18:
            return True
        last_w = curr[-1]['word']
        if any(last_w.endswith(p) for p in ['.', '?', '!']):
            return True
        if any(last_w.endswith(p) for p in [',', ';']) and len(curr) >= 2:
            return True
        if len(curr) >= 3:
            return True
        dur = curr[-1]['end'] - curr[0]['start']
        if dur >= 1.25:
            return True
        return False

    for i, w in enumerate(words):
        current.append(w)
        gap = 0.0
        if i + 1 < len(words):
            gap = words[i+1]['start'] - w['end']
        next_w = words[i+1] if i + 1 < len(words) else None
        if should_break(current, next_w, gap):
            cards_words.append(current)
            current = []

    if current:
        cards_words.append(current)

    # 4. Refine cards: merge tiny 1-word orphan fragments (<0.35s) into previous card
    refined = []
    for cw in cards_words:
        if len(cw) == 1 and refined:
            prev = refined[-1]
            gap = cw[0]['start'] - prev[-1]['end']
            dur = cw[0]['end'] - cw[0]['start']
            if dur < 0.35 or gap < 0.15:
                refined[-1].extend(cw)
                continue
        refined.append(cw)

    # 5. Format cards with timing & punchy keyword highlight
    stop_words = {'IN', 'OF', 'THE', 'AND', 'OR', 'IF', 'HE', 'IT', 'TO', 'WAS', 'ON', 'A', 'AN', 'THAT', 'BE', 'AS', 'IS', 'AT', 'BY', 'WITH', 'FOR', 'DID'}
    cards = []
    for cw in refined:
        text = ' '.join([x['word'] for x in cw]).upper()
        clean_words = [re.sub(r'[^A-Z0-9]', '', x['word'].upper()) for x in cw]
        meaningful = [w for w in clean_words if w not in stop_words]
        hl = max(meaningful, key=len) if meaningful else (max(clean_words, key=len) if clean_words else '')
        cards.append({
            'start': float(cw[0]['start']),
            'end': float(cw[-1]['end']),
            'text': text,
            'highlight': hl
        })

    print(f"✅ Acoustic alignment complete: {len(cards)} precision subtitle cards generated.")
    return cards

def generate_timed_subtitles(audio_path: str, script_text: str, total_duration: float, cache_json_path: str = None, force_refresh: bool = True) -> list:
    """Generates subtitle cards strictly aligned to vocal cadence with instant pause clearance."""
    if not force_refresh and cache_json_path and os.path.exists(cache_json_path) and os.path.getsize(cache_json_path) > 10:
        try:
            with open(cache_json_path, "r", encoding="utf-8") as f:
                cards = json.load(f)
                if cards and len(cards) > 5:
                    print(f"✅ Loaded cached subtitle timing cards ({len(cards)} cards)")
                    return cards
        except Exception:
            pass

    # Method 1: Try faster-whisper acoustic forced alignment
    try:
        cards = align_with_whisper(audio_path, script_text)
        if cards and len(cards) > 10:
            if cache_json_path:
                with open(cache_json_path, "w", encoding="utf-8") as f:
                    json.dump(cards, f, indent=2)
            return cards
    except Exception as e:
        print(f"⚠️ Whisper alignment failed or not available: {e}")

    # Method 2: Gemini 3.8-flash forced alignment
    try:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k")
        client = genai.Client(api_key=api_key)
        print("Uploading audio to Gemini 3.8-flash for acoustic alignment...")
        uploaded = client.files.upload(file=audio_path)
        prompt = f"""Listen to this audio ({total_duration:.2f}s). Script: '{script_text}'.
Return a raw JSON array of rapid subtitle cards (2-3 words per card).
Format:
[
  {{"start": 0.29, "end": 1.12, "text": "IN AGE OF ULTRON,", "highlight": "ULTRON"}}
]
DO NOT linger during pauses. Subtitle must disappear when phrase ends. Return ONLY raw JSON."""
        resp = client.models.generate_content(model="gemini-3.8-flash", contents=[uploaded, prompt])
        raw_text = resp.text.strip()
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-z]*\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)
        cards = json.loads(raw_text)
        if cache_json_path:
            with open(cache_json_path, "w", encoding="utf-8") as f:
                json.dump(cards, f, indent=2)
        return cards
    except Exception as e2:
        print(f"⚠️ Gemini fallback failed: {e2}")

    # Method 3: Proportional fallback
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
    """Creates a Center Bold Stroke ASS subtitle file with rapid-fire visibility and pause clearance."""
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
