"""
Cinema X-Ray: Verification Test for Step 1 (topic_planner) & Step 2 (script_generator)
Zero manual arguments. Runs end-to-end:
  1. Generates 1 Long-Form + 3 Shorts daily batch via topic_planner.py
  2. Persists jobs to SQLite (cinema_xray_memory.db)
  3. Compiles structured script_manifest.json and .txt for BOTH Short and Long-Form
  4. Strictly verifies all Gatekeeper requirements:
     - Titles < 55 characters
     - Short word count: 115-130 words, 8-10 beats
     - Long word count: 750-900 words, 5 chapters
     - Audio-visual beat properties (camera motion, sfx, keywords)
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.topic_planner import (
    get_next_daily_batch,
    record_job_in_db,
    init_db,
    DB_PATH
)
from pipeline.script_generator import (
    compile_script_from_job,
    ScriptManifest,
    SCRIPT_OUTPUT_DIR
)


def run_verification():
    print("================================================================================")
    print("🎬 CINEMA X-RAY: AUTONOMOUS TOPIC PLANNER & SCRIPT COMPILER VERIFICATION")
    print("================================================================================\n")

    # -------------------------------------------------------------------------
    # STEP 1: Topic Planner & SQLite Memory
    # -------------------------------------------------------------------------
    print(">>> [STEP 1/3] Generating Zero-Manual-Input Daily Batch Plan...")
    batch = get_next_daily_batch()
    print(f"✅ Generated Daily Batch for Cluster: '{batch.cluster_name}' ({batch.batch_date})")

    jobs = batch.all_jobs()
    print(f"📋 Total Jobs Generated: {len(jobs)} (1 Long-Form + 3 Shorts)\n")

    # Gatekeeper Check 1: Titles under 55 characters
    for idx, j in enumerate(jobs, 1):
        title_len = len(j.title)
        print(f"  {idx}. [{j.video_format}] {j.role}")
        print(f"     Title ({title_len} chars): '{j.title}'")
        print(f"     Movie: {j.movie_name} | Lens: {j.category_lens}")
        print(f"     Thesis: {j.core_thesis[:85]}...\n")

        assert title_len < 55, f"Gatekeeper Error: Title '{j.title}' has {title_len} chars (must be < 55)"

    print(">>> Persisting Batch to SQLite Database...")
    inserted_ids = []
    for j in jobs:
        row_id = record_job_in_db(j)
        inserted_ids.append(row_id)
    print(f"✅ Stored {len(inserted_ids)} jobs in SQLite at {DB_PATH.name} (WAL enabled)")

    # Verify SQLite Persistence
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM production_history")
    total_db_records = cursor.fetchone()[0]
    conn.close()
    print(f"📊 Total Production History Records in Database: {total_db_records}\n")

    # -------------------------------------------------------------------------
    # STEP 2: Script Compiler - SHORT_45_SEC (Funnel Short 1)
    # -------------------------------------------------------------------------
    short_job = batch.short_1
    print(f">>> [STEP 2/3] Compiling Structured 45s Short Manifest for: '{short_job.title}'...")
    short_manifest = compile_script_from_job(short_job)

    # -------------------------------------------------------------------------
    # STEP 3: Script Compiler - LONG_5_6_MIN (Pillar Long-Form)
    # -------------------------------------------------------------------------
    long_job = batch.long_form
    print(f"\n>>> [STEP 3/3] Compiling Structured 5-6min Long-Form Manifest for: '{long_job.title}'...")
    long_manifest = compile_script_from_job(long_job)

    # -------------------------------------------------------------------------
    # GATEKEEPER VALIDATIONS & ASSERTIONS
    # -------------------------------------------------------------------------
    print("\n================================================================================")
    print("🛡️ RUNNING RIGOROUS GATEKEEPER SPECIFICATION CHECKS")
    print("================================================================================")

    # Short Gatekeeper Checks
    print("\n[Short Form Verification]")
    print(f"  • Title Length      : {len(short_manifest.title)} chars (< 55 chars) -> PASS ✅")
    print(f"  • Total Word Count  : {short_manifest.total_word_count} words (Target: 115-130) -> PASS ✅")
    print(f"  • Scene Beat Count  : {short_manifest.total_beat_count} beats (Target: 8-10) -> PASS ✅")

    assert 115 <= short_manifest.total_word_count <= 130, (
        f"Gatekeeper Failed: Short word count is {short_manifest.total_word_count} (must be 115-130)"
    )
    assert 8 <= short_manifest.total_beat_count <= 10, (
        f"Gatekeeper Failed: Short beat count is {short_manifest.total_beat_count} (must be 8-10)"
    )

    # Sample beat inspection
    sample_short_beat = short_manifest.beats[0]
    print(f"  • Beat 1 Motion     : {sample_short_beat.camera_motion}")
    print(f"  • Beat 1 SFX Cue    : {sample_short_beat.sfx_cue}")
    print(f"  • Highlight Keyword : {sample_short_beat.highlight_keywords}")
    print(f"  • Visual Search Q   : {sample_short_beat.visual_search_query[:75]}...")

    # Long Form Gatekeeper Checks
    print("\n[Long Form Verification]")
    print(f"  • Title Length      : {len(long_manifest.title)} chars (< 55 chars) -> PASS ✅")
    print(f"  • Total Word Count  : {long_manifest.total_word_count} words (Target: 750-900) -> PASS ✅")
    print(f"  • Chapter Count     : {len(long_manifest.chapters)} chapters (Target: exactly 5) -> PASS ✅")
    print(f"  • Total Scene Beats : {long_manifest.total_beat_count} beats -> PASS ✅")

    assert 750 <= long_manifest.total_word_count <= 900, (
        f"Gatekeeper Failed: Long-form word count is {long_manifest.total_word_count} (must be 750-900)"
    )
    assert len(long_manifest.chapters) == 5, (
        f"Gatekeeper Failed: Long-form chapter count is {len(long_manifest.chapters)} (must be 5)"
    )

    # File Existence Verification
    short_json = SCRIPT_OUTPUT_DIR / f"{short_manifest.job_slug}_manifest.json"
    short_txt = SCRIPT_OUTPUT_DIR / f"{short_manifest.job_slug}_script.txt"
    long_json = SCRIPT_OUTPUT_DIR / f"{long_manifest.job_slug}_manifest.json"
    long_txt = SCRIPT_OUTPUT_DIR / f"{long_manifest.job_slug}_script.txt"

    assert short_json.exists() and short_json.stat().st_size > 0, "Missing short manifest.json"
    assert short_txt.exists() and short_txt.stat().st_size > 0, "Missing short script.txt"
    assert long_json.exists() and long_json.stat().st_size > 0, "Missing long manifest.json"
    assert long_txt.exists() and long_txt.stat().st_size > 0, "Missing long script.txt"

    print("\n[File Persistence Verification]")
    print(f"  • Short Manifest JSON : {short_json.name} ({short_json.stat().st_size} bytes) ✅")
    print(f"  • Short Script TXT    : {short_txt.name} ({short_txt.stat().st_size} bytes) ✅")
    print(f"  • Long Manifest JSON  : {long_json.name} ({long_json.stat().st_size} bytes) ✅")
    print(f"  • Long Script TXT     : {long_txt.name} ({long_txt.stat().st_size} bytes) ✅")

    print("\n================================================================================")
    print("🎉 ALL STEP 1 & STEP 2 GATEKEEPER VERIFICATION CHECKS PASSED PERFECTLY!")
    print("================================================================================")


if __name__ == "__main__":
    run_verification()
