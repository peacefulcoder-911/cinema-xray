#!/usr/bin/env python3
"""
Cinema Decoded: Spider-Man: Brand New Day — The Mutating DNA Paradox
Builds a broadcast-grade 9:16 vertical Short in 8K Ultra HD (4320x7680)
with 70% active cinematic framing (1080x1344), soft ambient blur backdrop,
Arc Reactor Cyan HUD ASS subtitles, ElevenLabs Liam master audio,
Apple Silicon 8K Super-Resolution, and direct unlisted YouTube publishing.
"""

import os
import sys
import time
import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent
CLIPS_DIR = BASE_DIR / "clips"
OUT_DIR = BASE_DIR / "out"
QC_DIR = BASE_DIR / "qc_frames"
SCENE_PLAN_PATH = BASE_DIR / "scene_plan.json"

FINAL_8K_REPO = REPO_ROOT / "output" / "final_video" / "cinema_xray_spiderman_brand_new_day_dna_8k.mp4"
THUMBNAIL_PATH = BASE_DIR / "thumbnail.jpg"
THUMBNAIL_OUTPUT_DIR = REPO_ROOT / "output" / "thumbnails_short" / "spiderman_brand_new_day_dna_thumb.jpg"

CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
QC_DIR.mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "output" / "final_video").mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "output" / "thumbnails_short").mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO_ROOT))
from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution
from pipeline.youtube_uploader import upload_video
from pipeline.topic_database import TopicDatabase

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


class PipelineStageTimer:
    def __init__(self):
        self.records = []
        self._current_stage = None
        self._start_time = None
        self._pipeline_start = time.time()

    def start(self, stage_name: str):
        if self._current_stage and self._start_time:
            elapsed = time.time() - self._start_time
            self.records.append((self._current_stage, elapsed))
            print(f"⏱️  [{self._current_stage}] Completed in {elapsed:.2f}s ({elapsed/60:.2f}m)")
        self._current_stage = stage_name
        self._start_time = time.time()
        print(f"\n▶️  STARTING STAGE: {stage_name}...")

    def finish_all(self):
        if self._current_stage and self._start_time:
            elapsed = time.time() - self._start_time
            self.records.append((self._current_stage, elapsed))
            print(f"⏱️  [{self._current_stage}] Completed in {elapsed:.2f}s ({elapsed/60:.2f}m)")
        self.total_time = time.time() - self._pipeline_start

    def get_summary(self):
        return {
            "stages": [
                {"stage": name, "duration_seconds": round(dur, 2), "percentage": round((dur / self.total_time) * 100, 1)}
                for name, dur in self.records
            ],
            "total_duration_seconds": round(self.total_time, 2),
            "total_duration_minutes": round(self.total_time / 60, 2)
        }


def run_cmd(cmd, desc=""):
    print(f"\n[RUNNING] {desc}")
    print(" ".join(cmd[:12]) + ("..." if len(cmd) > 12 else ""))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:\n{res.stderr}")
        raise RuntimeError(f"Command failed with exit code {res.returncode}")
    return res


def render_70pct_clip_clean(
    src_video: str,
    start_sec: float,
    duration: float,
    out_name: str,
    callout_text: str = None,
    callout_y: int = 340,
    motion: str = "SLOW_PUSH_IN",
    fps: int = 30
) -> str:
    """
    Renders clean 70% cinematic framing (1080x1344) with soft ambient blur background (1080x1920)
    and clean matte dividers at Y=287 and Y=1632.
    """
    out_path = str(CLIPS_DIR / out_name)
    crop_str = "crop=1080:1344"

    # Motion dynamics
    if motion == "FAST_ZOOM":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0016,1.10)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PAN_LEFT":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0005,1.035)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PAN_RIGHT":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0005,1.035)':d=1:x='(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PUSH_IN":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0004,1.03)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    else:  # STATIC
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str}"

    extra_overlay = ""
    if callout_text:
        clean_callout = callout_text.replace("'", "").replace(":", "\\:").upper()
        extra_overlay = (
            f",drawtext=fontfile='{FONT_PATH}':text='{clean_callout}':fontcolor=white:fontsize=30:"
            f"x=(w-text_w)/2:y={callout_y}:shadowcolor=black@0.9:shadowx=2:shadowy=2"
        )

    vf = (
        f"[0:v]tpad=stop_mode=clone:stop_duration=1.0[vpad];"
        f"[vpad]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=35:5,eq=brightness=-0.08:contrast=1.15:saturation=1.2[bg];"
        f"[vpad]{fg_zoom},eq=brightness=-0.03:contrast=1.16:saturation=1.15[fg];"
        f"[bg][fg]overlay=0:288,"
        f"drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
        f"drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill"
        f"{extra_overlay},"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-t", f"{duration:.3f}",
        "-i", str(src_video),
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-t", f"{duration:.3f}",
        "-r", str(fps), "-pix_fmt", "yuv420p", "-an",
        out_path
    ]
    run_cmd(cmd, f"Rendering clean 70% beat: {out_name}")
    return out_path


