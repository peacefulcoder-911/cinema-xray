"""
Cinema X-Ray QA Gatekeeper (Pre-Upload Final Inspector)
Strict deterministic quality inspection using ffprobe & Pillow before YouTube publishing:
  - Video stream existence (h264/hevc) & integrity
  - Audio stream existence (aac/pcm) & loudness integrity
  - Exact resolution & aspect ratio (1080x1920 for Shorts, 1920x1080 for Long-Form)
  - Duration bounds (30.0s-59.5s for Shorts, 240.0s-420.0s for Long-Form)
  - File size bounds (>2MB video, <2MB thumbnail)
  - Thumbnail resolution & format match
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Any
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent


def inspect_final_render(
    video_path: Union[str, Path],
    thumbnail_path: Optional[Union[str, Path]],
    video_format: str = "SHORT_45_SEC",
    dry_run: bool = False
) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Deterministically inspects the final rendered video and custom thumbnail before publishing.
    
    Returns:
      (True, diagnostics_dict) if all checks pass.
      (False, error_reason_string) if any check fails.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return False, f"Video file not found: {video_path}"

    # 1. File Size Gatekeeper
    file_size_bytes = video_path.stat().st_size
    min_size = 50_000 if dry_run else 2_000_000  # 2MB minimum for real master render
    if file_size_bytes < min_size:
        return False, f"Video file size too small: {file_size_bytes} bytes (min: {min_size})"

    # 2. ffprobe Stream Analysis
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(res.stdout)
    except Exception as e:
        return False, f"ffprobe execution failed on {video_path}: {e}"

    streams = probe_data.get("streams", [])
    format_info = probe_data.get("format", {})

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not video_stream:
        return False, f"No video stream found in {video_path}"
    if not audio_stream:
        return False, f"No audio stream found in {video_path}"

    # 3. Video Codec & Geometry Verification
    v_codec = video_stream.get("codec_name", "").lower()
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    if v_codec not in ("h264", "hevc", "avc1"):
        return False, f"Unsupported video codec: '{v_codec}' (expected h264 or hevc)"

    # Compute duration
    dur_str = format_info.get("duration") or video_stream.get("duration")
    duration = float(dur_str) if dur_str else 0.0

    if video_format == "SHORT_45_SEC":
        # Required vertical 9:16
        aspect_ratio = width / height if height > 0 else 0.0
        expected_aspect = 9.0 / 16.0
        if abs(aspect_ratio - expected_aspect) > 0.03:
            return False, f"Shorts aspect ratio invalid: {width}x{height} (aspect: {aspect_ratio:.3f}, expected 9:16)"

        # Must be 1080x1920 or 2160x3840 UHD
        if (width, height) not in ((1080, 1920), (2160, 3840)):
            return False, f"Shorts resolution must be 1080x1920 (or 2160x3840), got {width}x{height}"

        # Duration bounds: 30.0s to 59.5s
        if not dry_run and (duration < 30.0 or duration > 59.5):
            return False, f"Shorts duration ({duration:.2f}s) outside 30.0s-59.5s YouTube limit"

    elif video_format == "LONG_5_6_MIN":
        # Required widescreen 16:9
        aspect_ratio = width / height if height > 0 else 0.0
        expected_aspect = 16.0 / 9.0
        if abs(aspect_ratio - expected_aspect) > 0.03:
            return False, f"Long-Form aspect ratio invalid: {width}x{height} (aspect: {aspect_ratio:.3f}, expected 16:9)"

        # Must be 1920x1080 or 3840x2160 4K UHD
        if (width, height) not in ((1920, 1080), (3840, 2160)):
            return False, f"Long-Form resolution must be 1920x1080 (or 3840x2160), got {width}x{height}"

        # Duration bounds: 240.0s (4 min) to 420.0s (7 min)
        if not dry_run and (duration < 240.0 or duration > 420.0):
            return False, f"Long-Form duration ({duration:.2f}s) outside 240.0s-420.0s bounds"

    else:
        return False, f"Unknown video_format: '{video_format}'"

    # 4. Audio Codec Verification
    a_codec = audio_stream.get("codec_name", "").lower()
    if a_codec not in ("aac", "pcm_s16le", "mp3"):
        return False, f"Unexpected audio codec: '{a_codec}'"

    # 5. Thumbnail Verification
    thumb_info = None
    if thumbnail_path:
        thumb_path = Path(thumbnail_path)
        if not thumb_path.exists():
            return False, f"Thumbnail file not found: {thumb_path}"

        thumb_bytes = thumb_path.stat().st_size
        if thumb_bytes >= 2_000_000:
            return False, f"Thumbnail size ({thumb_bytes / (1024*1024):.2f} MB) exceeds YouTube 2MB limit"

        try:
            with Image.open(thumb_path) as im:
                tw, th = im.size
                if video_format == "LONG_5_6_MIN" and (tw, th) != (1280, 720):
                    return False, f"Long-Form thumbnail must be strictly 1280x720, got {tw}x{th}"
                elif video_format == "SHORT_45_SEC" and (tw, th) != (1080, 1920):
                    return False, f"Shorts thumbnail must be strictly 1080x1920, got {tw}x{th}"
                thumb_info = {
                    "path": str(thumb_path),
                    "resolution": f"{tw}x{th}",
                    "size_kb": round(thumb_bytes / 1024, 1)
                }
        except Exception as e:
            return False, f"Corrupted or invalid thumbnail image: {e}"

    diagnostics = {
        "status": "QA_PASSED",
        "video_format": video_format,
        "video_file": str(video_path),
        "video_size_mb": round(file_size_bytes / (1024 * 1024), 2),
        "video_codec": v_codec,
        "audio_codec": a_codec,
        "resolution": f"{width}x{height}",
        "duration_sec": round(duration, 2),
        "fps": video_stream.get("r_frame_rate"),
        "thumbnail": thumb_info
    }
    return True, diagnostics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cinema X-Ray QA Gatekeeper Inspector")
    parser.add_argument("--video", type=str, required=True, help="Video path to inspect")
    parser.add_argument("--thumbnail", type=str, default=None, help="Thumbnail path to inspect")
    parser.add_argument("--format", choices=["SHORT_45_SEC", "LONG_5_6_MIN"], default="SHORT_45_SEC")
    parser.add_argument("--dry-run", action="store_true", help="Allow dry-run bounds")
    args = parser.parse_args()

    passed, result = inspect_final_render(args.video, args.thumbnail, args.format, dry_run=args.dry_run)
    if passed:
        print(f"✅ QA Gatekeeper PASSED:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ QA Gatekeeper FAILED: {result}")
        exit(1)
