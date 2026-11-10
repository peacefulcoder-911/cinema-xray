#!/usr/bin/env python3
import json
from pathlib import Path

cards_data = [
    # sec1_hook (0.20s - 6.70s)
    {"start": 0.20, "end": 1.40, "text": "THERE'S A SMALL DETAIL", "highlight": "SMALL"},
    {"start": 1.40, "end": 2.50, "text": "IN DOCTOR STRANGE", "highlight": "STRANGE"},
    {"start": 2.50, "end": 3.70, "text": "THAT REVEALS HOW MUCH", "highlight": "REVEALS"},
    {"start": 3.80, "end": 5.10, "text": "STEPHEN STRANGE", "highlight": "STRANGE"},
    {"start": 5.10, "end": 6.40, "text": "LOST.", "highlight": "LOST"},
    # Pause 6.40 - 8.50
    # sec2_engraving (8.50s - 15.14s)
    {"start": 8.50, "end": 9.50, "text": "BEFORE HIS ACCIDENT,", "highlight": "ACCIDENT"},
    {"start": 9.50, "end": 10.50, "text": "CHRISTINE GIVES STEPHEN", "highlight": "STEPHEN"},
    {"start": 10.50, "end": 11.40, "text": "A WATCH.", "highlight": "WATCH"},
    {"start": 11.40, "end": 12.30, "text": "BUT LOOK CLOSELY", "highlight": "CLOSELY"},
    {"start": 12.30, "end": 13.10, "text": "AT ITS ENGRAVING.", "highlight": "ENGRAVING"},
    {"start": 13.10, "end": 13.90, "text": "IT SAYS, 'TIME WILL TELL", "highlight": "TIME"},
    {"start": 13.90, "end": 14.90, "text": "HOW MUCH I LOVE YOU.'", "highlight": "LOVE"},
    # Pause 14.90 - 17.34
    # sec3_crash (17.34s - 26.82s)
    {"start": 17.34, "end": 18.40, "text": "AT FIRST, IT SEEMS LIKE", "highlight": "SEEMS"},
    {"start": 18.40, "end": 19.40, "text": "A ROMANTIC GIFT.", "highlight": "ROMANTIC"},
    {"start": 19.40, "end": 20.60, "text": "THEN STEPHEN'S ACCIDENT", "highlight": "ACCIDENT"},
    {"start": 20.60, "end": 21.80, "text": "DESTROYS THE LIFE", "highlight": "DESTROYS"},
    {"start": 21.80, "end": 22.90, "text": "HE BUILT AROUND HIS HANDS.", "highlight": "HANDS"},
    {"start": 22.90, "end": 24.10, "text": "HIS CAREER DISAPPEARS.", "highlight": "DISAPPEARS"},
    {"start": 24.10, "end": 25.20, "text": "HIS CONFIDENCE COLLAPSES.", "highlight": "COLLAPSES"},
    {"start": 25.20, "end": 26.40, "text": "AND HIS RELATIONSHIP WITH CHRISTINE", "highlight": "CHRISTINE"},
    {"start": 26.40, "end": 27.20, "text": "BEGINS TO FALL APART.", "highlight": "APART"},
    # Pause 27.20 - 28.82
    # sec4_broken_watch (28.82s - 33.27s)
    {"start": 28.82, "end": 29.80, "text": "BUT HE KEEPS THAT", "highlight": "KEEPS"},
    {"start": 29.80, "end": 30.80, "text": "BROKEN WATCH.", "highlight": "BROKEN"},
    {"start": 30.80, "end": 31.90, "text": "EVEN AFTER EVERYTHING CHANGES,", "highlight": "CHANGES"},
    {"start": 31.90, "end": 33.10, "text": "HE REFUSES TO LET IT GO.", "highlight": "REFUSES"},
    # Pause 33.10 - 35.47
    # sec5_payoff (35.47s - 45.83s)
    {"start": 35.47, "end": 36.70, "text": "THE WATCH BECOMES A REMINDER", "highlight": "REMINDER"},
    {"start": 36.70, "end": 37.90, "text": "OF THE PERSON HE WAS,", "highlight": "PERSON"},
    {"start": 37.90, "end": 39.10, "text": "THE PERSON HE LOST,", "highlight": "LOST"},
    {"start": 39.10, "end": 40.40, "text": "AND THE LOVE HE COULDN'T", "highlight": "LOVE"},
    {"start": 40.40, "end": 41.40, "text": "HOLD ON TO.", "highlight": "HOLD"},
    {"start": 41.40, "end": 42.80, "text": "IN A MOVIE ABOUT CONTROLLING TIME,", "highlight": "TIME"},
    {"start": 42.80, "end": 44.20, "text": "THE MOST IMPORTANT THING STEPHEN", "highlight": "IMPORTANT"},
    {"start": 44.20, "end": 45.70, "text": "CANNOT REPAIR IS HIS OWN PAST.", "highlight": "REPAIR"}
]

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

header = """[Script Info]
Title: Cinema Decoded Arc Reactor Cyan HUD Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ArcReactorCyanHUD,Futura,74,&H00FFFFFF,&H000000FF,&H000A0A0A,&H80000000,-1,0,0,0,100,100,3,0,1,8,3,2,60,60,360,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
CYAN_TAG = "{\\c&H00FFFF00&}"
WHITE_TAG = "{\\c&H00FFFFFF&}"

for c in cards_data:
    st = format_ass_time(c['start'])
    et = format_ass_time(c['end'])
    txt = c['text']
    hl = c['highlight']
    if hl and hl in txt:
        hl_ass = f"{CYAN_TAG}{hl}{WHITE_TAG}"
        styled_text = txt.replace(hl, hl_ass, 1)
    else:
        styled_text = txt
    events.append(f"Dialogue: 0,{st},{et},ArcReactorCyanHUD,,0,0,0,,{styled_text}")

ass_content = header + "\n".join(events) + "\n"

repo_root = Path(__file__).resolve().parent.parent
p1 = repo_root / "projects" / "cinema-decoded-doctor-strange-watch" / "subtitles.ass"
p2 = repo_root / "doctor-strange-breakdown" / "subtitles.ass"
p1.write_text(ass_content, encoding="utf-8")
p2.write_text(ass_content, encoding="utf-8")

j1 = repo_root / "projects" / "cinema-decoded-doctor-strange-watch" / "subtitles.json"
j2 = repo_root / "doctor-strange-breakdown" / "subtitles.json"
j1.write_text(json.dumps(cards_data, indent=2), encoding="utf-8")
j2.write_text(json.dumps(cards_data, indent=2), encoding="utf-8")

print("Subtitles successfully generated and written to project paths!")

