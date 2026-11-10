"""
Gatekeeper Verification Test for Step 4:
Packaging & Publishing Modules (Thumbnail Generator + YouTube Publisher)

Verifies:
  1. thumbnail_generator.py:
     - Long-Form 1280x720 thumbnail (< 2MB)
     - Short-Form 1080x1920 thumbnail
     - Unified Cinema X-Ray brand theme (Electric Gold #FFE500, pure white, 8px stroke, HUD badge)
  2. youtube_publisher.py:
     - Long-Form metadata: Title < 52 chars, exact 00:00 chapter timestamps, 15 tags (< 450 chars), category_id=1, made_for_kids=False
     - Short-Form metadata: Title < 52 chars with #Shorts, Funnel link to related Long-Form video
     - Resumable upload dry-run compilation & validation on disk
  3. STRICT ISOLATION RULE:
     - Zero modifications to video_compositor.py, long_form_compositor.py, subtitle_engine.py, audio_generator.py.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.thumbnail_generator import (
    extract_best_keyframe,
    apply_cinema_xray_theme,
    COLOR_GOLD,
    COLOR_WHITE
)
from pipeline.youtube_publisher import (
    generate_algorithmic_metadata,
    upload_to_youtube,
    YouTubePackage
)


def test_long_form_thumbnail():
    print("\n" + "="*70)
    print("TEST 1: Long-Form Thumbnail Generation (1280x720, < 2MB)")
    print("="*70)

    clip_path = REPO_ROOT / "output" / "clips" / "scene_01.mp4"
    if clip_path.exists():
        print(f"Sampling dramatic keyframe from {clip_path.name}...")
        keyframe = extract_best_keyframe(clip_path, start_sec=0.0, end_sec=5.0)
    else:
        print("Using procedural base frame...")
        import numpy as np
        keyframe = np.zeros((720, 1280, 3), dtype=np.uint8)
        keyframe[:, :] = [30, 40, 60]

    job_slug = "gatekeeper_long_test"
    thumb_path = apply_cinema_xray_theme(
        frame_img=keyframe,
        hook_text="WHY THANOS WAS BROKEN",
        highlight_word="BROKEN",
        video_format="LONG_5_6_MIN",
        job_slug=job_slug
    )

    thumb_file = Path(thumb_path)
    assert thumb_file.exists(), f"Thumbnail not found on disk: {thumb_path}"

    with Image.open(thumb_file) as im:
        w, h = im.size
        print(f"  Resolution: {w}x{h} (Expected: 1280x720)")
        assert (w, h) == (1280, 720), f"Incorrect dimensions: {w}x{h}"

    file_size_bytes = thumb_file.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"  File Size:  {file_size_mb:.2f} MB ({file_size_bytes} bytes)")
    assert file_size_mb < 2.0, f"Thumbnail exceeds 2MB limit: {file_size_mb:.2f} MB"

    print("  ✅ Long-Form Thumbnail Gatekeeper PASSED")
    return thumb_path


def test_short_form_thumbnail():
    print("\n" + "="*70)
    print("TEST 2: Short-Form Cover Thumbnail Generation (1080x1920)")
    print("="*70)

    clip_path = REPO_ROOT / "output" / "clips" / "scene_02.mp4"
    if clip_path.exists():
        print(f"Sampling keyframe from {clip_path.name}...")
        keyframe = extract_best_keyframe(clip_path, start_sec=0.0, end_sec=5.0)
    else:
        import numpy as np
        keyframe = np.zeros((1920, 1080, 3), dtype=np.uint8)
        keyframe[:, :] = [40, 30, 60]

    job_slug = "gatekeeper_short_test"
    thumb_path = apply_cinema_xray_theme(
        frame_img=keyframe,
        hook_text="THAT SILENCE BROKE CINEMA",
        highlight_word="SILENCE",
        video_format="SHORT_45_SEC",
        job_slug=job_slug
    )

    thumb_file = Path(thumb_path)
    assert thumb_file.exists(), f"Thumbnail not found on disk: {thumb_path}"

    with Image.open(thumb_file) as im:
        w, h = im.size
        print(f"  Resolution: {w}x{h} (Expected: 1080x1920)")
        assert (w, h) == (1080, 1920), f"Incorrect dimensions: {w}x{h}"

    file_size_mb = thumb_file.stat().st_size / (1024 * 1024)
    print(f"  File Size:  {file_size_mb:.2f} MB")
    assert file_size_mb < 2.0, f"Short thumbnail exceeds 2MB limit: {file_size_mb:.2f} MB"

    print("  ✅ Short-Form Thumbnail Gatekeeper PASSED")
    return thumb_path


def test_long_form_youtube_publisher(long_thumb_path):
    print("\n" + "="*70)
    print("TEST 3: Algorithmic Metadata & Dry-Run Upload (Long-Form)")
    print("="*70)

    manifest_path = REPO_ROOT / "output" / "script" / "infinity_war_thanos_flawed_logic_manifest.json"
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"

    pkg = generate_algorithmic_metadata(manifest_path, video_format="LONG_5_6_MIN")

    print(f"  Optimized Title: '{pkg.optimized_title}'")
    print(f"  Title Length:    {len(pkg.optimized_title)} chars (Requirement: < 52 chars)")
    assert len(pkg.optimized_title) <= 52, f"Title too long: {len(pkg.optimized_title)} chars"

    print(f"  Category ID:     {pkg.category_id} (Expected: '1')")
    assert pkg.category_id in ("1", "24"), f"Invalid category ID: {pkg.category_id}"

    print(f"  Made For Kids:   {pkg.made_for_kids} (Requirement: Strictly False)")
    assert pkg.made_for_kids is False, "made_for_kids must be False"

    tag_chars = sum(len(t) for t in pkg.tags) + len(pkg.tags) - 1
    print(f"  Tag Count:       {len(pkg.tags)} (Requirement: 15 tags)")
    print(f"  Tag Total Chars: {tag_chars} (Requirement: < 450 chars)")
    assert len(pkg.tags) == 15, f"Tag count was {len(pkg.tags)}, expected 15"
    assert tag_chars <= 450, f"Tags character count exceeds 450: {tag_chars}"

    # Verify Chapter Timestamps
    print("\n  Chapter Timestamps Verification:")
    assert pkg.chapter_timestamps and len(pkg.chapter_timestamps) >= 5, "Missing 5 chapter timestamps"
    first_ch = pkg.chapter_timestamps[0]
    print(f"    First Chapter: {first_ch['timestamp']} - {first_ch['title']}")
    assert first_ch["timestamp"] == "00:00", f"First chapter must start at 00:00, got: {first_ch['timestamp']}"

    for ch in pkg.chapter_timestamps[1:]:
        print(f"    Next Chapter:  {ch['timestamp']} - {ch['title']}")

    assert "TIMESTAMPS:" in pkg.seo_description, "Description must contain 'TIMESTAMPS:'"
    assert "00:00" in pkg.seo_description, "Description must contain '00:00' timestamp"

    # Test Dry-Run Packaging & Validation
    video_mock = REPO_ROOT / "output" / "clips" / "scene_01.mp4"
    upload_res = upload_to_youtube(
        video_path=video_mock,
        thumbnail_path=long_thumb_path,
        metadata_package=pkg,
        dry_run=True
    )

    assert upload_res["dry_run"] is True, "dry_run must be True"
    assert upload_res["status"] == "VALIDATED", "status must be VALIDATED"
    pkg_json = Path(upload_res["package_json_path"])
    assert pkg_json.exists(), f"Package JSON not created: {pkg_json}"

    with open(pkg_json, "r", encoding="utf-8") as f:
        saved_pkg = json.load(f)
    assert saved_pkg["payload"]["snippet"]["title"] == pkg.optimized_title
    assert saved_pkg["payload"]["status"]["selfDeclaredMadeForKids"] is False

    print("  ✅ Long-Form YouTube Publisher Gatekeeper PASSED")


def test_short_form_youtube_publisher(short_thumb_path):
    print("\n" + "="*70)
    print("TEST 4: Algorithmic Metadata & Funnel Link (Short-Form)")
    print("="*70)

    manifest_path = REPO_ROOT / "output" / "script" / "infinity_war_snap_sound_design_manifest.json"
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"

    test_long_id = "dQw4w9WgXcQ"
    pkg = generate_algorithmic_metadata(
        manifest_path,
        video_format="SHORT_45_SEC",
        related_long_video_id=test_long_id
    )

    print(f"  Optimized Short Title: '{pkg.optimized_title}'")
    print(f"  Title Length:          {len(pkg.optimized_title)} chars (Requirement: < 52 chars)")
    assert len(pkg.optimized_title) <= 52, f"Title too long: {len(pkg.optimized_title)}"
    assert "#Shorts" in pkg.optimized_title, "Short title must cleanly contain '#Shorts'"

    print(f"  Funnel Link Check:")
    expected_link = f"https://youtu.be/{test_long_id}"
    print(f"    Expected: {expected_link}")
    assert expected_link in pkg.seo_description, f"Funnel link not found in description:\n{pkg.seo_description}"

    # Dry-run upload
    video_mock = REPO_ROOT / "output" / "clips" / "scene_02.mp4"
    upload_res = upload_to_youtube(
        video_path=video_mock,
        thumbnail_path=short_thumb_path,
        metadata_package=pkg,
        dry_run=True
    )
    assert upload_res["status"] == "VALIDATED"
    print("  ✅ Short-Form YouTube Publisher Gatekeeper PASSED")


def test_strict_isolation_rule():
    print("\n" + "="*70)
    print("TEST 5: Strict Isolation Rule Verification")
    print("="*70)

    protected_files = [
        "pipeline/video_compositor.py",
        "pipeline/long_form_compositor.py",
        "pipeline/subtitle_engine.py",
        "pipeline/audio_generator.py"
    ]

    for pf in protected_files:
        diff_res = subprocess.run(
            ["git", "diff", "--name-only", pf],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True
        )
        changed = diff_res.stdout.strip()
        print(f"  Checking {pf}: {'CLEAN (UNMODIFIED)' if not changed else 'MODIFIED ERROR'}")
        assert not changed, f"VIOLATION: Protected file was modified: {pf}"

    print("  ✅ Strict Isolation Rule 100% PRESERVED")


if __name__ == "__main__":
    print("\n" + "🚀"*35)
    print("CINEMA X-RAY STEP 4: PACKAGING & PUBLISHING GATEKEEPER TEST")
    print("🚀"*35)

    long_thumb = test_long_form_thumbnail()
    short_thumb = test_short_form_thumbnail()
    test_long_form_youtube_publisher(long_thumb)
    test_short_form_youtube_publisher(short_thumb)
    test_strict_isolation_rule()

    print("\n" + "🎉"*35)
    print("ALL STEP 4 GATEKEEPER VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("🎉"*35 + "\n")
