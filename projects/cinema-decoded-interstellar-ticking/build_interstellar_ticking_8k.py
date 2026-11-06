#!/usr/bin/env python3
"""
Cinema Decoded: Interstellar — The Ticking Clock 8K Master Builder
Topic: Hans Zimmer's 1.25s Ticking Clock Countdown on Miller's Planet
Features:
- Fast Achird voice narration + synchronized 1.25s acoustic clock ticking + cosmic drone + wave roar.
- True 1080p Full HD source footage from YouTube (Paramount official clips).
- Clean 70% active cinematic canvas with dynamic blurred ambient backdrop (ZERO box text / HUD overlays).
- Center-bold kinetic ASS subtitles in the lower third.
- Direct 8K Super-Resolution (4320x7680) via Lanczos + AMD CAS sharpening (Apple Silicon hevc_videotoolbox).
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution

PROJECT_DIR = Path(__file__).resolve().parent
CLIPS_DIR = PROJECT_DIR / "clips"
SCRATCH_DIR = PROJECT_DIR / "scratch"
QC_DIR = PROJECT_DIR / "qc_frames"
OUT_DIR = PROJECT_DIR / "out"

for d in [CLIPS_DIR, SCRATCH_DIR, QC_DIR, OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

AUDIO_MASTER = PROJECT_DIR / "interstellar_ticking_mixed_audio.m4a"
ASS_PATH = PROJECT_DIR / "interstellar_subtitles.ass"

FINAL_1080P_REPO = REPO_ROOT / "output" / "cinema_xray_interstellar_ticking_1080p.mp4"
FINAL_4K_REPO = REPO_ROOT / "output" / "cinema_xray_interstellar_ticking_4k.mp4"
FINAL_8K_REPO = REPO_ROOT / "output" / "cinema_xray_interstellar_ticking_8k.mp4"

FINAL_1080P_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_interstellar_ticking_1080p.mp4"
FINAL_4K_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_interstellar_ticking_4k.mp4"
FINAL_8K_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_interstellar_ticking_8k.mp4"

THUMBNAIL_PATH = PROJECT_DIR / "thumbnail.jpg"
THUMBNAIL_OUTPUT = REPO_ROOT / "output" / "thumbnails_short" / "interstellar_ticking_thumb.jpg"

TOTAL_DUR = 36.85

def run_cmd(cmd, desc="Running command"):
    print(f"\n[RUNNING] {desc}")
    print(" ".join(cmd[:8]) + ("..." if len(cmd) > 8 else ""))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Error in {desc}:\n{res.stderr[-1000:]}")
        raise RuntimeError(f"Command failed: {desc}")
    return res

# -------------------------------------------------------------------------
# 1. Build Kinetic ASS Subtitles (NO Box Overlays)
# -------------------------------------------------------------------------
def build_ass_subtitles():
    print("--- 1. Generating Kinetic ASS Subtitles (Lower Third Only) ---")
    words_file = SCRATCH_DIR / "words.json"
    words = json.loads(words_file.read_text(encoding="utf-8"))

    def fmt_time(t):
        hrs = int(t // 3600)
        mins = int((t % 3600) // 60)
        secs = int(t % 60)
        centis = int(round((t - int(t)) * 100))
        if centis >= 100:
            centis = 99
        return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

    GOLD = r"{\c&H0000D7FF&}"
    CYAN = r"{\c&H00FFFF00&}"
    RED = r"{\c&H000030D0&}"
    WHITE = r"{\c&HFFFFFF&}"

    KEYWORD_COLORS = {
        "soundtrack": GOLD, "miller's": CYAN, "tick": GOLD, "zimmer's": GOLD,
        "1.25": GOLD, "seconds": GOLD, "tempo": WHITE, "gargantua's": RED,
        "gravity": RED, "hour": GOLD, "seven": GOLD, "years": GOLD,
        "math": WHITE, "earth": CYAN, "day": CYAN, "click": GOLD,
        "cooper": WHITE, "losing": RED, "daughter's": GOLD, "life": GOLD,
        "mountain": RED, "wave": RED, "ship": WHITE, "twenty-three": RED,
        "four": RED, "eight": RED, "days": RED, "vanished": RED,
        "ticking": GOLD, "music": WHITE, "countdown": RED, "parenthood": GOLD
    }

    cards = []
    curr = []
    for w in words:
        curr.append(w)
        if w["word"].endswith((".", ",", ";", ":", "?", "!")) or len(curr) >= 3:
            cards.append(curr)
            curr = []
    if curr:
        cards.append(curr)

    events = []
    for card in cards:
        st = card[0]["start"]
        et = card[-1]["end"]
        et = max(et, st + 0.50)

        line_parts = []
        for w in card:
            raw = w["word"].upper()
            core = w["word"].strip().lower().replace(",", "").replace(".", "").replace('"', '').replace("'", "")
            col = KEYWORD_COLORS.get(core)
            if col and col != WHITE:
                line_parts.append(f"{col}{raw}{WHITE}")
            else:
                line_parts.append(raw)
        text = " ".join(line_parts)
        events.append(f"Dialogue: 0,{fmt_time(st)},{fmt_time(et)},CenterBold,,0,0,0,,{text}")

    ass_content = f"""[Script Info]
