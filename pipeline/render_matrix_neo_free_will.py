#!/usr/bin/env python3
"""
Cinema Decoded: The Matrix Reloaded — Was Neo Ever Really Free?
Director-level prompt-driven documentary engine.
- Duration: 52.50s (Target: 50-55s)
- Aspect Ratio: 9:16 Vertical
- Master 8K: 4320x7680 @ 30 FPS HEVC
- Delivery 1080p: 1080x1920 @ 30 FPS H.264
- Audio: ElevenLabs Liam (-14.0 LUFS / -1.0 dBFS) + Sterile Sub-Bass Drone (-22 dBFS)
- Captions: Style 7 Arc Reactor Cyan HUD + Director Graphical Callout Cards
- ZERO WHOOSHES, ZERO SWOOSHES, ZERO ARTIFICIAL TRANSITION SFX.
"""

import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
PROJ_DIR = REPO_ROOT / "projects" / "cinema-decoded-matrix_neo_free_will"
CLIPS_DIR = PROJ_DIR / "clips"
OUT_DIR = PROJ_DIR / "out"
AUDIO_DIR = PROJ_DIR / "audio"
FINAL_DIR = REPO_ROOT / "output" / "final_video"

FOOTAGE_DIR = REPO_ROOT / "assets" / "footage" / "matrix_reloaded" / "architect_revelation"
AUDIO_PATH = AUDIO_DIR / "master_audio_final.wav"
ASS_PATH = PROJ_DIR / "subtitles.ass"

CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_DUR = 52.50

def render_vertical_scene(src_path: str, ss: float, dur: float, out_path: str, x_offset_ratio: float = 0.5, zoom: str = "SLOW_PUSH_IN"):
    """
    Renders an authentic 1080p film clip into 9:16 vertical (1080x1920)
    with cinematic camera motion and high-contrast clinical color grading.
    x_offset_ratio: 0.0 (left), 0.5 (center), 1.0 (right).
    """
    frames = int(dur * 30)

    # Base scale: height to 1920, width scales proportionally to ~3413
    # Crop to 1080x1920 focusing on x_offset
    crop_x_expr = f"(iw-1080)*{x_offset_ratio}"

    if zoom == "SLOW_PUSH_IN":
        zoom_expr = f"zoompan=z='min(zoom+0.0003,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    elif zoom == "PULL_BACK":
        zoom_expr = f"zoompan=z='max(1.10-0.0003*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    elif zoom == "PAN_RIGHT":
        zoom_expr = f"zoompan=z=1.05:x='(iw-iw/zoom)*(on/{frames})':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    else:
        zoom_expr = f"zoompan=z=1.0:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"

    # Color grading: crisp contrast, clinical cool white architectural grade, controlled highlights
    eq_filter = "eq=contrast=1.12:brightness=-0.02:saturation=0.92"

    vf = (
        f"scale=-1:1920,"
        f"crop=1080:1920:{crop_x_expr}:0,"
        f"{zoom_expr},"
        f"{eq_filter},"
        f"fps=30,format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{ss:.3f}",
        "-i", src_path,
        "-t", f"{dur:.3f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-an",
        out_path
    ]
    subprocess.run(cmd, check=True)
    print(f"  -> Generated {os.path.basename(out_path)} ({dur:.2f}s)")


def create_scene_01(out_path: str):
    """Scene 1 (0.00s - 6.50s | 6.50s): The Revelation - Symmetrical White Room & Wall of Screens"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "architect_room_wide.mp4"),
        ss=0.5,
        dur=6.50,
        out_path=out_path,
        x_offset_ratio=0.5,
        zoom="SLOW_PUSH_IN"
    )

def create_scene_02(out_path: str):
    """Scene 2 (6.50s - 12.00s | 5.50s): The Plan - Television Screens Tracking Pre-calculated Reactions"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "television_screens.mp4"),
        ss=0.0,
        dur=5.50,
        out_path=out_path,
        x_offset_ratio=0.5,
        zoom="PAN_RIGHT"
    )

def create_scene_03(out_path: str):
    """Scene 3 (12.00s - 17.50s | 5.50s): The Architect - Dominant Composition Behind Desk"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "architect_closeup.mp4"),
        ss=0.5,
        dur=5.50,
        out_path=out_path,
        x_offset_ratio=0.55,
        zoom="SLOW_PUSH_IN"
    )

def create_scene_04(out_path: str):
    """Scene 4 (17.50s - 27.50s | 10.00s): The Previous Ones - Screaming TV Screens & Iteration Cycles"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "television_screens.mp4"),
        ss=2.0,
        dur=10.00,
        out_path=out_path,
        x_offset_ratio=0.45,
        zoom="SLOW_PUSH_IN"
    )

