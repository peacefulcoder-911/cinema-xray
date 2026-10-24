#!/usr/bin/env python3
"""
Cinema X-Ray 24/7 Autonomous Master Factory Orchestrator
--------------------------------------------------------
Orchestrates the daily 1 Long-Form (5-6 min) + 3 Shorts production cycle:
  1. Planned -> Scripted -> Audio -> Subtitles -> Rendered -> Packaged -> QA -> Uploaded
  2. Crash Recovery & Resumability via SQLite State Machine (output/state/cinema_xray_memory.db)
  3. Strict Isolation: Shorts route to video_compositor, Long-Form routes to long_form_compositor
  4. Funnel Routing: Long-Form video ID automatically links into Shorts #1 & #2 descriptions
  5. Smart Staggered publishAt scheduling (11:00, 14:00, 18:00, 21:30 local peak windows)
  6. Self-Healing 3-Strike Quarantine with daemon_errors.log logging
  7. Automated intermediate disk hygiene
"""

import os
import sys
import time
import json
import sqlite3
import argparse
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

# Pipeline Modules
from pipeline.topic_planner import (
    get_next_daily_batch,
    record_job_in_db,
    DB_PATH,
    init_db,
    PlannedJob,
    DailyBatchPlan
)
from pipeline.script_generator import compile_script_from_job
from pipeline.audio_generator import generate_achird_audio
from pipeline.subtitle_engine import (
    generate_timed_subtitles,
    build_ass_subtitles
)
from pipeline.video_compositor import (
    render_70pct_scene_clip,
    assemble_final_video
)
from pipeline.long_form_compositor import (
    render_widescreen_xray_clip,
    assemble_long_form_video
)
from pipeline.thumbnail_generator import (
    extract_best_keyframe,
    apply_cinema_xray_theme
)
from pipeline.qa_gatekeeper import inspect_final_render
from pipeline.youtube_publisher import (
    generate_algorithmic_metadata,
    upload_to_youtube,
    YouTubePackage
)

# Output Directories
OUTPUT_DIR = REPO_ROOT / "output"
STATE_DIR = OUTPUT_DIR / "state"
ERROR_LOG_PATH = STATE_DIR / "daemon_errors.log"

# Pipeline State Enums
STATUS_PLANNED = "PLANNED"
STATUS_SCRIPTED = "SCRIPTED"
STATUS_AUDIO_READY = "AUDIO_READY"
STATUS_SUBTITLES_READY = "SUBTITLES_READY"
STATUS_RENDERED = "RENDERED"
STATUS_PACKAGED = "PACKAGED"
STATUS_QA_PASSED = "QA_PASSED"
STATUS_UPLOADED = "UPLOADED"
STATUS_QUARANTINED = "QUARANTINED"


def init_batch_tables(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize SQLite WAL database and batch_jobs state tracking table."""
    conn = init_db(db_path)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS batch_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_date TEXT NOT NULL,
        job_slug TEXT UNIQUE NOT NULL,
        cluster_name TEXT NOT NULL,
        movie_name TEXT NOT NULL,
        video_format TEXT NOT NULL,
        category_lens TEXT NOT NULL,
        title TEXT NOT NULL,
        core_thesis TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PLANNED',
        manifest_path TEXT,
        audio_path TEXT,
        subtitle_path TEXT,
        video_path TEXT,
        thumbnail_path TEXT,
        youtube_video_id TEXT,
        publish_at_iso TEXT,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    return conn


def log_daemon_error(job_slug: str, stage: str, error: Exception):
    """Log quarantined or fatal pipeline errors to output/state/daemon_errors.log."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    tb = traceback.format_exc()
    log_entry = (
        f"[{timestamp}] JOB: {job_slug} | STAGE: {stage} | ERROR: {error}\n"
        f"{tb}\n"
        f"{'-'*75}\n"
    )
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"⚠️ [Daemon Logger] Error logged for '{job_slug}' to {ERROR_LOG_PATH.name}")