Title: Cinema Decoded - Interstellar Ticking Clock 8K
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterBold,Arial Black,76,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,2,0,1,10,4,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"

    ASS_PATH.write_text(ass_content, encoding="utf-8")
    print(f"✅ Generated {len(events)} ASS subtitle dialogue lines in: {ASS_PATH}")

# -------------------------------------------------------------------------
# 2. Render Clean Visual Clips (70% Canvas, Zero Box Text)
# -------------------------------------------------------------------------
SCENE_PLAN_INTERSTELLAR = [
    {
        "id": "scene_01",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 55.0, "dur": 2.80,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_02",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 68.0, "dur": 5.12,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_03",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 118.0, "dur": 4.00,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_04",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 135.0, "dur": 3.20,
        "motion": "FAST_ZOOM"
    },
    {
        "id": "scene_05",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 152.0, "dur": 5.60,
        "motion": "FAST_ZOOM"
    },
    {
        "id": "scene_06",
        "clip": "output/clip_cache/interstellar_tidal_wave_1080p.mp4",
        "ss": 205.0, "dur": 4.88,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_07",
        "clip": "output/clip_cache/interstellar_romilly_23years_1080p.mp4",
        "ss": 18.0, "dur": 6.56,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_08",
        "clip": "output/clip_cache/interstellar_messages_23years_1080p.mp4",
        "ss": 88.0, "dur": 4.69,
        "motion": "SLOW_PUSH_IN"
    }
]

def render_clean_clip(scene, out_path):
    clip_path = REPO_ROOT / scene["clip"]
    ss = scene["ss"]
    dur = scene["dur"]
    zoom_expr = "min(zoom+0.0016,1.10)" if scene["motion"] == "FAST_ZOOM" else "min(zoom+0.0004,1.03)"

    filter_complex = (
        f"[0:v]tpad=stop_mode=clone:stop_duration=1.0[vpad];"
        f"[vpad]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=35:5,eq=brightness=-0.08:contrast=1.15:saturation=1.3[bg];"
        f"[vpad]scale=1080:1344:force_original_aspect_ratio=increase,crop=1080:1344,"
        f"zoompan=z='{zoom_expr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        f"[bg][fg]overlay=0:288,"
        f"drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
        f"drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill,"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{ss:.3f}",
        "-t", f"{dur:.3f}",
        "-i", str(clip_path),
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ]
    run_cmd(cmd, f"Rendering clean {Path(out_path).name}")

