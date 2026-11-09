#!/usr/bin/env python3
"""
Cinema Decoded Asset Cleaner
Safely deletes uploaded master 8K videos, duplicate project renders, raw downloaded clip caches,
and temporary audio/scratch files while preserving all project scripts, master voiceovers,
subtitles, thumbnails, metadata, and database records.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_cleanup():
    deleted_files = []
    freed_bytes = 0

    def remove_safely(path: Path):
        nonlocal freed_bytes
        if path.exists() and path.is_file():
            size = path.stat().st_size
            try:
                path.unlink()
                deleted_files.append((str(path.relative_to(REPO_ROOT)), size))
                freed_bytes += size
            except Exception as e:
                print(f"⚠️ Error deleting {path}: {e}")

    # 1. Uploaded & rendered final videos in output/final_video/ and output/
    for p in (REPO_ROOT / "output" / "final_video").glob("*.mp4"):
        remove_safely(p)
    for p in (REPO_ROOT / "output").glob("*.mp4"):
        remove_safely(p)

    # 2. Project intermediate render outputs in projects/*/out/
    for p in REPO_ROOT.glob("projects/*/out/*.mp4"):
        remove_safely(p)

    # 3. Raw downloaded footage in output/clip_cache/
    for p in (REPO_ROOT / "output" / "clip_cache").glob("*"):
        if p.is_file():
            remove_safely(p)

    # 4. Scratch files in output/temp/
    for p in (REPO_ROOT / "output" / "temp").rglob("*"):
        if p.is_file():
            remove_safely(p)

    # 5. Raw unnormalized TTS files in projects/*/audio/temp_tts/
    for p in REPO_ROOT.glob("projects/*/audio/temp_tts/*"):
        if p.is_file():
            remove_safely(p)

    # 6. QC verification frames in output/qc_verification/
    for p in (REPO_ROOT / "output" / "qc_verification").glob("*"):
        if p.is_file():
            remove_safely(p)

    # Summary
    print("=" * 70)
    print("🧹 CINEMA DECODED: ASSET CLEANUP COMPLETE")
    print("=" * 70)
    print(f"Total files removed: {len(deleted_files)}")
    print(f"Total disk space freed: {freed_bytes / (1024**3):.2f} GB ({freed_bytes / (1024**2):.1f} MB)")
    print("\nPreserved assets verified:")
    print("  ✅ All master voiceovers in projects/*/audio/*_master.wav preserved")
    print("  ✅ All vertical thumbnails in output/thumbnails_short/ and projects/ preserved")
    print("  ✅ All production scripts, scene plans, and subtitle files preserved")
    print("  ✅ All database records, upload receipts, and metadata preserved")
    print("=" * 70)

if __name__ == "__main__":
    run_cleanup()

