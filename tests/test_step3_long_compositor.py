"""
Cinema X-Ray: Verification Test for Step 3 (pipeline/long_form_compositor.py)
Tests:
  1. Renders 2 isolated widescreen beats into output/clips_long/ (one with Chapter HUD + SLOW_PUSH_IN)
  2. Assembles 1080p widescreen video with procedural ambient score and widescreen lower-third ASS subtitles
  3. Upscales to horizontal 4K UHD (3840x2160)
  4. Runs gatekeeper ffprobe checks for 16:9 aspect ratio, resolution, and audio integrity
  5. Strictly asserts git diff pipeline/video_compositor.py is empty (zero changes to Shorts compositor)
"""

import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.long_form_compositor import (
    render_widescreen_xray_clip,
    assemble_long_form_video,
    export_long_form_4k_uhd,
    gatekeeper_verify_long_video,
    CLIPS_LONG_DIR,
    TEMP_LONG_DIR,
    FINAL_LONG_DIR
)
from pipeline.subtitle_engine import build_ass_subtitles


def run_step3_verification():
    print("================================================================================")
    print("🎬 CINEMA X-RAY: STEP 3 LONG-FORM WIDESCREEN COMPOSITOR VERIFICATION")
    print("================================================================================\n")

    # 1. Assert git diff on Shorts compositor is completely empty
    print(">>> [CHECK 1/5] Verifying pipeline/video_compositor.py is 100% untouched...")
    diff_res = subprocess.run(
        ["git", "diff", "pipeline/video_compositor.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    diff_output = diff_res.stdout.strip()
    assert len(diff_output) == 0, f"VIOLATION: pipeline/video_compositor.py was modified:\n{diff_output}"
    print("✅ Verified: pipeline/video_compositor.py is completely clean and untouched!\n")

    # 2. Source video paths
    source_video = REPO_ROOT / "projects" / "marvel-decoded" / "raw_video" / "endgame_mjolnir.mp4"
    assert source_video.exists(), f"Source video not found: {source_video}"

    # 3. Render 2 isolated widescreen beats
    print(">>> [CHECK 2/5] Rendering isolated widescreen clips into output/clips_long/...")
    clip1 = CLIPS_LONG_DIR / "test_long_beat_01.mp4"
    clip2 = CLIPS_LONG_DIR / "test_long_beat_02.mp4"

    # Beat 1: Chapter HUD + SLOW_PUSH_IN (4.5s)
    print("  • Rendering Beat 1: Chapter 1 HUD ('The Inciting Incident') + SLOW_PUSH_IN...")
    render_widescreen_xray_clip(
        source_path=str(source_video),
        start_time=13.5,
        duration=4.5,
        output_clip_path=str(clip1),
        camera_motion="SLOW_PUSH_IN",
        chapter_title="Chapter 1: The Inciting Incident"
    )

    # Beat 2: STATIC (4.5s)
    print("  • Rendering Beat 2: STATIC framing...")
    render_widescreen_xray_clip(
        source_path=str(source_video),
        start_time=18.0,
        duration=4.5,
        output_clip_path=str(clip2),
        camera_motion="STATIC",
        chapter_title=None
    )

    assert clip1.exists() and clip1.stat().st_size > 0, "Clip 1 failed to render"
    assert clip2.exists() and clip2.stat().st_size > 0, "Clip 2 failed to render"
    print(f"✅ Rendered clips: {clip1.name} ({clip1.stat().st_size/1024:.1f} KB), {clip2.name} ({clip2.stat().st_size/1024:.1f} KB)\n")

    # 4. Prepare test audio & widescreen subtitles matching 9.0s duration
    print(">>> [CHECK 3/5] Generating matching 9.0s test audio & widescreen lower-third ASS...")
    TEMP_LONG_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_LONG_DIR.mkdir(parents=True, exist_ok=True)
    test_audio = TEMP_LONG_DIR / "test_long_voiceover_9s.wav"
    subprocess.run([
        "ffmpeg", "-y", "-v", "quiet",
        "-f", "lavfi", "-i", "sine=frequency=220:duration=9.0:sample_rate=24000",
        "-c:a", "pcm_s16le", str(test_audio)
    ], check=True)

    test_cards = [
        {"start": 0.5, "end": 2.2, "text": "CHAPTER ONE BEGINS,", "highlight": "CHAPTER"},
        {"start": 2.5, "end": 4.5, "text": "THE MOMENT CAP CAUGHT MJOLNIR,", "highlight": "MJOLNIR"},
        {"start": 5.0, "end": 6.8, "text": "THE BALANCE OF POWER SHIFTED,", "highlight": "POWER"},
        {"start": 7.0, "end": 8.8, "text": "REVEALING THE ULTIMATE TRUTH.", "highlight": "TRUTH"}
    ]
    test_ass = TEMP_LONG_DIR / "test_widescreen_lower_third.ass"
    build_ass_subtitles(test_cards, str(test_ass), video_format="LONG_5_6_MIN")

    # 5. Assemble 1080p Widescreen Master
    print("\n>>> [CHECK 4/5] Assembling 1080p Widescreen Master (with procedural score mix & subtitles)...")
    out_1080p = FINAL_LONG_DIR / "test_long_xray_1080p.mp4"
    assemble_long_form_video(
        clip_paths=[str(clip1), str(clip2)],
        voiceover_wav_path=str(test_audio),
        ass_subtitle_path=str(test_ass),
        output_1080p_path=str(out_1080p),
        temp_dir=str(TEMP_LONG_DIR)
    )

    meta_1080p = gatekeeper_verify_long_video(out_1080p, expected_duration=9.0)
    print(f"✅ Verified 1080p Master: {out_1080p.name}")
    print(f"   Resolution: {meta_1080p['width']}x{meta_1080p['height']} | DAR: {meta_1080p['aspect_ratio']} | Duration: {meta_1080p['duration']:.2f}s | Audio: {meta_1080p['codec_audio']}\n")

    # 6. Export Horizontal 4K UHD Master (3840x2160)
    print(">>> [CHECK 5/5] Exporting Horizontal 4K UHD Master (3840x2160)...")
    out_4k = FINAL_LONG_DIR / "test_long_xray_4k.mp4"
    export_long_form_4k_uhd(str(out_1080p), str(out_4k))

    meta_4k = gatekeeper_verify_long_video(out_4k, expected_duration=9.0)
    print(f"✅ Verified 4K UHD Master: {out_4k.name}")
    print(f"   Resolution: {meta_4k['width']}x{meta_4k['height']} | DAR: {meta_4k['aspect_ratio']} | Duration: {meta_4k['duration']:.2f}s | Codec: {meta_4k['codec_video']}\n")

    print("================================================================================")
    print("🎉 STEP 3 VERIFICATION COMPLETE: ALL ISOLATION & GATEKEEPER CHECKS PASSED!")
    print(f"  • Isolated Clips  : {CLIPS_LONG_DIR.relative_to(REPO_ROOT)}")
    print(f"  • Isolated Temp   : {TEMP_LONG_DIR.relative_to(REPO_ROOT)}")
    print(f"  • Isolated Output : {FINAL_LONG_DIR.relative_to(REPO_ROOT)}")
    print(f"  • 1080p Master    : {out_1080p.name} ({meta_1080p['width']}x{meta_1080p['height']})")
    print(f"  • 4K UHD Master   : {out_4k.name} ({meta_4k['width']}x{meta_4k['height']})")
    print(f"  • Shorts Pipeline : 100% untouched (git diff pipeline/video_compositor.py: clean)")
    print("================================================================================")


if __name__ == "__main__":
    run_step3_verification()