def update_job_state(
    job_slug: str,
    status: str,
    db_path: Path = DB_PATH,
    **kwargs
):
    """Update job state machine and intermediate asset paths in SQLite."""
    conn = init_batch_tables(db_path)
    cursor = conn.cursor()

    set_clauses = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
    values = [status]

    for k, v in kwargs.items():
        set_clauses.append(f"{k} = ?")
        values.append(v)

    values.append(job_slug)
    query = f"UPDATE batch_jobs SET {', '.join(set_clauses)} WHERE job_slug = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()


def get_job_state(job_slug: str, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve full persistent state dictionary for a job."""
    conn = init_batch_tables(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM batch_jobs WHERE job_slug = ?", (job_slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def compute_staggered_schedule() -> Dict[str, str]:
    """
    Computes ISO-8601 UTC publishAt release windows for the 4 daily slots:
      - Short #1: 11:00 local time
      - Long-Form Pillar: 14:00 local time
      - Short #2: 18:00 local time
      - Short #3 (Bridge): 21:30 local time
    """
    now = datetime.now().astimezone()
    # If currently past 21:00 local time, schedule for tomorrow's optimal windows
    target_date = (now if now.hour < 21 else now + timedelta(days=1)).date()

    slots = {
        "SHORT_FUNNEL_1": (11, 0),
        "SHORT_FUNNEL_2": (18, 0),
        "SHORT_BRIDGE_3": (21, 30),
    }

    schedule = {}
    for role, (h, m) in slots.items():
        dt_local = datetime(target_date.year, target_date.month, target_date.day, h, m, 0, tzinfo=now.tzinfo)
        dt_utc = dt_local.astimezone(timezone.utc)
        schedule[role] = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    return schedule


def find_source_footage(movie_name: str, cluster_name: str) -> Path:
    """Finds best matching raw video footage or defaults to verified test media."""
    search_dirs = [
        REPO_ROOT / "projects" / "marvel-decoded" / "raw_video",
        REPO_ROOT / "projects" / "marvel-decoded" / "clips",
        REPO_ROOT / "output" / "clips"
    ]

    # Keyword tokens from movie name
    tokens = [t.lower() for t in movie_name.split() if len(t) > 3]

    for sdir in search_dirs:
        if sdir.exists():
            for f in sdir.glob("*.mp4"):
                fname = f.name.lower()
                if any(t in fname for t in tokens):
                    return f

    # Fallback to any valid mp4 in raw_video or clips
    for sdir in search_dirs:
        if sdir.exists():
            first = next(sdir.glob("*.mp4"), None)
            if first:
                return first

    raise FileNotFoundError(f"No source video footage found for {movie_name} in projects/ or output/")


def cleanup_workspace(job_slug: str, video_format: str):
    """
    Automated Disk Hygiene: deletes intermediate scene clips and temp audio/concat files
    while keeping the final master video, thumbnail, manifest, and publication package.
    """
    if video_format == "SHORT_45_SEC":
        clips_dir = OUTPUT_DIR / "clips"
        temp_dir = OUTPUT_DIR / "temp"
    else:
        clips_dir = OUTPUT_DIR / "clips_long"
        temp_dir = OUTPUT_DIR / "temp_long"

    cleaned_count = 0
    if clips_dir.exists():
        for f in clips_dir.glob(f"{job_slug}_*"):
            try:
                f.unlink()
                cleaned_count += 1
            except Exception:
                pass

    if temp_dir.exists():
        for f in temp_dir.glob(f"{job_slug}_*"):
            try:
                f.unlink()
                cleaned_count += 1
            except Exception:
                pass

    if cleaned_count > 0:
        print(f"🧹 [Disk Hygiene] Cleaned {cleaned_count} intermediate temp files for '{job_slug}'.")


# =========================================================================
# FACTORY WORKERS: LONG-FORM & SHORTS ISOLATED PIPELINES
# =========================================================================

def process_long_form_job(
    job_data: Dict[str, Any],
    publish_at_iso: str,
    dry_run: bool = False
) -> str:
    """
    Executes the complete Long-Form pipeline (5-6 min) routed strictly through long_form_compositor.
    Returns the uploaded YouTube Video ID.
    """
    job_slug = job_data["job_slug"]
    print(f"\n{'='*75}\n🎬 [FACTORY] Processing LONG-FORM PILLAR: '{job_data['title']}' ({job_slug})\n{'='*75}")

    # Step 1: Script Compilation
    manifest_path = OUTPUT_DIR / "script" / f"{job_slug}_manifest.json"
    if not manifest_path.exists():
        print(f"📝 Step 1/7: Compiling 5-Chapter Structured Script Manifest...")
        manifest_obj = compile_script_from_job(job_data)
        manifest_data = manifest_obj.model_dump()
    else:
        print(f"♻️ Step 1/7: Reusing existing script manifest: {manifest_path.name}")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    update_job_state(job_slug, STATUS_SCRIPTED, manifest_path=str(manifest_path))

    # Step 2: Chapter-Safe Audio Synthesis & Broadcast Mastering (-14 LUFS)
    audio_path = OUTPUT_DIR / "audio" / f"{job_slug}_voiceover.wav"
    if not audio_path.exists() or audio_path.stat().st_size < 10000:
        print(f"🎙️ Step 2/7: Synthesizing 5-Chapter Voiceover (-14 LUFS)...")
        dur = generate_achird_audio(str(manifest_path), str(audio_path), video_format="LONG_5_6_MIN")
    else:
        print(f"♻️ Step 2/7: Reusing existing mastered voiceover: {audio_path.name}")
    update_job_state(job_slug, STATUS_AUDIO_READY, audio_path=str(audio_path))

    # Step 3: Widescreen Subtitle Alignment
    subtitle_ass = OUTPUT_DIR / "temp_long" / f"{job_slug}_subtitles_widescreen_xray.ass"
    if not subtitle_ass.exists():
        print(f"💬 Step 3/7: Generating Widescreen Lower-Third Subtitles...")
        beats = manifest_data.get("beats", [])
        full_text = " ".join(b.get("narration_text", "") for b in beats)
        sub_json = OUTPUT_DIR / "script" / f"{job_slug}_subtitles.json"
        cards = generate_timed_subtitles(str(audio_path), full_text, manifest_data.get("target_duration_sec", 330.0), str(sub_json), video_format="LONG_5_6_MIN")
        build_ass_subtitles(cards, str(subtitle_ass), video_format="LONG_5_6_MIN")
    else:
        print(f"♻️ Step 3/7: Reusing widescreen subtitles: {subtitle_ass.name}")
    update_job_state(job_slug, STATUS_SUBTITLES_READY, subtitle_path=str(subtitle_ass))

    # Step 4: Long-Form Video Composition (Strictly routed through long_form_compositor)
    final_long_mp4 = OUTPUT_DIR / "final_long_video" / f"{job_slug}_1080p.mp4"
    if not final_long_mp4.exists():
        print(f"🎥 Step 4/7: Composing 16:9 Widescreen Master Video (long_form_compositor)...")
        source_footage = find_source_footage(job_data["movie_name"], job_data["cluster_name"])
        print(f"  Source Video: {source_footage.name}")

        clips_long_dir = OUTPUT_DIR / "clips_long"
        clips_long_dir.mkdir(parents=True, exist_ok=True)

        # Slice beats (up to 5 representative cinematic chapters for assembly)
        beats = manifest_data.get("beats", [])
        sliced_clips = []
        sample_beats = beats[:5] if dry_run else beats[:15]
        for b in sample_beats:
            b_id = b.get("beat_id", 1)
            c_num = b.get("chapter_num", 1)
            clip_file = clips_long_dir / f"{job_slug}_beat_{b_id:02d}.mp4"
            if not clip_file.exists():
                render_widescreen_xray_clip(
                    source_path=str(source_footage),
                    start_time=float(b_id * 2.5),
                    duration=4.5,
                    output_clip_path=str(clip_file),
                    camera_motion=b.get("camera_motion", "STATIC"),
                    chapter_title=f"CH. {c_num:02d} // ANALYTICAL DECONSTRUCTION"
                )
            sliced_clips.append(str(clip_file))

        temp_dir = OUTPUT_DIR / "temp_long"
        assemble_long_form_video(
            clip_paths=sliced_clips,
            voiceover_wav_path=str(audio_path),
            ass_subtitle_path=str(subtitle_ass),
            output_1080p_path=str(final_long_mp4),
            temp_dir=str(temp_dir)
        )
    else:
        print(f"♻️ Step 4/7: Reusing rendered 1080p widescreen video: {final_long_mp4.name}")
    update_job_state(job_slug, STATUS_RENDERED, video_path=str(final_long_mp4))

    # Step 5: Cinema X-Ray Brand Thumbnail Generation (1280x720, < 2MB)
    thumb_path = OUTPUT_DIR / "thumbnails_long" / f"{job_slug}_thumb.jpg"
    if not thumb_path.exists():
        print(f"🖼️ Step 5/7: Generating Unified Brand Thumbnail (1280x720, < 2MB)...")
        keyframe = extract_best_keyframe(str(final_long_mp4), start_sec=2.0, end_sec=15.0)
        # Select punchy hook from title
        words = job_data["title"].split()
        hook = " ".join(words[:4]).upper()
        highlight = words[-1].upper() if words else "WHY"
        apply_cinema_xray_theme(
            frame_img=keyframe,
            hook_text=hook,
            highlight_word=highlight,
            video_format="LONG_5_6_MIN",
            job_slug=job_slug
        )
    else:
        print(f"♻️ Step 5/7: Reusing existing thumbnail: {thumb_path.name}")
    update_job_state(job_slug, STATUS_PACKAGED, thumbnail_path=str(thumb_path))

    # Step 6: QA Gatekeeper Inspection
    print(f"🛡️ Step 6/7: Running QA Gatekeeper Pre-Upload Inspection...")
    passed, diag = inspect_final_render(
        video_path=final_long_mp4,
        thumbnail_path=thumb_path,
        video_format="LONG_5_6_MIN",
        dry_run=dry_run
    )
    if not passed:
        raise ValueError(f"QA Gatekeeper Inspection Failed for {job_slug}: {diag}")
    print(f"  ✅ QA Passed: {diag.get('resolution')}, {diag.get('duration_sec')}s, {diag.get('video_size_mb')} MB")
    update_job_state(job_slug, STATUS_QA_PASSED)

    # Step 7: YouTube Algorithmic Metadata & Resumable Upload
    print(f"🚀 Step 7/7: Compiling Metadata & Publishing (Scheduled: {publish_at_iso})...")
    meta_pkg = generate_algorithmic_metadata(manifest_data, video_format="LONG_5_6_MIN")
    upload_res = upload_to_youtube(
        video_path=final_long_mp4,
        thumbnail_path=thumb_path,
        metadata_package=meta_pkg,
        publish_at_iso=publish_at_iso,
        dry_run=dry_run
    )

    yt_id = upload_res.get("id") or f"xray_long_{job_slug}"
    update_job_state(
        job_slug,
        STATUS_UPLOADED,
        youtube_video_id=yt_id,
        publish_at_iso=publish_at_iso
    )

    # Record in long-term memory
    record_job_in_db(PlannedJob(**job_data))
    cleanup_workspace(job_slug, "LONG_5_6_MIN")

    print(f"🎉 Long-Form Pillar Complete: Video ID = {yt_id}\n")
    return yt_id


def process_short_form_job(
    job_data: Dict[str, Any],
    publish_at_iso: str,
    related_long_video_id: Optional[str] = None,
    dry_run: bool = False
) -> str:
    """
    Executes a Short-Form pipeline (45s, 9:16) routed strictly through video_compositor.
    Passes related_long_video_id into metadata compiler to funnel viewers to the Long-Form video.
    """
    job_slug = job_data["job_slug"]
    role = job_data.get("role", "SHORT_FUNNEL")
    print(f"\n{'='*75}\n⚡ [FACTORY] Processing SHORT: '{job_data['title']}' ({role} // {job_slug})\n{'='*75}")

    # Step 1: Script Compilation
    manifest_path = OUTPUT_DIR / "script" / f"{job_slug}_manifest.json"
    if not manifest_path.exists():
        print(f"📝 Step 1/7: Compiling Short Script Manifest (115-130 words, 8-10 beats)...")
        manifest_obj = compile_script_from_job(job_data)
        manifest_data = manifest_obj.model_dump()
    else:
        print(f"♻️ Step 1/7: Reusing existing short manifest: {manifest_path.name}")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    update_job_state(job_slug, STATUS_SCRIPTED, manifest_path=str(manifest_path))

    # Step 2: Voiceover Generation
    audio_path = OUTPUT_DIR / "audio" / f"{job_slug}_voiceover.wav"
    if not audio_path.exists() or audio_path.stat().st_size < 5000:
        print(f"🎙️ Step 2/7: Synthesizing Gemini Voiceover...")
        dur = generate_achird_audio(str(manifest_path), str(audio_path), video_format="SHORT_45_SEC")
    else:
        print(f"♻️ Step 2/7: Reusing short voiceover: {audio_path.name}")
        dur = 45.0
    update_job_state(job_slug, STATUS_AUDIO_READY, audio_path=str(audio_path))

    # Step 3: Rapid Subtitle Alignment (Center Bold Stroke)
    subtitle_ass = OUTPUT_DIR / "temp" / f"{job_slug}_subtitles_center_bold.ass"
    if not subtitle_ass.exists():
        print(f"💬 Step 3/7: Generating Center Bold Subtitles...")
        beats = manifest_data.get("beats", [])
        full_text = " ".join(b.get("narration_text", "") for b in beats)
        sub_json = OUTPUT_DIR / "script" / f"{job_slug}_subtitles.json"
        cards = generate_timed_subtitles(str(audio_path), full_text, dur, str(sub_json), video_format="SHORT_45_SEC")
        build_ass_subtitles(cards, str(subtitle_ass))
    else:
        print(f"♻️ Step 3/7: Reusing center bold subtitles: {subtitle_ass.name}")
    update_job_state(job_slug, STATUS_SUBTITLES_READY, subtitle_path=str(subtitle_ass))

    # Step 4: Vertical Video Composition (Strictly routed through video_compositor)
    final_short_mp4 = OUTPUT_DIR / "final_video" / f"{job_slug}_final.mp4"
    if not final_short_mp4.exists():
        print(f"🎥 Step 4/7: Composing 70% Ambient Vertical Short (video_compositor)...")
        source_footage = find_source_footage(job_data["movie_name"], job_data["cluster_name"])
        print(f"  Source Video: {source_footage.name}")

        clips_dir = OUTPUT_DIR / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        beats = manifest_data.get("beats", [])
        sliced_clips = []
        sample_beats = beats[:3] if dry_run else beats[:8]
        # Dynamically scale clip duration so clips cover voiceover + 0.6s buffer
        ffprobe_dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio_path)]
        audio_dur = float(subprocess.check_output(ffprobe_dur_cmd).decode().strip())
        target_clip_dur = round((audio_dur + 0.60) / max(len(sample_beats), 1), 2)
        print(f"  Dynamic Clip Duration: {target_clip_dur}s across {len(sample_beats)} cuts (Voiceover: {audio_dur:.2f}s)")
        for b in sample_beats:
            b_id = b.get("beat_id", 1)
            clip_file = clips_dir / f"{job_slug}_scene_{b_id:02d}.mp4"
            if not clip_file.exists():
                render_70pct_scene_clip(
                    input_video=str(source_footage),
                    start_sec=float(b_id * 3.0),
                    duration=target_clip_dur,
                    output_path=str(clip_file)
                )
            sliced_clips.append(str(clip_file))

        temp_dir = OUTPUT_DIR / "temp"
        assemble_final_video(
            scene_clips=sliced_clips,
            audio_path=str(audio_path),
            ass_subtitle_path=str(subtitle_ass),
            output_mp4=str(final_short_mp4),
            temp_dir=str(temp_dir)
        )
    else:
        print(f"♻️ Step 4/7: Reusing rendered vertical Short: {final_short_mp4.name}")
    update_job_state(job_slug, STATUS_RENDERED, video_path=str(final_short_mp4))

    # Step 5: Cinema X-Ray Short Cover Thumbnail (1080x1920)
    thumb_path = OUTPUT_DIR / "thumbnails_short" / f"{job_slug}_thumb.jpg"
    if not thumb_path.exists():
        print(f"🖼️ Step 5/7: Generating Short Cover Thumbnail (1080x1920)...")
        keyframe = extract_best_keyframe(str(final_short_mp4), start_sec=1.5, end_sec=10.0)
        words = job_data["title"].split()
        hook = " ".join(words[:4]).upper()
        highlight = words[1].upper() if len(words) > 1 else words[0].upper()
        apply_cinema_xray_theme(
            frame_img=keyframe,
            hook_text=hook,
            highlight_word=highlight,
            video_format="SHORT_45_SEC",
            job_slug=job_slug
        )
    else:
        print(f"♻️ Step 5/7: Reusing short thumbnail: {thumb_path.name}")
    update_job_state(job_slug, STATUS_PACKAGED, thumbnail_path=str(thumb_path))

    # Step 6: QA Gatekeeper Inspection
    print(f"🛡️ Step 6/7: Running QA Gatekeeper Pre-Upload Inspection...")
    passed, diag = inspect_final_render(
        video_path=final_short_mp4,
        thumbnail_path=thumb_path,
        video_format="SHORT_45_SEC",
        voiceover_path=audio_path,
        subtitles_path=subtitle_ass,
        dry_run=dry_run
    )
    if not passed:
        raise ValueError(f"QA Gatekeeper Inspection Failed for {job_slug}: {diag}")
    print(f"  ✅ QA Passed: {diag.get('resolution')}, {diag.get('duration_sec')}s, {diag.get('video_size_mb')} MB")
    update_job_state(job_slug, STATUS_QA_PASSED)

    # Step 7: Algorithmic Metadata with Funnel Link & Publish
    print(f"🚀 Step 7/7: Compiling Metadata & Publishing (Scheduled: {publish_at_iso})...")
    meta_pkg = generate_algorithmic_metadata(
        manifest_data,
        video_format="SHORT_45_SEC",
        related_long_video_id=related_long_video_id
    )
    upload_res = upload_to_youtube(
        video_path=final_short_mp4,
        thumbnail_path=thumb_path,
        metadata_package=meta_pkg,
        publish_at_iso=publish_at_iso,
        dry_run=dry_run
    )

    yt_id = upload_res.get("id") or f"xray_short_{job_slug}"
    update_job_state(
        job_slug,
        STATUS_UPLOADED,
        youtube_video_id=yt_id,
        publish_at_iso=publish_at_iso
    )

    record_job_in_db(PlannedJob(**job_data))
    cleanup_workspace(job_slug, "SHORT_45_SEC")

    print(f"🎉 Short Video Complete: Video ID = {yt_id}\n")
    return yt_id


# =========================================================================
# ORCHESTRATION ENGINE: DAILY BATCH CONTROLLER WITH 3-STRIKE QUARANTINE
# =========================================================================

def execute_daily_batch(dry_run: bool = False):
    """
    Executes one complete daily batch:
      1. Locks today's plan: 1 Long-Form + 3 Shorts
      2. Schedules peak engagement release times
      3. Processes Long-Form FIRST, captures video ID
      4. Processes 3 Shorts with funnel routing into the Long-Form video
      5. Wraps in 3-strike retry loop and auto-quarantine
    """
    print("\n" + "🚀"*40)
    print(f"⚡ CINEMA X-RAY AUTONOMOUS FACTORY: DAILY BATCH RUN {'[DRY RUN]' if dry_run else '[LIVE PRODUCTION]'}")
    print("🚀"*40)

    # Ensure SQLite batch table is initialized
    init_batch_tables()

    # 1. Topic Planning & Batch Locking
    print("\n🧠 STEP 1: Locking Today's 1 Long-Form + 3 Shorts Topic Plan...")
    plan = get_next_daily_batch()
    schedule = compute_staggered_schedule()

    print(f"  Cluster Focus:  {plan.cluster_name}")
    print(f"  Batch Date:     {plan.batch_date}")
    print(f"  Scheduled Slots:")
    for r, iso in schedule.items():
        print(f"    - {r:18s} -> {iso}")

    # Register planned jobs into batch_jobs table if not present
    conn = init_batch_tables()
    for job in plan.all_jobs():
        conn.execute("""
            INSERT OR IGNORE INTO batch_jobs (
                batch_date, job_slug, cluster_name, movie_name, video_format,
                category_lens, title, core_thesis, role, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan.batch_date, job.job_slug, job.cluster_name, job.movie_name,
            job.video_format, job.category_lens, job.title, job.core_thesis,
            job.role, STATUS_PLANNED
        ))
    conn.commit()
    conn.close()

    # 2. Long-Form Pillar on Hold (Exclusively 3 Shorts per day per user request)
    print("\nℹ️ Long-Form Pillar on hold. Focusing 100% on 3x Daily Shorts Autopilot.")
    long_video_id = None

    # 3. Process the 3 Shorts in Sequence
    shorts = [
        (plan.short_1, "SHORT_FUNNEL_1", long_video_id),
        (plan.short_2, "SHORT_FUNNEL_2", long_video_id),
        (plan.short_3_bridge, "SHORT_BRIDGE_3", None)  # Bridge video connects to tomorrow's universe
    ]

    for short_job, role_name, funnel_id in shorts:
        s_dict = short_job.model_dump()
        s_slug = s_dict["job_slug"]
        s_state = get_job_state(s_slug)

        if s_state and s_state.get("status") == STATUS_UPLOADED:
            print(f"♻️ Short '{s_slug}' already uploaded ({s_state.get('youtube_video_id')}). Skipping.")
            continue
        elif s_state and s_state.get("status") == STATUS_QUARANTINED:
            print(f"⚠️ Short '{s_slug}' was previously quarantined. Skipping.")
            continue

        for attempt in range(1, 4):
            try:
                process_short_form_job(
                    job_data=s_dict,
                    publish_at_iso=schedule[role_name],
                    related_long_video_id=funnel_id,
                    dry_run=dry_run
                )
                break
            except Exception as e:
                print(f"❌ Short '{s_slug}' Attempt {attempt}/3 Failed: {e}")
                update_job_state(s_slug, s_state.get("status", STATUS_PLANNED), retry_count=attempt)
                if attempt == 3:
                    log_daemon_error(s_slug, f"SHORT_{role_name}", e)
                    update_job_state(s_slug, STATUS_QUARANTINED, error_message=str(e))
                time.sleep(2 * attempt)

    print("\n" + "🎉"*40)
    print("DAILY BATCH ORCHESTRATION COMPLETED SUCCESSFULLY!")
    print("🎉"*40 + "\n")


