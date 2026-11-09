"""
Cinema X-Ray: End-to-End Production & Timeline Profiler
Topic: KGF: Chapter 1 — Why Rocky Bhai Wore Gold Before He Had Money
---------------------------------------------------------------------
Measures the exact runtime of every single production stage:
1. Topic Ideation & Thesis Formulation
2. Voiceover Synthesis & Broadcast Loudness Normalization (-14 LUFS)
3. Faster-Whisper Word-Level Acoustic Subtitle Alignment
4. YouTube Video Acquisition via yt-dlp
5. Scene Footage Slicing & 70% Letterbox Compositing (Ambient Motion Blur)
6. 1080p Master Video Assembly
7. 8K Ultra HD Super-Resolution Render (4320x7680 @ 85 Mbps HEVC)
8. Storage Optimization (Purge intermediate 1080p/4K, keep 8K Master)
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = REPO_ROOT / "output"
FINAL_VIDEO_DIR = OUTPUT_DIR / "final_video"
TEMP_DIR = OUTPUT_DIR / "temp"
CLIPS_DIR = OUTPUT_DIR / "clips" / "kgf_rocky_psychology"
AUDIO_DIR = OUTPUT_DIR / "audio"

FINAL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

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

    def print_summary(self):
        print("\n" + "="*75)
        print("🎬 CINEMA X-RAY: PRODUCTION TIMELINE & BENCHMARK REPORT")
        print("="*75)
        print(f"{'Stage':<48} | {'Duration (s)':<12} | {'Percentage'}")
        print("-" * 75)
        for name, dur in self.records:
            pct = (dur / self.total_time) * 100 if self.total_time > 0 else 0
            print(f"{name:<48} | {dur:>10.2f}s | {pct:>6.1f}%")
        print("-" * 75)
        print(f"{'TOTAL PIPELINE RUNTIME':<48} | {self.total_time:>10.2f}s | {self.total_time/60:>5.2f} min")
        print("="*75 + "\n")


def run_kgf_benchmark():
    timer = PipelineStageTimer()

    # -------------------------------------------------------------
    # STAGE 1: Topic Ideation & Thesis Formulation
    # -------------------------------------------------------------
    timer.start("1. Topic Ideation & Thesis Formulation")
    film = "KGF: Chapter 1"
    title = "Why Rocky Bhai Wore Gold Before He Had Money"
    hook = "When Rocky was a starving boy in Bombay, his dying mother demanded one promise: to die the richest man in the world."
    core_thesis = "Rocky Bhai's obsession wasn't greed; it was grief weaponized into an unstoppable empire. Every gold bar was a monument to the mother the world ignored."
    script_text = (
        "When Rocky was a starving boy in the slums of Bombay, his mother died in his arms of poverty. "
        "Her dying words weren't a plea for survival. She demanded one terrifying promise: "
        "live how you want, but when you die, you must die the richest man in the world. "
        "From that second, Bruce Wayne built an armor of fear, but Rocky built an empire of gold. "
        "Every single coin he earned, every gangster he crushed, wasn't driven by greed. "
        "It was grief weaponized into pure dominance. "
        "Rocky didn't want wealth for power. He conquered the gold mines to prove to the universe "
        "that his mother's promise was law."
    )
    topic_slug = "kgf_rocky_gold_mother_promise"
    print(f"  Film:   {film}")
    print(f"  Title:  {title} ({len(title)} chars)")
    print(f"  Words:  {len(script_text.split())} words")

    # -------------------------------------------------------------
    # STAGE 2: Voiceover Synthesis & Audio Normalization
    # -------------------------------------------------------------
    timer.start("2. Gemini TTS Synthesis & Broadcast Mastering (-14 LUFS)")
    from pipeline.audio_generator import _synthesize_raw_tts
    raw_wav = str(TEMP_DIR / f"{topic_slug}_raw.wav")
    mastered_wav = str(AUDIO_DIR / f"{topic_slug}_achird_fast_112.wav")

    print("  Synthesizing pure Achird voiceover...")
    _synthesize_raw_tts(script_text, raw_wav)

    print("  Accelerating (+12%) and mastering to EBU R128 (-14.0 LUFS)...")
    cmd_audio = [
        "ffmpeg", "-y", "-v", "error",
        "-i", raw_wav,
        "-filter_complex", "[0:a]atempo=1.12,loudnorm=I=-14:TP=-1.5:LRA=11[aout]",
        "-map", "[aout]",
        "-ar", "24000",
        "-c:a", "pcm_s16le",
        mastered_wav
    ]
    subprocess.run(cmd_audio, check=True)

    # Duration probe
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mastered_wav]
    audio_dur = float(subprocess.check_output(probe_cmd).decode().strip())
    print(f"  Mastered Voiceover Duration: {audio_dur:.2f}s")

    # -------------------------------------------------------------
    # STAGE 3: Faster-Whisper Acoustic Subtitle Alignment
    # -------------------------------------------------------------
    timer.start("3. Faster-Whisper Word-Level Acoustic Subtitle Alignment")
    from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles
    ass_path = TEMP_DIR / f"{topic_slug}_centerbold.ass"
    sub_json = OUTPUT_DIR / "script" / f"{topic_slug}_subtitles.json"

    cards = generate_timed_subtitles(mastered_wav, script_text, total_duration=audio_dur, cache_json_path=str(sub_json), force_refresh=True, video_format="SHORT_45_SEC")
    build_ass_subtitles(cards, str(ass_path), video_format="SHORT_45_SEC")
    print(f"  Generated {len(cards)} precision CenterBold subtitle cards (Y=960, Alignment 5)")

    # -------------------------------------------------------------
    # STAGE 4: YouTube Video Acquisition via yt-dlp
    # -------------------------------------------------------------
    timer.start("4. YouTube Video Acquisition via yt-dlp")
    youtube_url = "https://www.youtube.com/watch?v=7bB80VKb1xo"  # Official Hombale Films KGF: The Rise of Rocky!
    downloaded_source = OUTPUT_DIR / "clip_cache" / "kgf_the_rise_of_rocky_1080p.mp4"
    downloaded_source.parent.mkdir(parents=True, exist_ok=True)

    if not downloaded_source.exists() or downloaded_source.stat().st_size < 5000000:
        print(f"  Downloading pristine 1080p source from YouTube ({youtube_url})...")
        dl_cmd = [
            "yt-dlp",
            "-f", "137/bestvideo[height<=1080][ext=mp4]/best[height<=1080]",
            "-o", str(downloaded_source),
            youtube_url
        ]
        subprocess.run(dl_cmd, check=True)
    else:
        print(f"  Reusing verified cached 1080p source ({downloaded_source.stat().st_size / (1024*1024):.1f} MB)")

    src_mb = downloaded_source.stat().st_size / (1024 * 1024)
    print(f"  Acquired Source File: {downloaded_source.name} ({src_mb:.2f} MB)")

    # -------------------------------------------------------------
    # STAGE 5: Scene Footage Slicing & 70% Letterbox Compositing
    # -------------------------------------------------------------
    timer.start("5. Scene Footage Slicing & 70% Letterbox Compositing")
    from pipeline.video_compositor import render_70pct_scene_clip

    # 6 Dynamic Cuts from KGF: The Rise of Rocky (Mother's memory, young Rocky, Bombay rise, gold reign)
    cuts = [
        (10.0, 5.0, "Young Rocky with mother in slum poverty"),
        (28.0, 5.5, "Mother taking the oath from young Rocky"),
        (55.0, 6.0, "Young Rocky earning his first coins in Bombay"),
        (90.0, 5.5, "Rocky growing up, taking down underworld rivals"),
        (135.0, 6.0, "Rocky Bhai suited mass swagger entrance"),
        (180.0, 6.0, "The reign of Rocky Bhai, gold empire")
    ]

    rendered_clips = []
    for idx, (c_in, c_len, c_label) in enumerate(cuts, 1):
        c_out = CLIPS_DIR / f"clip_{idx:02d}.mp4"
        print(f"  Slicing Cut {idx}/{len(cuts)}: {c_label} ({c_in}s, {c_len}s)...")
        render_70pct_scene_clip(str(downloaded_source), c_in, c_len, str(c_out))
        rendered_clips.append(str(c_out))

    # -------------------------------------------------------------
    # STAGE 6: Master 1080p Video Assembly
    # -------------------------------------------------------------
    timer.start("6. Master 1080p Video Assembly")
    from pipeline.video_compositor import assemble_final_video
    final_1080p = FINAL_VIDEO_DIR / f"cinema_xray_{topic_slug}_1080p.mp4"
    assemble_final_video(
        scene_clips=rendered_clips,
        audio_path=mastered_wav,
        ass_subtitle_path=str(ass_path),
        output_mp4=str(final_1080p),
        temp_dir=str(TEMP_DIR / topic_slug)
    )
    print(f"  Master 1080p Rendered: {final_1080p.name} ({final_1080p.stat().st_size / (1024*1024):.2f} MB)")

    # -------------------------------------------------------------
    # STAGE 7: 8K Ultra HD Super-Resolution Render (4320x7680)
    # -------------------------------------------------------------
    timer.start("7. 8K Ultra HD Super-Resolution Render (4320x7680 @ 85 Mbps)")
    from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution
    final_8k = FINAL_VIDEO_DIR / f"cinema_xray_{topic_slug}_8k.mp4"

    upgrade_to_super_resolution(
        input_video=str(final_1080p),
        output_video=str(final_8k),
        target_tier="8K",
        sharpness=0.35,
        bitrate="85M"
    )
    print(f"  👑 8K Ultra HD Master Rendered: {final_8k.name} ({final_8k.stat().st_size / (1024*1024):.2f} MB)")

    # -------------------------------------------------------------
    # STAGE 8: Storage Optimization (Purge intermediate 1080p/4K)
    # -------------------------------------------------------------
    timer.start("8. Storage Optimization (Purge Intermediate Files)")
    # Delete intermediate 1080p, temp cuts, leaving ONLY final 8K
    if final_1080p.exists():
        final_1080p.unlink()
        print(f"  Deleted intermediate 1080p master ({final_1080p.name})")

    # Clean intermediate sliced clips
    for c in rendered_clips:
        if os.path.exists(c):
            os.remove(c)
    print(f"  Cleaned {len(rendered_clips)} intermediate cut clips")

    timer.finish_all()
    timer.print_summary()

    # -------------------------------------------------------------
    # Quality Control Frame Extraction
    # -------------------------------------------------------------
    print("\n🔍 Extracting Quality Control (QC) frames from 8K master...")
    qc_dir = Path("/Users/vinaybt/.gemini/antigravity/brain/f5bbdfa3-43d4-4e1d-a047-6bac52b0ed76")
    for sec, label in [(5, "05s"), (15, "15s"), (25, "25s")]:
        qc_img = qc_dir / f"qc_kgf_8k_{label}.jpg"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"00:00:{sec:02d}",
            "-i", str(final_8k),
            "-vframes", "1",
            "-q:v", "2",
            str(qc_img)
        ], check=True)
        print(f"  QC Frame extracted: {qc_img.name}")

    print("\n🎉 PRODUCTION COMPLETE! Final 8K Master is safely preserved at:")
    print(f"   {final_8k}")
    return timer


if __name__ == "__main__":
    run_kgf_benchmark()

