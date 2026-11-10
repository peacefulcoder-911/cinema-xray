#!/usr/bin/env python3
"""
Deep Media Asset Cleaner for Cinema X-Ray
Safely purges heavy video files, audio tracks, intermediate clips, source footage,
and downloaded CI archives while strictly protecting code, scene plans,
subtitles, database records, and thumbnails.
"""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def deep_clean():
    freed_bytes = 0
    deleted_count = 0

    def delete_file(p: Path):
        nonlocal freed_bytes, deleted_count
        if p.exists() and p.is_file():
            sz = p.stat().st_size
            try:
                p.unlink()
                freed_bytes += sz
                deleted_count += 1
            except Exception as e:
                print(f"Error removing {p}: {e}")

    def delete_dir(p: Path):
        nonlocal freed_bytes, deleted_count
        if p.exists() and p.is_dir():
            for root, dirs, files in os.walk(p):
                for f in files:
                    fp = Path(root) / f
                    try:
                        sz = fp.stat().st_size
                        freed_bytes += sz
                        deleted_count += 1
                    except Exception:
                        pass
            try:
                shutil.rmtree(p)
            except Exception as e:
                print(f"Error removing directory {p}: {e}")

    # 1. Video files across outputs, projects, and assets
    video_exts = ["*.mp4", "*.mkv", "*.webm", "*.mov", "*.avi"]
    for ext in video_exts:
        for p in (REPO_ROOT / "output").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "projects").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "assets").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "doctor-strange-breakdown").rglob(ext):
            delete_file(p)

    # 2. Audio files
    audio_exts = ["*.wav", "*.mp3", "*.aac", "*.flac", "*.m4a"]
    for ext in audio_exts:
        for p in (REPO_ROOT / "projects").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "assets").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "doctor-strange-breakdown").rglob(ext):
            delete_file(p)
        for p in (REPO_ROOT / "temp_tts").rglob(ext):
            delete_file(p)

    # 3. Old CI run directories & artifact zips
    for p in REPO_ROOT.glob("downloaded_ci_run_*"):
        if p.is_dir():
            delete_dir(p)
        elif p.is_file():
            delete_file(p)

    for p in REPO_ROOT.glob("downloaded_artifacts*"):
        if p.is_dir():
            delete_dir(p)
        elif p.is_file():
            delete_file(p)

    # 4. Clip cache and temp scratch
    for p in (REPO_ROOT / "output" / "clip_cache").glob("*"):
        delete_file(p)
    for p in (REPO_ROOT / "output" / "temp").rglob("*"):
        delete_file(p)
    for p in (REPO_ROOT / "output" / "qc_verification").glob("*"):
        delete_file(p)

    print("=" * 70)
    print(f"🧹 DEEP CLEANUP COMPLETE: {deleted_count} files removed.")
    print(f"💾 Total Space Freed: {freed_bytes / (1024**3):.2f} GB ({freed_bytes / (1024**2):.1f} MB)")
    print("=" * 70)

if __name__ == "__main__":
    deep_clean()
