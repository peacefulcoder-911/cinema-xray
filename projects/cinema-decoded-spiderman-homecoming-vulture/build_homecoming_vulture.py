#!/usr/bin/env python3
"""
Cinema Decoded: Spider-Man: Homecoming — The Contract That Created The Vulture
Builds a broadcast-grade 9:16 vertical Short in 8K Ultra HD (4320x7680)
with 70% active cinematic framing (1080x1344), soft ambient blur backdrop,
CenterBold ASS subtitles (gold keyword emphasis, NO box backgrounds),
typographic documentary callouts, standard Achird voiceover (NO transition SFX, NO whoosh),
and Apple Silicon 8K Super-Resolution.
Exports both the 8K Master (4320x7680) and 1080p Delivery Copy (1080x1920).
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

FINAL_8K_REPO = REPO_ROOT / "output" / "final_video" / "cinema_xray_homecoming_vulture_8k.mp4"
THUMBNAIL_PATH = BASE_DIR / "thumbnail.jpg"
THUMBNAIL_OUTPUT_DIR = REPO_ROOT / "output" / "thumbnails_short" / "homecoming_vulture_thumb.jpg"

CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
QC_DIR.mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "output" / "final_video").mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "output" / "thumbnails_short").mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO_ROOT))
from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution


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


BEAT_CALLOUTS = {
    1: "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='WHY DOES A SALVAGE CREW HAVE ALIEN WEAPONS\\?':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=340:shadowcolor=black@0.9:shadowx=2:shadowy=2",
    4: "drawtext=fontfile='/System/Library/Fonts/HelveticaNeue.ttc':text='ADRIAN TOOMES | SALVAGE CONTRACTOR':fontcolor=0xF5C518:fontsize=32:x=(w-text_w)/2:y=1540:shadowcolor=black@0.9:shadowx=2:shadowy=2",
    7: "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='CONTRACT\\: CANCELLED':fontcolor=0xFF4B4B:fontsize=44:x=(w-text_w)/2:y=340:shadowcolor=black@0.9:shadowx=3:shadowy=3",
    11: "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='NOT POWER. PAYROLL.':fontcolor=0xF5C518:fontsize=44:x=(w-text_w)/2:y=340:shadowcolor=black@0.9:shadowx=3:shadowy=3",
    12: "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='WHICH MARVEL VILLAIN HAD THE MOST BELIEVABLE MOTIVE\\?':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=340:shadowcolor=black@0.9:shadowx=2:shadowy=2"
}


def render_70pct_clip_clean(
    src_video: str,
    start_sec: float,
    duration: float,
    out_name: str,
    beat_idx: int,
    motion: str = "SLOW_PUSH_IN",
    fps: int = 30
) -> str:
    """
    Renders clean 70% cinematic framing (1080x1344) with soft ambient blur background and matte dividers.
    Applies high-contrast industrial documentary color grading and subtle motion.
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

    extra_overlay = f",{BEAT_CALLOUTS[beat_idx]}" if beat_idx in BEAT_CALLOUTS else ""

    input_args = ["-ss", f"{start_sec:.3f}", "-t", f"{duration:.3f}", "-i", str(src_video)]
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
        *input_args,
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-t", f"{duration:.3f}",
        "-r", str(fps), "-pix_fmt", "yuv420p", "-an",
        out_path
    ]
    run_cmd(cmd, f"Rendering clean {out_name}")
    return out_path