def main():
    print("======================================================================")
    print("🚀 CINEMA DECODED: INTERSTELLAR TICKING CLOCK — 8K MASTER BUILDER")
    print("======================================================================\n")

    # 1. Build Subtitles
    build_ass_subtitles()

    # 2. Render 8 Visual Scenes
    concat_txt = CLIPS_DIR / "concat_list.txt"
    lines = []
    for i, s in enumerate(SCENE_PLAN_INTERSTELLAR, 1):
        c_path = CLIPS_DIR / f"{i:02d}_{s['id']}.mp4"
        if not c_path.exists():
            render_clean_clip(s, c_path)
        lines.append(f"file '{c_path.resolve()}'")
    concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    visual_master = str(CLIPS_DIR / "visual_master.mp4")
    if not (CLIPS_DIR / "visual_master.mp4").exists():
        run_cmd([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            visual_master
        ], "Concatenating Clean Visual Clips")

    # 3. Composite 1080p Master with Subtitles Only
    master_1080p = str(OUT_DIR / "cinema_decoded_interstellar_1080p.mp4")
    escaped_ass = str(ASS_PATH).replace("\\", "/").replace(":", "\\:")
    run_cmd([
        "ffmpeg", "-y",
        "-i", visual_master,
        "-i", str(AUDIO_MASTER),
        "-vf", f"subtitles='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
        "-c:a", "aac", "-b:a", "256k",
        "-t", f"{TOTAL_DUR:.3f}",
        "-movflags", "+faststart",
        master_1080p
    ], "Compositing 1080p Master Video with Subtitles Only")

    shutil.copyfile(master_1080p, str(FINAL_1080P_REPO))
    shutil.copyfile(master_1080p, str(FINAL_1080P_DIR))
    print(f"✅ 1080p Master exported: {FINAL_1080P_REPO}")

    # 4. Composite 4K UHD Master
    master_4k = str(OUT_DIR / "cinema_decoded_interstellar_4k.mp4")
    print("\n[SUPER-RESOLUTION] Generating pristine 4K UHD Master...")
    upgrade_to_super_resolution(
        input_video=master_1080p,
        output_video=master_4k,
        target_tier="4K",
        sharpness=0.30
    )
    shutil.copyfile(master_4k, str(FINAL_4K_REPO))
    shutil.copyfile(master_4k, str(FINAL_4K_DIR))
    print(f"✅ 4K UHD Master exported: {FINAL_4K_REPO}")

    # 5. Composite 8K Ultra HD Master (4320x7680)
    master_8k = str(OUT_DIR / "cinema_decoded_interstellar_8k.mp4")
    print("\n[SUPER-RESOLUTION] Generating pristine 8K Ultra HD Master (4320x7680)...")
    upgrade_to_super_resolution(
        input_video=master_1080p,
        output_video=master_8k,
        target_tier="8K",
        sharpness=0.35,
        bitrate="85M"
    )
    shutil.copyfile(master_8k, str(FINAL_8K_REPO))
    shutil.copyfile(master_8k, str(FINAL_8K_DIR))
    print(f"✅ 8K Ultra HD Master exported: {FINAL_8K_REPO}")

    # 6. Render Clean High-CTR Thumbnail
    thumb_src = str(REPO_ROOT / "output" / "clip_cache" / "interstellar_tidal_wave_1080p.mp4")
    run_cmd([
        "ffmpeg", "-y",
        "-ss", "152.0", "-i", thumb_src,
        "-filter_complex", (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=30:5,eq=brightness=-0.10:contrast=1.20:saturation=1.4[bg];"
            "[0:v]scale=1080:1344:force_original_aspect_ratio=increase,crop=1080:1344,"
            "eq=brightness=0.04:contrast=1.18:saturation=1.25[fg];"
            "[bg][fg]overlay=0:288,"
            "drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
            "drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill"
        ),
        "-vframes", "1",
        str(THUMBNAIL_PATH)
    ], "Rendering Clean High-CTR Vertical Thumbnail")
    shutil.copyfile(str(THUMBNAIL_PATH), str(THUMBNAIL_OUTPUT))

    # 7. QC Frames
    print("\n[QC] Extracting 16 verification frames across the timeline...")
    qc_stamps = [round(i * (TOTAL_DUR / 16.0) + 0.3, 2) for i in range(16)]
    for i, t in enumerate(qc_stamps, 1):
        fpath = str(QC_DIR / f"frame_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", master_1080p, "-vframes", "1", "-q:v", "2", fpath], capture_output=True)

    print("======================================================================")
    print("🎉 INTERSTELLAR 8K MASTER VIDEO COMPLETE!")
    print(f"   8K Ultra HD: {FINAL_8K_REPO}")
    print(f"   4K UHD:      {FINAL_4K_REPO}")
    print(f"   1080p:       {FINAL_1080P_REPO}")
    print(f"   Duration:    {TOTAL_DUR:.2f}s")
    print("======================================================================")

if __name__ == "__main__":
    main()

