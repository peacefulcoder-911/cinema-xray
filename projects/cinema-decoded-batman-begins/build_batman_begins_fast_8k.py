#!/usr/bin/env python3
"""
Cinema Decoded: Batman Begins — Fast 8K Ultra HD Master Builder
Uses the Native Fast Achird Voiceover (41.37s), procedural cinematic sound design,
clean 70% canvas framing (ZERO box text / HUD overlays), kinetic ASS subtitles,
and direct 8K Super-Resolution (4320x7680) via Apple Silicon hevc_videotoolbox.
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
CLIPS_DIR = PROJECT_DIR / "clips_fast"
SCRATCH_DIR = PROJECT_DIR / "scratch"
QC_DIR = PROJECT_DIR / "qc_frames_fast"
OUT_DIR = PROJECT_DIR / "out_fast"

for d in [CLIPS_DIR, SCRATCH_DIR, QC_DIR, OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

VOICE_WAV = REPO_ROOT / "output" / "audio_only" / "batman_begins_achird_without_emotions_fast_native.wav"
AUDIO_MASTER = PROJECT_DIR / "batman_begins_fast_mixed_audio.m4a"
ASS_PATH = PROJECT_DIR / "batman_begins_fast_subtitles.ass"

FINAL_1080P_REPO = REPO_ROOT / "output" / "cinema_xray_batman_begins_fear_1080p.mp4"
FINAL_4K_REPO = REPO_ROOT / "output" / "cinema_xray_batman_begins_fear_4k.mp4"
FINAL_8K_REPO = REPO_ROOT / "output" / "cinema_xray_batman_begins_fear_8k.mp4"

FINAL_1080P_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_batman_begins_fear_1080p.mp4"
FINAL_4K_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_batman_begins_fear_4k.mp4"
FINAL_8K_DIR = REPO_ROOT / "output" / "final_video" / "cinema_xray_batman_begins_fear_8k.mp4"

THUMBNAIL_PATH = PROJECT_DIR / "thumbnail_fast.jpg"
THUMBNAIL_OUTPUT = REPO_ROOT / "output" / "thumbnails_short" / "batman_begins_fear_thumb.jpg"

TOTAL_DUR = 41.371

def run_cmd(cmd, desc="Running command"):
    print(f"\n[RUNNING] {desc}")
    print(" ".join(cmd[:8]) + ("..." if len(cmd) > 8 else ""))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Error in {desc}:\n{res.stderr[-1000:]}")
        raise RuntimeError(f"Command failed: {desc}")
    return res

# -------------------------------------------------------------------------
# 1. Build High-Fidelity Mixed Audio (Voice + Drone + Room Tone + 7 SFX)
# -------------------------------------------------------------------------
def build_audio_master():
    print("--- 1. Building Broadcast Standard Mixed Audio Master (41.37s) ---")
    drone_wav = str(SCRATCH_DIR / "batman_drone_fast.wav")
    cave_wav = str(SCRATCH_DIR / "cave_ambience_fast.wav")

    # A. Sub-Bass Drone (55Hz + 110Hz harmonic)
    drone_cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-f", "lavfi", "-i", f"sine=frequency=55:duration={TOTAL_DUR:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=110:duration={TOTAL_DUR:.3f}",
        "-filter_complex",
        "[0:a]volume=0.22[sub];"
        "[1:a]volume=0.07[harm];"
        "[sub][harm]amix=inputs=2:dropout_transition=0,"
        "volume='if(between(t,4.0,7.0), 0.28, if(between(t,22.0,28.0), 0.32, if(between(t,33.0,38.0), 0.26, 0.18)))':eval=frame,"
        f"afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL_DUR-2.0:.2f}:d=2.0[drone]",
        "-map", "[drone]",
        "-c:a", "pcm_s16le", "-ar", "24000",
        drone_wav
    ]
    subprocess.run(drone_cmd, check=True)

    # B. Batcave Room Tone
    cave_cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-f", "lavfi", "-i", f"anoisesrc=d={TOTAL_DUR:.3f}:c=pink:r=24000:a=0.06",
        "-af", f"lowpass=f=450,highpass=f=80,volume=0.18,afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL_DUR-2.0:.2f}:d=2.0",
        "-c:a", "pcm_s16le", "-ar", "24000",
        cave_wav
    ]
    subprocess.run(cave_cmd, check=True)

    # C. SFX Components
    plunge_wav = str(SCRATCH_DIR / "plunge_sub.wav")
    flutter_wav = str(SCRATCH_DIR / "bat_flutter.wav")
    rise_wav = str(SCRATCH_DIR / "father_rise.wav")
    steel_wav = str(SCRATCH_DIR / "ninja_steel.wav")

    # Generate if missing
    if not os.path.exists(plunge_wav):
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi", "-i", "sine=frequency=52:duration=2.0", "-af", "afade=t=in:st=0:d=0.05,afade=t=out:st=0.3:d=1.7,volume=0.35", "-ar", "24000", plunge_wav], check=True)
    if not os.path.exists(flutter_wav):
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi", "-i", "anoisesrc=d=2.0:c=brown:r=24000:a=0.35", "-af", "lowpass=f=950,highpass=f=250,afade=t=in:st=0:d=0.2,afade=t=out:st=0.6:d=1.4,volume=0.25", "-ar", "24000", flutter_wav], check=True)
    if not os.path.exists(rise_wav):
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi", "-i", "sine=frequency=146.8:duration=2.5", "-af", "afade=t=in:st=0:d=0.3,afade=t=out:st=0.8:d=1.7,volume=0.20", "-ar", "24000", rise_wav], check=True)
    if not os.path.exists(steel_wav):
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi", "-i", "sine=frequency=1046.5:duration=1.5", "-f", "lavfi", "-i", "sine=frequency=78:duration=1.5", "-filter_complex", "[0:a]afade=t=in:st=0:d=0.01,afade=t=out:st=0.2:d=1.3,volume=0.20[ring];[1:a]afade=t=in:st=0:d=0.02,afade=t=out:st=0.3:d=1.2,volume=0.30[sub];[ring][sub]amix=inputs=2:dropout_transition=0[out]", "-map", "[out]", "-ar", "24000", steel_wav], check=True)

    # Master Mixing
    mix_filter = (
        "[0:a]volume=1.0[voice];"
        "[1:a]volume=0.24[drone];"
        "[2:a]volume=0.18[cave];"
        "[3:a]adelay=4200|4200,volume=0.40[sfx_plunge];"
        "[4:a]adelay=7000|7000,volume=0.30[sfx_flutter];"
        "[5:a]adelay=10800|10800,volume=0.25[sfx_rise];"
        "[6:a]adelay=16000|16000,volume=0.30[sfx_steel];"
        "[voice][drone][cave][sfx_plunge][sfx_flutter][sfx_rise][sfx_steel]"
        "amix=inputs=7:dropout_transition=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[master]"
    )

    master_cmd = [
        "ffmpeg", "-y",
        "-i", str(VOICE_WAV),
        "-i", drone_wav,
        "-i", cave_wav,
        "-i", plunge_wav,
        "-i", flutter_wav,
        "-i", rise_wav,
        "-i", steel_wav,
        "-filter_complex", mix_filter,
        "-map", "[master]",
        "-c:a", "aac", "-b:a", "256k",
        "-t", f"{TOTAL_DUR:.3f}",
        str(AUDIO_MASTER)
    ]
    run_cmd(master_cmd, "Mastering Broadcast Mixed Audio (-14 LUFS)")
    print(f"✅ Audio master exported: {AUDIO_MASTER}")

# -------------------------------------------------------------------------
# 2. Build Kinetic ASS Subtitles (NO Box Overlays)
# -------------------------------------------------------------------------
def build_ass_subtitles():
    print("--- 2. Generating Kinetic ASS Subtitles (Clean Lower Third) ---")
    words_file = SCRATCH_DIR / "fast_words.json"
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
    RED = r"{\c&H000030D0&}"
    WHITE = r"{\c&HFFFFFF&}"

    KEYWORD_COLORS = {
        "fearlessness": GOLD, "terror": RED, "bruce": WHITE, "wayne": WHITE,
        "well": GOLD, "bats": GOLD, "scarred": RED, "falling": GOLD,
        "rise": GOLD, "darkness": GOLD, "truth": GOLD, "fear": RED,
        "become": GOLD, "swarm": GOLD, "dread": GOLD, "weakness": RED,
        "armor": GOLD, "weapon": GOLD, "identity": GOLD
    }

    # Group words into 2-4 word cards
    cards = []
    curr = []
    for w in words:
        curr.append(w)
        cleaned = w["word"].strip().lower().replace(",", "").replace(".", "").replace('"', '').replace("'", "")
        # Break on punctuation or every 3-4 words
        if w["word"].endswith((".", ",", ";", ":", "?", "!")) or len(curr) >= 3:
            cards.append(curr)
            curr = []
    if curr:
        cards.append(curr)

    events = []
    for card in cards:
        st = card[0]["start"]
        et = card[-1]["end"]
        # Extend slightly for readability
        et = max(et, st + 0.55)

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
Title: Cinema Decoded - Batman Begins Fast 8K
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
# 3. Render Clean Visual Clips (70% Canvas, Zero Box Text)
# -------------------------------------------------------------------------
SCENE_PLAN_FAST = [
    {
        "id": "scene_01",
        "clip": "output/clip_cache/_BdN3m5ZENI_hd.mp4",
        "ss": 22.0, "dur": 4.20,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_02",
        "clip": "output/clip_cache/_BdN3m5ZENI_hd.mp4",
        "ss": 26.5, "dur": 2.60,
        "motion": "FAST_ZOOM"
    },
    {
        "id": "scene_03",
        "clip": "output/clip_cache/S3UsAgjZA3Q_hd.mp4",
        "ss": 12.0, "dur": 3.80,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_04",
        "clip": "output/clip_cache/HIcGuFnl7ZU_hd.mp4",
        "ss": 27.0, "dur": 5.20,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_05",
        "clip": "output/clip_cache/xJYSJWXmUeU_hd.mp4",
        "ss": 42.0, "dur": 7.40,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_06",
        "clip": "output/clip_cache/O346Rqdj2Uk_hd.mp4",
        "ss": 66.0, "dur": 5.30,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_07",
        "clip": "output/clip_cache/xd1Qp8VwiBU.mp4",
        "ss": 4.0, "dur": 6.50,
        "motion": "SLOW_PUSH_IN"
    },
    {
        "id": "scene_08",
        "clip": "output/clip_cache/8aGtHBHx7HU_hd.mp4",
        "ss": 268.0, "dur": 6.371,
        "motion": "FAST_ZOOM"
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
    print("🚀 CINEMA DECODED: BATMAN BEGINS — FAST 8K MASTER BUILDER")
    print("======================================================================\n")

    # 1. Master Mixed Audio
    build_audio_master()

    # 2. Build Kinetic Subtitles
    build_ass_subtitles()

    # 3. Render 8 Visual Scenes
    clip_files = []
    concat_txt = CLIPS_DIR / "concat_list.txt"
    lines = []
    for i, s in enumerate(SCENE_PLAN_FAST, 1):
        c_path = CLIPS_DIR / f"{i:02d}_{s['id']}.mp4"
        render_clean_clip(s, c_path)
        clip_files.append(c_path)
        lines.append(f"file '{c_path.resolve()}'")
    concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    visual_master = str(CLIPS_DIR / "visual_master_fast.mp4")
    run_cmd([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        visual_master
    ], "Concatenating Clean Visual Clips")

    # 4. Composite 1080p Master with Subtitles Only
    master_1080p = str(OUT_DIR / "cinema_decoded_batman_begins_fast_1080p.mp4")
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

    # 5. Composite 4K UHD Master
    master_4k = str(OUT_DIR / "cinema_decoded_batman_begins_fast_4k.mp4")
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

    # 6. Composite 8K Ultra HD Master (4320x7680)
    master_8k = str(OUT_DIR / "cinema_decoded_batman_begins_fast_8k.mp4")
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

    # 7. Render Clean Thumbnail
    thumb_src = str(REPO_ROOT / "output" / "clip_cache" / "O346Rqdj2Uk_hd.mp4")
    run_cmd([
        "ffmpeg", "-y",
        "-ss", "70.0", "-i", thumb_src,
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

    # 8. QC Frames
    print("\n[QC] Extracting 16 verification frames across the timeline...")
    qc_stamps = [round(i * (TOTAL_DUR / 16.0) + 0.3, 2) for i in range(16)]
    for i, t in enumerate(qc_stamps, 1):
        fpath = str(QC_DIR / f"frame_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", master_1080p, "-vframes", "1", "-q:v", "2", fpath], capture_output=True)

    print("======================================================================")
    print("🎉 FAST 8K PRODUCTION MASTER COMPLETE!")
    print(f"   8K Ultra HD: {FINAL_8K_REPO}")
    print(f"   4K UHD:      {FINAL_4K_REPO}")
    print(f"   1080p:       {FINAL_1080P_REPO}")
    print(f"   Duration:    {TOTAL_DUR:.2f}s")
    print("======================================================================")

if __name__ == "__main__":
    main()