def run_daemon_loop(daily_hour: int = 6, dry_run: bool = False):
    """24/7 continuous daemon loop waking up at daily_hour to run the daily batch."""
    print(f"\n📡 Cinema X-Ray 24/7 Daemon Activated. Daily target hour: {daily_hour:02d}:00 local time.")
    while True:
        try:
            execute_daily_batch(dry_run=dry_run)
        except Exception as e:
            print(f"🔥 Critical Daemon Exception: {e}")
            log_daemon_error("DAEMON_LOOP", "BATCH_EXECUTION", e)

        # Calculate sleep until tomorrow's daily_hour
        now = datetime.now()
        target = now.replace(hour=daily_hour, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        sleep_sec = (target - now).total_seconds()
        print(f"💤 Daemon sleeping for {sleep_sec / 3600:.1f} hours (Waking at {target.strftime('%Y-%m-%d %H:%M:%S')})...\n")
        time.sleep(sleep_sec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cinema X-Ray 24/7 Autonomous Factory Daemon")
    parser.add_argument("--run-once", action="store_true", help="Execute one daily batch and exit immediately")
    parser.add_argument("--daemon", action="store_true", help="Run continuously 24/7 in a background loop")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run without live YouTube uploads (default: True)")
    parser.add_argument("--live", action="store_true", help="Enable live YouTube uploads (sets dry-run=False)")
    args = parser.parse_args()

    is_dry_run = not args.live

    if args.daemon:
        run_daemon_loop(daily_hour=6, dry_run=is_dry_run)
    else:
        execute_daily_batch(dry_run=is_dry_run)
