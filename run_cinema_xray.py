#!/usr/bin/env python3
"""
Cinema X-Ray Master Autonomous Pipeline Runner
----------------------------------------------
Generates a complete, high-retention cinematic breakdown video:
1. Generates or loads the script & concept.
2. Generates studio-grade Gemini Achird voiceover.
3. Aligns rapid subtitle cards in Center Bold Stroke style with acoustic precision.
4. Slices and formats movie scenes to 100% Fullscreen (or 70% Ambient) framing.
5. Mixes cinematic tension score and burns subtitles.
6. Renders final 1080x1920 Short + Ultra 4K UHD Master (2160x3840).
"""

import os
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))

from pipeline.audio_generator import generate_achird_audio
from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles
from pipeline.youtube_uploader import upload_video
from pipeline.video_compositor import (
    render_70pct_scene_clip,
    render_100pct_fullscreen_clip,
    assemble_final_video,
    export_4k_uhd
)

def run_pipeline(mode: str = "fullscreen"):
    print("==================================================")
    print(f"🎬 CINEMA X-RAY: AUTONOMOUS VIDEO PRODUCTION ({mode.upper()} MODE)")
    print("==================================================")

    # 1. Topic & Script Configuration
    script_text = (
        "In Age of Ultron, when Steve Rogers barely nudged Thor's hammer, "
        "Thor's smile instantly froze in sheer panic. "
        "Did Cap suddenly become worthy in Endgame, or did he fake it five years earlier? "
        "The answer reveals Steve's true character. "
        "Odin's enchantment states that whoever holds the hammer, if he be worthy, "
        "possesses the power of Thor. "
        "There is no such thing as being 'a little bit worthy'. You can either lift it, or you cannot. "
        "The second Steve felt Mjolnir budge, his humility kicked in. "
        "He stopped pulling to spare Thor's ego in front of the team. "
        "Five years later, with Thanos crushing Thor's chest, politeness was off the table. "
        "When Thor screams 'I knew it!', he wasn't surprised Steve was worthy. "
        "He knew Cap had lied to protect his feelings all along."
    )

    script_dir = BASE_DIR / "output" / "script"
    audio_dir = BASE_DIR / "output" / "audio"
    clips_dir = BASE_DIR / "output" / (f"clips_{mode}" if mode == "fullscreen" else "clips")
    temp_dir = BASE_DIR / "output" / "temp"
    final_dir = BASE_DIR / "output" / "final_video"

    script_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    script_file = script_dir / "mjolnir_worthiness_script.txt"
    script_file.write_text(script_text, encoding="utf-8")
    print(f"\n[Step 1/5] Script Prepared:\n{script_text}\n")

    # 2. Voiceover Generation
    audio_path = audio_dir / "mjolnir_worthiness_voiceover.wav"
    print("\n[Step 2/5] Generating/Loading Gemini Achird Voiceover...")
    total_duration = generate_achird_audio(script_text, str(audio_path))
    print(f"Voiceover Duration: {total_duration:.2f} seconds")

    # 3. Subtitle Alignment & ASS Generation
    print("\n[Step 3/5] Generating Center Bold Stroke Subtitles (Acoustic Locked)...")
    subtitles_json_path = script_dir / "subtitles.json"
    cards = generate_timed_subtitles(str(audio_path), script_text, total_duration, str(subtitles_json_path), force_refresh=False)

    ass_path = temp_dir / "subtitles_center_bold.ass"
    build_ass_subtitles(cards, str(ass_path))

    # 4. Slicing & Preparing Video Scenes
    print(f"\n[Step 4/5] Processing Cinematic Scenes from Raw Video ({mode.upper()} Framing)...")
    ultron_raw = BASE_DIR / "projects" / "marvel-decoded" / "raw_video" / "ultron_hammer.mp4"
    endgame_raw = BASE_DIR / "projects" / "marvel-decoded" / "raw_video" / "endgame_mjolnir.mp4"

    # Precise scene timeline tailored to narration & subject placement
    scene_cuts = [
        {"src": ultron_raw,  "in": 14.5, "dur": 4.5, "x_offset": -600, "desc": "Thor watching Steve walk up"},
        {"src": ultron_raw,  "in": 20.0, "dur": 5.0, "x_offset": -300, "desc": "Steve pulls, hammer squeaks, Thor freezes"},
        {"src": ultron_raw,  "in": 25.5, "dur": 4.5, "x_offset": 0,    "desc": "Steve stops, Thor nervous laugh"},
        {"src": ultron_raw,  "in": 21.5, "dur": 4.8, "x_offset": -200, "desc": "Close up of Mjolnir enchantment"},
        {"src": endgame_raw, "in": 0.5,  "dur": 5.5, "x_offset": 0,    "desc": "Endgame: Thanos pressing axe on Thor"},
        {"src": endgame_raw, "in": 8.5,  "dur": 4.5, "x_offset": 0,    "desc": "Mjolnir flies off the ground"},
        {"src": endgame_raw, "in": 13.5, "dur": 5.2, "x_offset": -600, "desc": "Cap catches Mjolnir, ready to fight"},
        {"src": endgame_raw, "in": 23.5, "dur": 4.8, "x_offset": 300,  "desc": "Cap walks forward with Mjolnir and shield"},
        {"src": endgame_raw, "in": 17.5, "dur": round(total_duration - 38.8, 2), "x_offset": 0, "desc": "Thor smiling: I knew it!"}
    ]

    rendered_clips = []
    for idx, sc in enumerate(scene_cuts, 1):
        out_clip = clips_dir / f"scene_{idx:02d}.mp4"
        print(f"  Cutting Scene {idx:02d}: {sc['desc']} ({sc['dur']:.2f}s, offset: {sc['x_offset']})...")
        if mode == "fullscreen":
            render_100pct_fullscreen_clip(str(sc["src"]), sc["in"], sc["dur"], str(out_clip), x_offset=sc["x_offset"])
        else:
            render_70pct_scene_clip(str(sc["src"]), sc["in"], sc["dur"], str(out_clip))
        rendered_clips.append(str(out_clip))

    # 5. Master Video Assembly (Music + Subtitles + Clips)
    suffix = "_fullscreen" if mode == "fullscreen" else ""
    final_output_1080p = final_dir / f"cinema_xray_cap_mjolnir_worthy{suffix}.mp4"
    final_output_4k = final_dir / f"cinema_xray_cap_mjolnir_worthy{suffix}_4k.mp4"

    print(f"\n[Step 5/5] Assembling Master Video with Ambient Score & Subtitles...")
    assemble_final_video(
        scene_clips=rendered_clips,
        audio_path=str(audio_path),
        ass_subtitle_path=str(ass_path),
        output_mp4=str(final_output_1080p),
        temp_dir=str(temp_dir)
    )

    # 6. Ultra 4K UHD Master Export
    export_4k_uhd(str(final_output_1080p), str(final_output_4k))

    print("\n==================================================")
    print("🎉 CINEMA X-RAY VIDEO PRODUCTION COMPLETE!")
    print(f"📁 1080p Master : {final_output_1080p}")
    print(f"🌟 Ultra 4K UHD : {final_output_4k}")
    print(f"⏱️ Duration     : {total_duration:.2f}s")
    print(f"📺 Framing      : {mode.upper()} 100% Fullscreen Short Form")
    print(f"💬 Subtitles    : Center Bold Stroke (Acoustic Aligned + Gold Keywords)")
    # 7. Optional Direct YouTube Upload
    if upload:
        print("\n[Step 7] Uploading Video Directly to YouTube...")
        try:
            yt_title = "The Exact Second Cap Became Worthy | Cinema X-Ray #shorts"
            yt_desc = (
                "Did Steve Rogers always have the power of Thor? In Avengers: Age of Ultron, Mjolnir budged... "
                "In Avengers: Endgame, Thor's chest was being crushed when the hammer answered Cap's call.\n\n"
                "#CinemaXRay #Marvel #CaptainAmerica #Thor #Mjolnir #AvengersEndgame #Shorts"
            )
            upload_target = str(final_output_4k) if upload_4k else str(final_output_1080p)
            yt_result = upload_video(
                file_path=upload_target,
                title=yt_title,
                description=yt_desc,
                tags=["Cinema X-Ray", "Captain America", "Thor", "Mjolnir", "Marvel", "Endgame", "Shorts"],
                privacy_status=privacy
            )
            print(f"🚀 Live Video Link: {yt_result['url']}")
        except Exception as e:
            print(f"❌ YouTube Upload Error: {e}")

    print("==================================================")
    return str(final_output_4k)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["fullscreen", "70pct"], default="70pct")
    parser.add_argument("--upload", action="store_true", help="Upload directly to YouTube upon completion")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted", help="YouTube privacy status")
    parser.add_argument("--upload-4k", action="store_true", default=True, help="Upload Ultra 4K UHD master instead of 1080p")
    args = parser.parse_args()
    run_pipeline(mode=args.mode, upload=args.upload, privacy=args.privacy, upload_4k=args.upload_4k)