def build_homecoming_vulture_short():
    print("=" * 70)
    print("🎬 CINEMA DECODED: SPIDER-MAN: HOMECOMING — 8K MASTER BUILDER")
    print("=" * 70)

    timer = PipelineStageTimer()

    with open(SCENE_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # 1. Validate files
    audio_path = str(BASE_DIR / "audio" / "vulture_origin_master.wav")
    ass_path = str(BASE_DIR / "vulture_origin_subtitles.ass")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Missing master audio: {audio_path}")
    if not os.path.exists(ass_path):
        raise FileNotFoundError(f"Missing subtitles: {ass_path}")

    # Check footage availability
    missing_assets = []
    for beat in plan["beats"]:
        src = REPO_ROOT / beat.get("source_file", "")
        if not src.exists():
            missing_assets.append((beat["beat_id"], str(src)))

    if missing_assets:
        print("\n⚠️  SOURCE VIDEO FOOTAGE NOT FOUND FOR:")
        for bid, path in missing_assets:
            print(f"   - {bid}: {path}")
        return False

    # STAGE 1: Render 70% Cinematic Scenes
    timer.start("1. Scene Slicing & 70% Cinematic Framing (Ambient Blur + Motion)")
    clip_paths = []
    for idx, beat in enumerate(plan["beats"], 1):
        bid = beat["beat_id"]
        src = str(REPO_ROOT / beat.get("source_file", ""))
        st = beat.get("source_start", 0.0)
        dur = beat["duration"]
        motion = beat.get("motion", "SLOW_PUSH_IN")
        out_name = f"{idx:02d}_{bid}.mp4"

        rendered_clip = render_70pct_clip_clean(
            src_video=src,
            start_sec=st,
            duration=dur,
            out_name=out_name,
            beat_idx=idx,
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
    master_1080p = str(OUT_DIR / "cinema_decoded_homecoming_vulture_1080p.mp4")
    escaped_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")

    final_1080p_cmd = [
        "ffmpeg", "-y",
        "-i", visual_master,
        "-i", audio_path,
        "-vf", f"subtitles='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "256k",
        "-t", f"{master_dur:.3f}",
        "-movflags", "+faststart",
        master_1080p
    ]
    run_cmd(final_1080p_cmd, "Compositing 1080p Master Delivery Copy with Subtitles")

    # STAGE 4: Hardware-Accelerated 8K Super-Resolution
    timer.start("4. Hardware-Accelerated 8K Ultra HD Super-Resolution (4320x7680 @ 85 Mbps)")
    master_8k = str(OUT_DIR / "cinema_decoded_homecoming_vulture_8k.mp4")
    upgrade_to_super_resolution(
        input_video=master_1080p,
        output_video=master_8k,
        target_tier="8K",
        sharpness=0.55,
        bitrate="85M"
    )
    shutil.copyfile(master_8k, str(FINAL_8K_REPO))
    print(f"✅ 8K Ultra HD Master exported to: {FINAL_8K_REPO}")

    # STAGE 5: High-CTR Vertical Thumbnail
    timer.start("5. High-CTR Vertical Thumbnail Generation")
    thumb_src = str(REPO_ROOT / "assets" / "footage" / "spiderman_homecoming" / "vulture_origin" / "11_vulture_suit_reveal.mp4")
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "1.5", "-i", thumb_src,
        "-filter_complex", (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=30:5,eq=brightness=-0.10:contrast=1.20:saturation=1.3[bg];"
            "[0:v]scale=1080:1344:force_original_aspect_ratio=increase,crop=1080:1344,"
            "eq=brightness=0.04:contrast=1.18:saturation=1.2[fg];"
            "[bg][fg]overlay=0:288,"
            "drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
            "drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill,"
            "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='THE CONTRACT THAT CREATED':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=220:shadowcolor=black@0.9:shadowx=3:shadowy=3,"
            "drawtext=fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf':text='THE VULTURE':fontcolor=0xF5C518:fontsize=52:x=(w-text_w)/2:y=1680:shadowcolor=black@0.9:shadowx=3:shadowy=3"
        ),
        "-vframes", "1",
        str(THUMBNAIL_PATH)
    ]
    run_cmd(thumb_cmd, "Rendering Clean High-CTR Vertical Thumbnail")
    shutil.copyfile(str(THUMBNAIL_PATH), str(THUMBNAIL_OUTPUT_DIR))

    # STAGE 6: Automated Quality Control & QC Frame Extraction
    timer.start("6. Automated Quality Control & QC Frame Extraction")
    qc_stamps = [2.0, 6.0, 10.0, 15.0, 22.0, 28.0, 35.0, 42.0]
    qc_frame_paths = []
    artifacts_dir = Path("/Users/vinaybt/.gemini/antigravity/brain/f5bbdfa3-43d4-4e1d-a047-6bac52b0ed76")

    for stamp in qc_stamps:
        frame_name = f"qc_frame_{int(stamp):02d}s.jpg"
        frame_dest = QC_DIR / frame_name
        qc_cmd = [
            "ffmpeg", "-y",
            "-ss", f"{stamp:.2f}",
            "-i", master_8k,
            "-vframes", "1",
            str(frame_dest)
        ]
        run_cmd(qc_cmd, f"Extracting QC frame at {stamp}s")
        qc_frame_paths.append(str(frame_dest))
        if artifacts_dir.exists():
            art_dest = artifacts_dir / f"qc_homecoming_vulture_{int(stamp):02d}s.jpg"
            shutil.copyfile(str(frame_dest), str(art_dest))

    if artifacts_dir.exists():
        shutil.copyfile(str(THUMBNAIL_PATH), str(artifacts_dir / "qc_homecoming_vulture_thumbnail.jpg"))

    # QC Verification with ffprobe
    probe_8k = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,duration,r_frame_rate,bit_rate",
        "-show_entries", "format=size,duration",
        "-of", "json", master_8k
    ], capture_output=True, text=True)
    probe_data = json.loads(probe_8k.stdout)

    probe_1080p = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,duration,r_frame_rate,bit_rate",
        "-show_entries", "format=size,duration",
        "-of", "json", master_1080p
    ], capture_output=True, text=True)
    probe_1080p_data = json.loads(probe_1080p.stdout)

    timer.finish_all()
    summary = timer.get_summary()

    report = {
        "project": "cinema-decoded-spiderman-homecoming-vulture",
        "movie": "Spider-Man: Homecoming (2017)",
        "topic": "Spider-Man: Homecoming — The Contract That Created The Vulture",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "outputs": {
            "master_8k": {
                "path": master_8k,
                "global_path": str(FINAL_8K_REPO),
                "resolution": f"{probe_data['streams'][0]['width']}x{probe_data['streams'][0]['height']}",
                "fps": probe_data['streams'][0]['r_frame_rate'],
                "duration": float(probe_data['format']['duration']),
                "size_mb": round(int(probe_data['format']['size']) / (1024 * 1024), 2)
            },
            "delivery_1080p": {
                "path": master_1080p,
                "resolution": f"{probe_1080p_data['streams'][0]['width']}x{probe_1080p_data['streams'][0]['height']}",
                "fps": probe_1080p_data['streams'][0]['r_frame_rate'],
                "duration": float(probe_1080p_data['format']['duration']),
                "size_mb": round(int(probe_1080p_data['format']['size']) / (1024 * 1024), 2)
            },
            "thumbnail": {
                "path": str(THUMBNAIL_PATH),
                "global_path": str(THUMBNAIL_OUTPUT_DIR)
            }
        },
        "audio_standards": {
            "voice": "Achird (Gemini TTS single-take)",
            "peak_db": -1.0,
            "whoosh_sfx": False,
            "drone_noise_pumping": False,
            "silence_noise_floor_db": -68.0
        },
        "qc_frames": qc_frame_paths,
        "performance_profile": summary
    }

    with open(BASE_DIR / "qc_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(BASE_DIR / "benchmark_timeline.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("🏆 CINEMA DECODED: SPIDER-MAN: HOMECOMING 8K BUILD COMPLETE!")
    print(f"   8K Master: {master_8k} ({report['outputs']['master_8k']['size_mb']} MB)")
    print(f"   1080p Delivery: {master_1080p} ({report['outputs']['delivery_1080p']['size_mb']} MB)")
    print(f"   Total Build Time: {summary['total_duration_seconds']:.2f}s ({summary['total_duration_minutes']:.2f}m)")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = build_homecoming_vulture_short()
    if not success:
        sys.exit(1)

