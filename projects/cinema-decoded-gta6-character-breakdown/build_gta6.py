#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
"""
Cinema Decoded: Why GTA 6 Has Two Main Characters
Master Production Builder & 8K Super-Resolution Exporter
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
OUT_DIR = BASE_DIR / "output"
QC_DIR = OUT_DIR / "qc_frames"
SCENE_PLAN_PATH = BASE_DIR / "scene_plan.json"

FINAL_8K_REPO = REPO_ROOT / "output" / "final_video" / "cinema_xray_gta6_character_breakdown_8k.mp4"
THUMBNAIL_OUTPUT_DIR = REPO_ROOT / "output" / "thumbnails_short" / "gta6_character_breakdown_thumb.jpg"

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
        print(f"\n🏁 ALL PIPELINE STAGES COMPLETED in {self.total_time:.2f}s ({self.total_time/60:.2f}m)")
        print("\n" + "=" * 60)
        print("STAGE PERFORMANCE BREAKDOWN:")
        for name, dur in self.records:
            print(f"  • {name:50}: {dur:6.2f}s ({dur/60:4.2f}m)")
        print("=" * 60)


def run_cmd(cmd, desc):
    print(f"\n[RUNNING] {desc}")
    print(" ".join(cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"❌ Error in: {desc}")
        print("STDERR:\n" + res.stderr[-1000:])
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
    out_path = str(CLIPS_DIR / out_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"   [CACHE] Reusing rendered clip: {out_name}")
        return out_path

    crop_str = "crop=1080:1344"

    if motion == "FAST_ZOOM":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0016,1.10)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PAN_LEFT":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0005,1.035)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PAN_RIGHT":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0005,1.035)':d=1:x='(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    elif motion == "SLOW_PUSH_IN":
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str},zoompan=z='min(zoom+0.0004,1.03)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps={fps}"
    else:
        fg_zoom = f"scale=1080:1344:force_original_aspect_ratio=increase,{crop_str}"

    extra_overlay = ""
    if callout_text:
        clean_callout = callout_text.replace("'", "").replace(":", "\\:").upper()
        # Vice City color scheme: Lucia=Pink, Jason=Cyan, Story=Yellow
        if "LUCIA" in clean_callout or "PRISON" in clean_callout:
            font_color = "#ff4499"
        elif "JASON" in clean_callout or "KEYS" in clean_callout or "ARMY" in clean_callout:
            font_color = "#00e5ff"
        elif "WRONG" in clean_callout or "LEONIDA" in clean_callout:
            font_color = "#ff3344"
        else:
            font_color = "#ffcc00"

        font_size = 44 if len(clean_callout) <= 12 else 32
        border_w = 18 if len(clean_callout) <= 12 else 14
        extra_overlay = (
            f",drawtext=fontfile='{FONT_PATH}':text='{clean_callout}':fontcolor={font_color}:fontsize={font_size}:"
            f"box=1:boxcolor=black@0.92:boxborderw={border_w}:"
            f"x=(w-text_w)/2:y={callout_y}:shadowcolor=black@0.9:shadowx=2:shadowy=2"
        )

    vf = (
        f"[0:v]tpad=stop_mode=clone:stop_duration=1.0[vpad];"
        f"[vpad]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=35:5,eq=brightness=-0.08:contrast=1.15:saturation=1.2[bg];"
        f"[vpad]{fg_zoom},eq=brightness=-0.03:contrast=1.16:saturation=1.15[fg];"
        f"[bg][fg]overlay=0:288,"
        f"drawbox=x=0:y=287:w=1080:h=2:color='#ff4499'@0.75:t=fill,"
        f"drawbox=x=0:y=1632:w=1080:h=2:color='#00e5ff'@0.75:t=fill"
        f"{extra_overlay},"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-i", src_video,
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-t", f"{duration:.3f}",
        "-r", str(fps), "-pix_fmt", "yuv420p", "-an",
        out_path
    ]
    run_cmd(cmd, f"Rendering clean 70% beat: {out_name}")
    return out_path


def build_gta6_short():
    print("=" * 70)
    print("🎬 CINEMA DECODED: WHY GTA 6 HAS TWO MAIN CHARACTERS")
    print("======================================================================")

    timer = PipelineStageTimer()

    with open(SCENE_PLAN_PATH, "r", encoding="utf-8") as f:
        plan = json.load(f)

    audio_path = str(BASE_DIR / "assets" / "narration" / "master_narration.wav")
    ass_path = str(BASE_DIR / "subtitles.ass")

    # STAGE 1: Render 14 Word-Matched Scenes
    timer.start("1. Word-to-Visual Slicing & 70% Cinematic Framing (Ambient Blur + Callouts)")
    clip_paths = []
    for idx, scene in enumerate(plan["scenes"], 1):
        sid = scene["id"]
        src = str(BASE_DIR / scene["source_file"])
        st = scene["source_start"]
        dur = scene["duration_sec"]
        motion = scene.get("camera_movement", "SLOW_PUSH_IN")
        callout = scene.get("callout")
        out_name = f"{idx:02d}_{sid}.mp4"

        rendered_clip = render_70pct_clip_clean(
            src_video=src,
            start_sec=st,
            duration=dur,
            out_name=out_name,
            callout_text=callout,
            callout_y=340,
            motion=motion
        )
        clip_paths.append(rendered_clip)

    # STAGE 2: Concatenate Visual Clips
    timer.start("2. Visual Clips Concatenation")
    visual_master = str(CLIPS_DIR / "visual_master.mp4")
    if os.path.exists(visual_master) and os.path.getsize(visual_master) > 1000:
        print(f"   [CACHE] Reusing visual master: {visual_master}")
    else:
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
            "-c:v", "libx264", "-preset", "fast", "-crf", "14",
            "-pix_fmt", "yuv420p", "-r", "30",
            visual_master
        ]
        run_cmd(concat_cmd, "Concatenating 14 scene clips into visual master")

    # STAGE 3: Assemble 1080p Delivery Short with Subtitles & Audio
    timer.start("3. 1080p Master Assembly with Subtitles & Studio Narration")
    master_1080p = str(OUT_DIR / "gta6-youtube-1080p.mp4")
    total_dur = plan["total_duration"]

    if os.path.exists(master_1080p) and os.path.getsize(master_1080p) > 1000:
        print(f"   [CACHE] Reusing master 1080p: {master_1080p}")
    else:
        assemble_cmd = [
            "ffmpeg", "-y",
            "-i", visual_master,
            "-i", audio_path,
            "-filter_complex", f"[0:v]subtitles='{ass_path}':force_style='Alignment=2,MarginV=360'[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "14",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", f"{total_dur:.3f}",
            "-pix_fmt", "yuv420p", "-r", "30",
            master_1080p
        ]
        run_cmd(assemble_cmd, "Assembling final 1080p Short with subtitles")

    # STAGE 4: Hardware 8K Super-Resolution
    timer.start("4. Apple Silicon Hardware 8K Super-Resolution (4320x7680 @ 85 Mbps)")
    master_8k = str(OUT_DIR / "gta6-master-8k.mp4")
    if os.path.exists(master_8k) and os.path.getsize(master_8k) > 1000000:
        print(f"   [CACHE] Reusing 8K master: {master_8k}")
    else:
        upgrade_to_super_resolution(
            input_video=master_1080p,
            output_video=master_8k,
            target_tier="8K",
            sharpness=0.55,
            bitrate="85M"
        )
    if not FINAL_8K_REPO.exists() or FINAL_8K_REPO.stat().st_size != os.path.getsize(master_8k):
        shutil.copyfile(master_8k, str(FINAL_8K_REPO))

    # STAGE 5: High-CTR Vertical Thumbnail Cover
    timer.start("5. Generating High-CTR Vertical Thumbnail Cover")
    thumbnail_path = str(OUT_DIR / "thumbnail.jpg")
    thumb_bg = str(CLIPS_DIR / "thumb_bg.jpg")

    run_cmd([
        "ffmpeg", "-y",
        "-ss", "1.0",
        "-i", clip_paths[10],  # Scene 11: Convenience Store Robbery
        "-vframes", "1",
        "-q:v", "1",
        thumb_bg
    ], "Extracting thumbnail keyframe")

    thumb_vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"eq=brightness=0.04:contrast=1.28:saturation=1.35,"
        f"drawbox=x=0:y=0:w=1080:h=420:color=black@0.85:t=fill,"
        f"drawbox=x=0:y=1500:w=1080:h=420:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='WHY GTA 6 HAS':fontcolor=white:fontsize=72:"
        f"x=(w-text_w)/2:y=180:shadowcolor=black@0.9:shadowx=4:shadowy=4,"
        f"drawtext=fontfile='{FONT_PATH}':text='TWO PROTAGONISTS':fontcolor='#ff4499':fontsize=84:"
        f"x=(w-text_w)/2:y=270:shadowcolor=black@0.9:shadowx=4:shadowy=4,"
        f"drawtext=fontfile='{FONT_PATH}':text='JASON + LUCIA EXPLAINED':fontcolor='#00e5ff':fontsize=50:"
        f"x=(w-text_w)/2:y=1640:shadowcolor=black@0.9:shadowx=3:shadowy=3"
    )

    run_cmd([
        "ffmpeg", "-y",
        "-i", thumb_bg,
        "-vf", thumb_vf,
        "-q:v", "1",
        thumbnail_path
    ], "Compiling 1080x1920 high-CTR thumbnail cover")
    shutil.copyfile(thumbnail_path, str(THUMBNAIL_OUTPUT_DIR))

    # STAGE 6: Extract 8 QC Verification Frames
    timer.start("6. Extracting 8 QC Verification Keyframes")
    sample_points = [2.0, 5.0, 9.0, 14.0, 20.0, 26.0, 33.0, 39.0]
    qc_frame_paths = []
    for idx, t in enumerate(sample_points, 1):
        qpath = str(QC_DIR / f"qc_frame_{idx:02d}_{int(t)}s.jpg")
        run_cmd([
            "ffmpeg", "-y",
            "-ss", str(t),
            "-i", master_1080p,
            "-vframes", "1",
            "-q:v", "2",
            qpath
        ], f"Extracting QC frame {idx} at {t}s")
        qc_frame_paths.append(qpath)

    # STAGE 7: YouTube Publishing (Unlisted initially)
    timer.start("7. Publishing to YouTube Data API (Unlisted)")
    yt_title = "Why GTA 6 Has Two Main Characters #Shorts"
    yt_desc = (
        "GTA 6 doesn't give you just one criminal to follow. It gives you two—and they're nothing alike.\n\n"
        "Meet Jason Duval: grew up around criminals, joined the Army, ended up running drugs in the Florida Keys. "
        "Meet Lucia Caminos: raised to fight, ended up in prison for her family. Jason wants an easier life. Lucia wants a better one.\n\n"
        "When an easy score goes wrong, they are thrust into a criminal conspiracy stretching across the state of Leonida. "
        "Their biggest strength—and possibly their biggest weakness—is each other.\n\n"
        "🎮 Game: Grand Theft Auto VI (Rockstar Games)\n"
        "🎙️ Narration: ElevenLabs Liam (Conversational Master)\n"
        "📐 Resolution: 8K Super-Resolution (4320x7680) Master\n\n"
        "#GTA6 #GTAVI #GrandTheftAuto #RockstarGames #JasonAndLucia #Gaming #Shorts"
    )
    yt_tags = ["GTA 6", "GTAVI", "Grand Theft Auto VI", "Rockstar Games", "Jason Duval", "Lucia Caminos", "Gaming", "Shorts"]

    yt_res = upload_video(
        file_path=Path(master_8k),
        title=yt_title,
        description=yt_desc,
        tags=yt_tags,
        privacy_status="unlisted",
        thumbnail_path=Path(thumbnail_path)
    )
    print("=" * 70)
    print("🎉 YOUTUBE PUBLISH SUCCESSFUL!")
    print(f"   Video ID:  {yt_res.get('id')}")
    print(f"   Watch URL: {yt_res.get('url')}")
    print("=" * 70)

    # STAGE 8: Database Registration
    timer.start("8. Catalog Deduplication & Database Logging")
    db = TopicDatabase()
    db.add_completed_topic(
        topic_slug="gta_6_two_main_characters",
        movie_name="Grand Theft Auto VI",
        film_cluster="Gaming & Modern Crime",
        title="Why GTA 6 Has Two Main Characters",
        hook="GTA 6 doesn't give you just one criminal to follow. It gives you two—and they're nothing alike.",
        core_thesis="Jason wants an easier life while Lucia wants a better one; their relationship is both their ultimate strength and biggest weakness.",
        category_lens="Character Breakdown",
        scheduled_slot="ANY",
        scheduled_time_iso=None,
        youtube_video_id=yt_res.get("id"),
        youtube_url=yt_res.get("url")
    )

    timer.finish_all()
    print("\n✅ ALL PRODUCTION STAGES COMPLETED SUCCESSFULLY!")
    print(f"   1080p Delivery: {master_1080p}")
    print(f"   8K Master:      {master_8k}")
    print(f"   YouTube URL:    {yt_res.get('url')}")


if __name__ == "__main__":
    build_gta6_short()