def create_scene_05(out_path: str):
    """Scene 5 (27.50s - 38.00s | 10.50s): The Psychological Turn - 'Think about that' & Neo Realization"""
    # Part A: Neo stunned face (5.0s) + Part B: Screens tracking algorithmic behavior (5.5s)
    part_a = str(CLIPS_DIR / "s05_part_a.mp4")
    part_b = str(CLIPS_DIR / "s05_part_b.mp4")

    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "neo_reaction.mp4"),
        ss=0.5,
        dur=5.00,
        out_path=part_a,
        x_offset_ratio=0.5,
        zoom="SLOW_PUSH_IN"
    )
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "television_screens.mp4"),
        ss=4.5,
        dur=5.50,
        out_path=part_b,
        x_offset_ratio=0.6,
        zoom="PULL_BACK"
    )

    # Concat part A and B
    cat_txt = PROJ_DIR / "cat_s05.txt"
    with open(cat_txt, "w") as f:
        f.write(f"file '{part_a}'\nfile '{part_b}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat_txt), "-c", "copy", out_path], check=True)

def create_scene_06(out_path: str):
    """Scene 6 (38.00s - 46.50s | 8.50s): The Choice - Two Doors: Zion or Trinity"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "trinity_choice.mp4"),
        ss=1.0,
        dur=8.50,
        out_path=out_path,
        x_offset_ratio=0.4,
        zoom="SLOW_PUSH_IN"
    )

def create_scene_07(out_path: str):
    """Scene 7 (46.50s - 52.50s | 6.00s): Final Payoff - Neo's Unexpected Choice, Left Door & Cut to Black"""
    render_vertical_scene(
        src_path=str(FOOTAGE_DIR / "neo_decision.mp4"),
        ss=2.0,
        dur=6.00,
        out_path=out_path,
        x_offset_ratio=0.5,
        zoom="PULL_BACK"
    )


def main():
    print("=" * 70)
    print("🎬 CINEMA DECODED: THE MATRIX RELOADED — WAS NEO EVER REALLY FREE?")
    print("   Target Duration: 52.50s | Aspect Ratio: 9:16 Vertical")
    print("=" * 70)

    scene_files = [
        str(CLIPS_DIR / "scene_01_revelation.mp4"),
        str(CLIPS_DIR / "scene_02_plan.mp4"),
        str(CLIPS_DIR / "scene_03_architect.mp4"),
        str(CLIPS_DIR / "scene_04_previous_ones.mp4"),
        str(CLIPS_DIR / "scene_05_psychological_turn.mp4"),
        str(CLIPS_DIR / "scene_06_choice.mp4"),
        str(CLIPS_DIR / "scene_07_payoff.mp4")
    ]

    print("\n🎞️  Rendering Scene 1 (0.0s - 6.5s): Symmetrical White Room Establishing...")
    create_scene_01(scene_files[0])

    print("🎞️  Rendering Scene 2 (6.5s - 12.0s): Television Screens & Pre-calculated Reactions...")
    create_scene_02(scene_files[1])

    print("🎞️  Rendering Scene 3 (12.0s - 17.5s): Architect Dominant Chair Close-up...")
    create_scene_03(scene_files[2])

    print("🎞️  Rendering Scene 4 (17.5s - 27.5s): Alternate Neos Screaming Across Monitors...")
    create_scene_04(scene_files[3])

    print("🎞️  Rendering Scene 5 (27.5s - 38.0s): 'Think about that' & Algorithmic Rebellion...")
    create_scene_05(scene_files[4])

    print("🎞️  Rendering Scene 6 (38.0s - 46.5s): The Choice: Zion or Trinity Doors...")
    create_scene_06(scene_files[5])

    print("🎞️  Rendering Scene 7 (46.5s - 52.5s): Neo's Defiant Decision & Door Exit...")
    create_scene_07(scene_files[6])

    print("\n🔗 Assembling unified video montage...")
    concat_list = PROJ_DIR / "concat_scenes.txt"
    with open(concat_list, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf}'\n")

    video_only = str(CLIPS_DIR / "visual_montage_52s.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", video_only], check=True)

    delivery_1080p = str(OUT_DIR / "cinema_decoded_matrix_neo_free_will_1080p.mp4")
    print(f"\n✨ Assembling 1080p Delivery Copy with Arc Reactor Cyan HUD Subtitles...")
    cmd_burn = [
        "ffmpeg", "-y",
        "-i", video_only,
        "-i", str(AUDIO_PATH),
        "-filter_complex", f"[0:v]subtitles='{ASS_PATH}':fontsdir='/System/Library/Fonts/Supplemental'[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "320k",
        "-t", f"{TOTAL_DUR:.3f}",
        delivery_1080p
    ]
    subprocess.run(cmd_burn, check=True)
    sz_1080 = os.path.getsize(delivery_1080p) / (1024 * 1024)
    print(f"✅ 1080p YouTube Delivery Copy Assembled: {delivery_1080p} ({sz_1080:.2f} MB)")

    # STAGE 2: 8K Hardware-Accelerated Super-Resolution Master Render
    master_8k = str(FINAL_DIR / "cinema_decoded_matrix_neo_free_will_8k.mp4")
    print(f"\n🚀 Rendering 8K Master (4320x7680 @ 85 Mbps) to: {master_8k}...")
    from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution
    upgrade_to_super_resolution(
        input_video=delivery_1080p,
        output_video=master_8k,
        target_tier="8K"
    )
    sz_8k = os.path.getsize(master_8k) / (1024 * 1024)
    print(f"✅ 8K Super-Resolution Master Rendered: {master_8k} ({sz_8k:.2f} MB)")

    print("\n🎉 ALL RENDERS AND DELIVERABLES COMPLETE!")


if __name__ == "__main__":
    main()

