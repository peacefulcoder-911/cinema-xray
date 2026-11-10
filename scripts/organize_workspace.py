#!/usr/bin/env python3
"""
Workspace Organizer & Pruner for Cinema X-Ray
Restructures cinema-xray into a clean, professional architecture:
1. Moves test scripts from root into tests/ with corrected relative paths.
2. Moves utility & downloader scripts from root into scripts/.
3. Consolidates Doctor Strange Remotion components into projects/cinema-decoded-doctor-strange-watch/.
4. Prunes obsolete draft and legacy prototype folders from projects/.
5. Removes empty subdirectories across projects/, assets/, and output/.
6. Cleans obsolete voice tests and frame dumps.
"""

import os
import shutil
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def fix_repo_root_in_file(file_path: Path, old_pattern: str, new_pattern: str):
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            file_path.write_text(new_content, encoding="utf-8")
            print(f"  Updated REPO_ROOT in {file_path.name}")

def organize():
    print("=" * 70)
    print("🧹 CINEMA X-RAY: WORKSPACE ORGANIZER & PRUNER")
    print("=" * 70)

    tests_dir = REPO_ROOT / "tests"
    scripts_dir = REPO_ROOT / "scripts"
    projects_dir = REPO_ROOT / "projects"
    output_dir = REPO_ROOT / "output"
    assets_dir = REPO_ROOT / "assets"

    tests_dir.mkdir(exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)

    # 1. Move test scripts into tests/
    print("\n📂 1. Organizing Test Scripts -> tests/")
    test_files = [
        "test_step1_step2.py",
        "test_step2_audio_subtitles.py",
        "test_step3_long_compositor.py",
        "test_step4_packaging.py"
    ]
    for tf in test_files:
        src = REPO_ROOT / tf
        dst = tests_dir / tf
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"  Moved {tf} -> tests/{tf}")
            # Fix REPO_ROOT definition
            fix_repo_root_in_file(dst, "REPO_ROOT = Path(__file__).resolve().parent", "REPO_ROOT = Path(__file__).resolve().parent.parent")

    # 2. Move utility & downloader scripts into scripts/
    print("\n📂 2. Organizing Utility Scripts -> scripts/")
    script_files = [
        "benchmark_kgf_production.py",
        "download_the_thing_clips.py",
        "download_true_hd_clips.py",
        "download_truman_clips.py",
        "generate_custom_short.py"
    ]
    for sf in script_files:
        src = REPO_ROOT / sf
        dst = scripts_dir / sf
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"  Moved {sf} -> scripts/{sf}")
            fix_repo_root_in_file(dst, "REPO_ROOT = Path(__file__).resolve().parent", "REPO_ROOT = Path(__file__).resolve().parent.parent")

    # 3. Consolidate Doctor Strange breakdown
    print("\n📂 3. Consolidating Doctor Strange Project")
    ds_root = REPO_ROOT / "doctor-strange-breakdown"
    ds_target = projects_dir / "cinema-decoded-doctor-strange-watch"
    if ds_root.exists() and ds_target.exists():
        # Copy src if present
        src_dir = ds_root / "src"
        if src_dir.exists():
            target_src = ds_target / "src"
            if target_src.exists():
                shutil.rmtree(target_src)
            shutil.copytree(src_dir, target_src)
            print("  Merged Remotion src/ into projects/cinema-decoded-doctor-strange-watch/src/")

        # Copy approved-script if present
        script_dir = ds_root / "script"
        if script_dir.exists():
            target_script = ds_target / "script"
            target_script.mkdir(exist_ok=True)
            for f in script_dir.glob("*"):
                shutil.copy2(f, target_script / f.name)
            print("  Merged script/ into projects/cinema-decoded-doctor-strange-watch/script/")

        # Copy qc-report if present
        qc_rep = ds_root / "output" / "qc-report.md"
        if qc_rep.exists():
            shutil.copy2(qc_rep, ds_target / "qc-report.md")
            print("  Copied qc-report.md into projects/cinema-decoded-doctor-strange-watch/")

        # Delete loose root folder
        shutil.rmtree(ds_root)
        print("  Removed redundant doctor-strange-breakdown/ from workspace root")

    # 4. Prune obsolete / draft projects in projects/
    print("\n📂 4. Pruning Obsolete & Duplicate Projects")
    obsolete_projects = [
        "cinema-decoded-matrix_neo_free_will",
        "cinema-decoded-neo_choice_matrix_deception",
        "cinema-decoded-inception_real_totem",
        "interstellar-decoded",
        "marvel-decoded"
    ]
    for op in obsolete_projects:
        p = projects_dir / op
        if p.exists():
            shutil.rmtree(p)
            print(f"  Removed obsolete project: projects/{op}")

    # 5. Clean empty subdirectories in projects/
    print("\n📂 5. Cleaning Empty Subdirectories Across Projects")
    cleaned_subdirs = 0
    for p in projects_dir.iterdir():
        if p.is_dir():
            for sub in ["clips", "out", "audio", "audio_test", "temp_tts", "raw_clips", "thumb_inspect", "__pycache__"]:
                sub_path = p / sub
                if sub_path.exists() and sub_path.is_dir():
                    # check if empty
                    if not any(sub_path.iterdir()):
                        sub_path.rmdir()
                        cleaned_subdirs += 1
    print(f"  Removed {cleaned_subdirs} empty intermediate subdirectories in projects/")

    # 6. Clean root temp_tts
    root_temp_tts = REPO_ROOT / "temp_tts"
    if root_temp_tts.exists():
        if not any(root_temp_tts.iterdir()):
            root_temp_tts.rmdir()
            print("  Removed empty temp_tts/ from workspace root")
        else:
            shutil.rmtree(root_temp_tts)
            print("  Purged temp_tts/ from workspace root")

    # 7. Clean obsolete voice tests & temp in output/
    print("\n📂 6. Cleaning Obsolete Voice Tests & Temp Scratch in output/")
    voice_tests = output_dir / "voice_tests"
    if voice_tests.exists():
        shutil.rmtree(voice_tests)
        print("  Removed output/voice_tests/ (54 MB of obsolete voice trials)")

    test_wav = output_dir / "test_elevenlabs.wav"
    if test_wav.exists():
        test_wav.unlink()
        print("  Removed output/test_elevenlabs.wav")

    for sub in ["clip_cache", "temp", "qc_verification", "audio", "clips", "final_video"]:
        sub_path = output_dir / sub
        if sub_path.exists() and sub_path.is_dir() and not any(sub_path.iterdir()):
            sub_path.rmdir()
            print(f"  Removed empty output/{sub}")

    # 8. Clean temporary inspection frames in assets/
    print("\n📂 7. Cleaning Temporary Inspection Frame Dumps in assets/")
    spiderman_frames = assets_dir / "source" / "spiderman_brand_new_day" / "frames"
    if spiderman_frames.exists():
        shutil.rmtree(spiderman_frames)
        print("  Removed assets/source/spiderman_brand_new_day/frames/")

    fight_frames = assets_dir / "footage" / "fight_club" / "tyler_hidden_appearances" / "exact_frames"
    if fight_frames.exists():
        shutil.rmtree(fight_frames)
        print("  Removed assets/footage/fight_club/tyler_hidden_appearances/exact_frames/")

    fight_flashes = assets_dir / "footage" / "fight_club" / "tyler_hidden_appearances" / "flashes_inspection"
    if fight_flashes.exists():
        shutil.rmtree(fight_flashes)
        print("  Removed assets/footage/fight_club/tyler_hidden_appearances/flashes_inspection/")

    # Remove empty directories in assets
    empty_asset_dirs = 0
    for root, dirs, files in os.walk(assets_dir, topdown=False):
        for d in dirs:
            dp = Path(root) / d
            try:
                if not any(dp.iterdir()):
                    dp.rmdir()
                    empty_asset_dirs += 1
            except Exception:
                pass
    print(f"  Removed {empty_asset_dirs} empty subdirectories in assets/")

    print("\n" + "=" * 70)
    print("✅ WORKSPACE REORGANIZATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    organize()