def build_spiderman_short():
    print("=" * 70)
    print("🎬 CINEMA DECODED: SPIDER-MAN: BRAND NEW DAY — 8K MASTER BUILDER")
    print("=" * 70)

    timer = PipelineStageTimer()

    with open(SCENE_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    audio_path = str(BASE_DIR / "audio" / "master_audio.wav")
    ass_path = str(BASE_DIR / "subtitles.ass")
    source_video = str(REPO_ROOT / plan["source_trailer"])

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Missing master audio: {audio_path}")
    if not os.path.exists(ass_path):
        raise FileNotFoundError(f"Missing subtitles: {ass_path}")
    if not os.path.exists(source_video):
        raise FileNotFoundError(f"Missing source trailer: {source_video}")

    # STAGE 1: Render 70% Cinematic Scenes
    timer.start("1. Scene Slicing & 70% Cinematic Framing (Ambient Blur + Motion)")
    clip_paths = []
    for idx, beat in enumerate(plan["beats"], 1):
        bid = beat["beat_id"]
        st = beat.get("source_start", 0.0)
        dur = beat["duration"]
        motion = beat.get("motion", "SLOW_PUSH_IN")
        callout = beat.get("callout")
        callout_y = beat.get("callout_y", 340)
        out_name = f"{idx:02d}_{bid}.mp4"

        rendered_clip = render_70pct_clip_clean(
            src_video=source_video,
            start_sec=st,
            duration=dur,
            out_name=out_name,
            callout_text=callout,
            callout_y=callout_y,
            motion=motion
        )
        clip_paths.append(rendered_clip)

    # STAGE 2: Concat visual clips using concat filter
    timer.start("2. Visual Clips Concatenation")
    visual_master = str(CLIPS_DIR / "visual_master.mp4")

    inputs = []
    for p in clip_paths:
        inputs.extend(["-i", str(p)])

    filter_inputs = "".join(f"[{i}:v]" for i in range(len(clip_paths)))
    concat_filter = f"{filter_inputs}concat=n={len(clip_paths)}:v=1:a=0[outv]"

    concat_cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", concat_filter,
        "-map", "[outv]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "12",
        visual_master
    ]
    run_cmd(concat_cmd, "Concatenating Clean Visual Clips via Concat Filter")

    master_dur = plan["total_duration"]

    # STAGE 3: Composite 1080p Master with Subtitles and Mastered Audio
    timer.start("3. 1080p Master Assembly with Subtitle Burn-in & Audio")
    master_1080p = str(OUT_DIR / "cinema_decoded_spiderman_brand_new_day_dna_1080p.mp4")
    escaped_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")

    final_1080p_cmd = [
        "ffmpeg", "-y",
        "-i", visual_master,
        "-i", audio_path,
        "-vf", f"ass='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "256k",
        "-t", f"{master_dur:.3f}",
        "-movflags", "+faststart",
        master_1080p
    ]
    run_cmd(final_1080p_cmd, "Compositing 1080p Master Delivery Copy with Subtitles")

    # STAGE 4: Hardware-Accelerated 8K Super-Resolution
    timer.start("4. Hardware-Accelerated 8K Ultra HD Super-Resolution (4320x7680 @ 85 Mbps)")
    master_8k = str(OUT_DIR / "cinema_decoded_spiderman_brand_new_day_dna_8k.mp4")
    upgrade_to_super_resolution(
        input_video=master_1080p,
        output_video=master_8k,
        target_tier="8K",
        sharpness=0.55,
        bitrate="85M"
    )
    shutil.copyfile(master_8k, str(FINAL_8K_REPO))
    print(f"✅ 8K Ultra HD Master exported to: {FINAL_8K_REPO}")

    # STAGE 5: High-CTR Vertical Thumbnail & QC Frames
    timer.start("5. High-CTR Vertical Thumbnail Generation & QC Extraction")
    thumb_src = clip_paths[1]  # Timestamp 00:30 laboratory confrontation
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "1.5", "-i", thumb_src,
        "-filter_complex", (
            f"[0:v]split=2[vbg][vfg];"
            f"[vbg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.10:contrast=1.20:saturation=1.3[bg];"
            f"[vfg]scale=1080:1344:force_original_aspect_ratio=increase,crop=1080:1344,eq=brightness=0.04:contrast=1.18:saturation=1.2[fg];"
            f"[bg][fg]overlay=0:288,"
            f"drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
            f"drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill,"
            f'drawtext=fontfile="{FONT_PATH}":text="THE LINE EVERYONE MISSED":fontcolor=white:fontsize=36:x=(w-text_w)/2:y=220:shadowcolor=black@0.9:shadowx=3:shadowy=3,'
            f'drawtext=fontfile="{FONT_PATH}":text="SUPPRESSING HIS DNA?":fontcolor=0xF5C518:fontsize=52:x=(w-text_w)/2:y=1680:shadowcolor=black@0.9:shadowx=3:shadowy=3'
        ),
        "-vframes", "1",
        str(THUMBNAIL_PATH)
    ]
    run_cmd(thumb_cmd, "Rendering High-CTR Vertical Thumbnail")
    shutil.copyfile(str(THUMBNAIL_PATH), str(THUMBNAIL_OUTPUT_DIR))

    # QC Frames
    timestamps = [round(master_dur * r, 2) for r in [0.05, 0.15, 0.30, 0.45, 0.60, 0.75, 0.88, 0.96]]
    qc_frame_paths = []
    for idx, ts in enumerate(timestamps, 1):
        qf = QC_DIR / f"qc_frame_{idx:02d}_{int(ts)}s.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", master_1080p, "-vframes", "1", str(qf)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if qf.exists():
            qc_frame_paths.append(str(qf))

    # STAGE 6: Direct Unlisted YouTube Upload
    timer.start("6. Direct Unlisted YouTube Upload")
    yt_title = "Spider-Man: Brand New Day — The Line Everyone Missed (Banner Lab Scene) #Shorts"[:100]
    yt_desc = (
        "You completely missed the most terrifying line in the new Spider-Man: Brand New Day trailer.\n"
        "At the thirty-second mark, Peter Parker asks Bruce Banner how to suppress mutating DNA.\n\n"
        "🎬 Film: Spider-Man: Brand New Day (2026)\n"
        "🎙️ Narration: ElevenLabs Liam (Cinema Decoded Lead Voice)\n"
        "📐 Resolution: 8K Super-Resolution (4320x7680) Master\n"
        "🎞️ Source: Sony Pictures Entertainment Official Trailer\n\n"
        "#SpiderManBrandNewDay #SpiderMan #Marvel #Shorts #MovieExplained #CinemaDecoded"
    )
    yt_tags = ["Spider-Man: Brand New Day", "Spider-Man", "Bruce Banner", "Hulk", "Tom Holland", "Mark Ruffalo", "Cinema Decoded", "Shorts", "Marvel"]

    print("Uploading 8K master to YouTube as unlisted...")
    yt_res = upload_video(
        file_path=str(FINAL_8K_REPO),
        title=yt_title,
        description=yt_desc,
        tags=yt_tags,
        privacy_status="unlisted"
    )
    yt_url = yt_res.get("url")
    yt_id = yt_res.get("id")

    # STAGE 7: Database Registration
    timer.start("7. Topic Database Registration")
    topic_db = TopicDatabase()
    topic_db.add_completed_topic(
        topic_slug="spiderman_brand_new_day_dna_paradox",
        movie_name="Spider-Man: Brand New Day (2026)",
        film_cluster="Marvel Cinematic Universe",
        title="The Mutating DNA Paradox: Why Peter Asks Bruce Banner to Suppress His Spider-Powers",
        hook="You completely missed the most terrifying line in the new Spider-Man trailer.",
        core_thesis="At the 30-second mark of Brand New Day, Peter Parker isn't fighting a villain—he is begging Bruce Banner to suppress his mutating DNA.",
        category_lens="Trailer Detail Investigation",
        scheduled_slot="ANY",
        scheduled_time_iso=None,
        youtube_video_id=yt_id,
        youtube_url=yt_url
    )

    timer.finish_all()
    summary = timer.get_summary()

    print("=" * 70)
    print("🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"   8K Master: {FINAL_8K_REPO}")
    print(f"   1080p Delivery: {master_1080p}")
    print(f"   Thumbnail: {THUMBNAIL_OUTPUT_DIR}")
    print(f"   YouTube URL: {yt_url} (unlisted)")
    print(f"   Total Time: {summary['total_duration_minutes']} minutes")
    print("=" * 70)

    # Save QC Report
    qc_report = {
        "project": "Spider-Man: Brand New Day — The Mutating DNA Paradox",
        "movie": "Spider-Man: Brand New Day (2026)",
        "source_trailer": "Sony Pictures Entertainment (Official 4K Trailer)",
        "duration": master_dur,
        "master_8k_path": str(FINAL_8K_REPO),
        "delivery_1080p_path": master_1080p,
        "thumbnail_path": str(THUMBNAIL_OUTPUT_DIR),
        "youtube_url": yt_url,
        "youtube_id": yt_id,
        "qc_frames": qc_frame_paths,
        "timing_summary": summary
    }
    (BASE_DIR / "qc_report.json").write_text(json.dumps(qc_report, indent=2), encoding="utf-8")
    return qc_report


if __name__ == "__main__":
    build_spiderman_short()

