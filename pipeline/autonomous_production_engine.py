"""
Cinema Decoded: Autonomous Production Engine
============================================
End-to-end autonomous video production pipeline for Cinema Decoded YouTube Shorts.
Connects:
1. Executive Producer & Lead Writer Agent (Gemini + youtube-agent-skill hookscore)
2. Audio Generator (ElevenLabs Liam / Gemini TTS single-take, linear normalized, zero whoosh/drone)
3. Subtitle Engine (Arc Reactor Cyan HUD ASS subtitles with vivid Stark cyan highlights)
4. Footage Acquisition & Scene Planner (yt-dlp clip search or local asset cache)
5. 70% Cinematic Visual Compositor (1080x1344 active framing, ambient blur, motion, callouts)
6. 1080p Master Assembly & Burn-in
7. Hardware-Accelerated 8K Super-Resolution (4320x7680 @ 85 Mbps HEVC)
8. Vertical Thumbnail & Automated Quality Control (8 QC frames + json report)
9. Registry & Deduplication Gatekeeper (completed_topics.json & SQLite)
"""

import os
import sys
import re
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.executive_producer_agent import (
    ExecutiveProducerAgent,
    extract_approved_script,
    extract_topic_metadata
)
from pipeline.audio_generator import generate_achird_audio, verify_audio_file
from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles
from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution
from pipeline.topic_database import TopicDatabase

OUTPUT_DIR = REPO_ROOT / "output"
FINAL_8K_DIR = OUTPUT_DIR / "final_video"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails_short"
PROJECTS_DIR = REPO_ROOT / "projects"
CLIP_CACHE_DIR = OUTPUT_DIR / "clip_cache"

FINAL_8K_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
CLIP_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def probe_media_duration(file_path: Union[str, Path]) -> float:
    """Accurately extracts media duration in seconds via ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        return float(res)
    except Exception as e:
        raise RuntimeError(f"Failed to probe duration of {file_path}: {e}")


def sanitize_slug(text: str) -> str:
    """Converts a movie/topic title to a safe file and directory slug."""
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", s)


def get_bold_font_path() -> str:
    """Finds the path to a bold sans-serif font across macOS and Ubuntu Linux."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


class AutonomousProductionEngine:
    """The master coordinator for autonomous Cinema Decoded video creation."""

    def __init__(self):
        self.ep_agent = ExecutiveProducerAgent()
        self.topic_db = TopicDatabase()
        self.font_path = get_bold_font_path()

    def parse_shot_callouts_from_brief(self, brief_text: str) -> Dict[int, str]:
        """
        Extracts graphic callouts defined in section 3 of the brief.
        Example: Centered subtle documentary callout at y=340: `WHY DOES A SALVAGE CREW HAVE ALIEN WEAPONS?`
        """
        callouts = {}
        # Pattern to capture shot number and graphic callout
        shot_blocks = re.findall(
            r"###\s+SHOT\s+(\d+)[^\n]*\n(.*?)(?=\n###|\n---|\n##|$)",
            brief_text,
            re.DOTALL
        )
        for num_str, block in shot_blocks:
            shot_idx = int(num_str)
            g_match = re.search(r"\*\*Graphic\*\*:\s*(?:Centered[^\n]*at\s*y=(\d+):\s*)?`([^`]+)`", block)
            if g_match:
                y_pos = int(g_match.group(1)) if g_match.group(1) else 340
                text = re.sub(r"[^A-Za-z0-9\s-]", "", g_match.group(2)).strip().upper()
                callouts[shot_idx] = (
                    f"drawtext=fontfile='{self.font_path}':"
                    f"text='{text}':fontcolor=white:fontsize=32:x=(w-text_w)/2:y={y_pos}:"
                    f"shadowcolor=black@0.9:shadowx=2:shadowy=2"
                )
            else:
                # Secondary pattern: look for plain text in graphic
                g_plain = re.search(r"\*\*Graphic\*\*:\s*([^\n]+)", block)
                if g_plain and "none" not in g_plain.group(1).lower() and len(g_plain.group(1).strip()) > 5:
                    clean_text = re.sub(r"[^A-Za-z0-9\s-]", "", g_plain.group(1)).strip().upper()
                    callouts[shot_idx] = (
                        f"drawtext=fontfile='{self.font_path}':"
                        f"text='{clean_text}':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=340:"
                        f"shadowcolor=black@0.9:shadowx=2:shadowy=2"
                    )
        return callouts

    def acquire_footage_for_topic(
        self,
        movie_name: str,
        scene_description: str,
        topic_slug: str
    ) -> Path:
        """
        Finds or downloads verified 1080p movie footage:
        1. Checks local assets/footage/<movie_slug>/
        2. Checks direct assets/footage/*.mp4
        3. Checks output/clip_cache/
        4. Uses clip_search_engine with yt-dlp to download from YouTube.
        5. Falls back to verified repo footage assets if network/bot blocked in CI.
        """
        movie_clean = re.sub(r"\s*\(\d{4}\)", "", movie_name).strip()
        slug_m = sanitize_slug(movie_clean)
        slug_no_the = re.sub(r"^the_", "", slug_m)

        # 1. Local assets directory
        for cand in [slug_m, slug_no_the]:
            local_dir = REPO_ROOT / "assets" / "footage" / cand
            if local_dir.exists():
                mp4s = sorted(list(local_dir.rglob("*.mp4")))
                curated = [p for p in mp4s if "raw_sources" not in str(p)]
                if curated:
                    print(f"🎬 Found {len(curated)} curated local clips in: {local_dir}")
                    return curated
                elif mp4s:
                    print(f"🎬 Found {len(mp4s)} local clips in: {local_dir}")
                    return mp4s

        # 1b. Check direct assets/footage/*.mp4 for matching film title
        direct_matches = [f for f in (REPO_ROOT / "assets" / "footage").glob("*.mp4") if slug_m in f.stem.lower() or slug_no_the in f.stem.lower()]
        if direct_matches:
            print(f"🎬 Found matched local footage in assets/footage: {len(direct_matches)} clips")
            return direct_matches

        # 2. Check clip cache for matched filename
        cached_matches = [f for f in CLIP_CACHE_DIR.glob("*.mp4") if slug_m in f.stem or slug_no_the in f.stem or topic_slug in f.stem]
        if cached_matches:
            print(f"🎬 Found cached footage: {len(cached_matches)} clips")
            return cached_matches

        # 3. Use clip_search_engine via yt-dlp
        print(f"🔍 Searching YouTube for verified 1080p footage: {movie_clean} - {scene_description}...")
        try:
            from pipeline.clip_search_engine import search_and_acquire_clip
            clip_info = search_and_acquire_clip(
                query=f"{movie_clean} {scene_description} scene 1080p",
                movie_name=movie_clean,
                focus_characters=[],
                require_authorized_license=False,
                allow_network_download=True
            )
            if clip_info and clip_info.file_path and clip_info.file_path.exists():
                print(f"✅ Downloaded & cached footage to: {clip_info.file_path}")
                return [clip_info.file_path]
        except Exception as e:
            print(f"⚠️ Clip search engine note: {e}")

        # 3b. Broader movie scene query retry if specific query did not yield results
        try:
            from pipeline.clip_search_engine import search_and_acquire_clip
            print(f"🔍 Retrying YouTube with broader scene query: {movie_clean} movie scene 1080p...")
            clip_info = search_and_acquire_clip(
                query=f"{movie_clean} scene 1080p",
                movie_name=movie_clean,
                focus_characters=[],
                require_authorized_license=False,
                allow_network_download=True
            )
            if clip_info and clip_info.file_path and clip_info.file_path.exists():
                print(f"✅ Downloaded & cached footage via broader query: {clip_info.file_path}")
                return [clip_info.file_path]
        except Exception as e:
            print(f"⚠️ Broader clip search note: {e}")

        # 4. Check if any existing mp4 in clip_cache matches this specific movie
        all_cached = sorted(list(CLIP_CACHE_DIR.glob("*.mp4")), key=lambda p: p.stat().st_size, reverse=True)
        fallback_cached = [f for f in all_cached if slug_m in f.stem.lower() or slug_no_the in f.stem.lower() or topic_slug in f.stem.lower()]
        if fallback_cached:
            print(f"🎬 Found matched cached footage in fallback search: {len(fallback_cached)} clips")
            return fallback_cached

        raise FileNotFoundError(
            f"No authentic footage could be acquired for '{movie_name}'. "
            f"YouTube search and local cache found no matching scene clips."
        )

    def render_70pct_clip_clean(
        self,
        src_video: str,
        start_sec: float,
        duration: float,
        out_path: str,
        callout_filter: Optional[str] = None,
        motion: str = "SLOW_PUSH_IN",
        fps: int = 30
    ) -> str:
        """
        Renders clean 70% cinematic framing (1080x1344) with soft ambient blur background (1080x1920),
        2px matte lines, high-contrast grading, and subtle motion dynamics.
        """
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
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

        extra_overlay = f",{callout_filter}" if callout_filter else ""

        vf = (
            f"[0:v]tpad=stop_mode=clone:stop_duration=1.0,split=2[vpad1][vpad2];"
            f"[vpad1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"boxblur=35:5,eq=brightness=-0.08:contrast=1.15:saturation=1.2[bg];"
            f"[vpad2]{fg_zoom},eq=brightness=-0.03:contrast=1.16:saturation=1.15[fg];"
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
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
            "-t", f"{duration:.3f}",
            "-r", str(fps), "-pix_fmt", "yuv420p", "-an",
            out_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg failed rendering clip {out_path}: {res.stderr[:400]}")
        return out_path

    def assemble_final_1080p(
        self,
        clip_paths: List[str],
        audio_path: str,
        ass_path: str,
        output_mp4: str,
        total_duration: float
    ) -> str:
        """Concatenates video clips, synchronizes master Achird audio, and burns in Arc Reactor Cyan HUD subtitles."""
        os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
        temp_dir = Path(output_mp4).parent / "temp_assembly"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 1. Visual Concat
        inputs = []
        for p in clip_paths:
            inputs.extend(["-i", str(p)])
        filter_inputs = "".join(f"[{i}:v]" for i in range(len(clip_paths)))
        concat_filter = f"{filter_inputs}concat=n={len(clip_paths)}:v=1:a=0[outv]"
        visual_master = str(temp_dir / "visual_master.mp4")

        concat_cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", concat_filter,
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
            visual_master
        ]
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL)

        # 2. Burn in ASS Subtitles and combine with Master Audio
        escaped_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")
        final_cmd = [
            "ffmpeg", "-y",
            "-i", visual_master,
            "-i", audio_path,
            "-vf", f"ass='{escaped_ass}'",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16",
            "-c:a", "aac", "-b:a", "256k",
            "-t", f"{total_duration:.3f}",
            "-movflags", "+faststart",
            output_mp4
        ]
        res = subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg assembly failed: {res.stderr[:400]}")

        # Cleanup temp
        shutil.rmtree(temp_dir, ignore_errors=True)
        return output_mp4

    def generate_vertical_thumbnail(
        self,
        src_video: str,
        title_top: str,
        title_bottom: str,
        out_path: str,
        sample_time: float = 3.0
    ) -> str:
        """Renders a high-CTR 1080x1920 vertical thumbnail with bold yellow/white text."""
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        t_top = re.sub(r"[^A-Za-z0-9\s-]", "", title_top).strip().upper()[:32]
        t_bot = re.sub(r"[^A-Za-z0-9\s-]", "", title_bottom).strip().upper()[:35]

        vf = (
            "[0:v]split=2[vbg][vfg];"
            "[vbg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=30:5,eq=brightness=-0.10:contrast=1.20:saturation=1.3[bg];"
            "[vfg]scale=1080:1344:force_original_aspect_ratio=increase,crop=1080:1344,"
            "eq=brightness=0.04:contrast=1.18:saturation=1.2[fg];"
            "[bg][fg]overlay=0:288,"
            "drawbox=x=0:y=287:w=1080:h=2:color=black@0.8:t=fill,"
            "drawbox=x=0:y=1632:w=1080:h=2:color=black@0.8:t=fill,"
            f'drawtext=fontfile="{self.font_path}":text="{t_top}":fontcolor=white:fontsize=36:x=(w-text_w)/2:y=220:shadowcolor=black@0.9:shadowx=3:shadowy=3,'
            f'drawtext=fontfile="{self.font_path}":text="{t_bot}":fontcolor=0xF5C518:fontsize=52:x=(w-text_w)/2:y=1680:shadowcolor=black@0.9:shadowx=3:shadowy=3'
        )

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{sample_time:.2f}",
            "-i", str(src_video),
            "-filter_complex", vf,
            "-vframes", "1",
            out_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"⚠️ Thumbnail rendering warning: {res.stderr[:200]}")
        return out_path

    def extract_qc_frames(self, video_path: str, qc_dir: Path, duration: float) -> List[str]:
        """Extracts 8 evenly spaced QC frames across the timeline."""
        qc_dir.mkdir(parents=True, exist_ok=True)
        timestamps = [
            round(duration * 0.05, 2),
            round(duration * 0.15, 2),
            round(duration * 0.28, 2),
            round(duration * 0.42, 2),
            round(duration * 0.58, 2),
            round(duration * 0.72, 2),
            round(duration * 0.85, 2),
            round(duration * 0.95, 2)
        ]
        frame_paths = []
        for idx, ts in enumerate(timestamps, 1):
            out_img = qc_dir / f"qc_frame_{idx:02d}_{int(ts)}s.jpg"
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{ts:.2f}",
                "-i", str(video_path),
                "-vframes", "1",
                str(out_img)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out_img.exists():
                frame_paths.append(str(out_img))
        return frame_paths

    def produce(
        self,
        topic: Optional[Dict[str, Any]] = None,
        movie: Optional[str] = None,
        scene: Optional[str] = None,
        brief_file: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
        upscale_8k: bool = True,
        upload_youtube: bool = False,
        privacy_status: str = "unlisted"
    ) -> Dict[str, Any]:
        """
        Executes the entire autonomous pipeline end-to-end.
        """
        start_time = time.time()
        print("=" * 70)
        print("🚀 CINEMA DECODED: AUTONOMOUS PRODUCTION ENGINE STARTING")
        print("=" * 70)

        # STAGE 1: Ideate & Generate Executive Producer Brief
        if brief_file and Path(brief_file).exists():
            print(f"📄 Loading approved brief from file: {brief_file}")
            brief_text = Path(brief_file).read_text(encoding="utf-8")
            meta = extract_topic_metadata(brief_text)
            script_text = extract_approved_script(brief_text)
            topic_slug = meta.get("topic_slug", "cinema_decoded_video")
            movie_title = meta.get("movie", "Cinema Decoded")
            scene_desc = meta.get("central_discovery", "")
        else:
            if not topic:
                if movie:
                    from pipeline.executive_producer_agent import CATALOG_PATH
                    cat_scenes = json.loads(CATALOG_PATH.read_text(encoding="utf-8")).get("scenes", [])
                    matched = next((s for s in cat_scenes if movie.lower() in s.get("movie", "").lower()), None)
                    if matched and (not scene or scene.lower() in matched.get("topic", "").lower()):
                        topic = matched
                    else:
                        print(f"🎬 Ideating dynamic cinematic breakdown for film: '{movie}' (scene: '{scene}')...")
                        topic = self.ep_agent.ideate_topic_for_movie(movie=movie, scene=scene)
                if not topic:
                    topic = self.ep_agent.pick_next_topic()

            print(f"🎯 Selected Topic: {topic['movie']} — {topic['topic']}")
            print(f"💡 Core Thesis: {topic['core_thesis']}")

            # Score & select hook
            hook, score_data = self.ep_agent.select_best_hook(
                topic["movie"], topic["topic"], topic["core_thesis"]
            )
            print(f"🔥 Champion Hook ({score_data.get('score')} pts, {score_data.get('grade')}): {hook}")

            # Generate 11-section Executive Producer Brief
            print("✍️  Generating complete 11-section Executive Producer Brief with Gemini...")
            brief_text = self.ep_agent.generate_executive_producer_brief(
                movie=topic["movie"],
                topic=topic["topic"],
                core_thesis=topic["core_thesis"],
                scene_description=topic["scene_description"],
                best_hook=hook
            )
            meta = extract_topic_metadata(brief_text)
            script_text = extract_approved_script(brief_text)
            topic_slug = topic["topic_slug"]
            movie_title = topic["movie"]
            scene_desc = topic["scene_description"]

        # Setup Project Directory
        proj_dir = PROJECTS_DIR / f"cinema-decoded-{topic_slug}"
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / "audio").mkdir(exist_ok=True)
        (proj_dir / "clips").mkdir(exist_ok=True)
        (proj_dir / "out").mkdir(exist_ok=True)
        (proj_dir / "qc_frames").mkdir(exist_ok=True)

        # Save Brief & Script
        (proj_dir / "brief.md").write_text(brief_text, encoding="utf-8")
        (proj_dir / "script.txt").write_text(script_text, encoding="utf-8")
        print(f"✅ Brief saved to: {proj_dir / 'brief.md'}")

        # STAGE 2: Studio Voiceover (ElevenLabs Liam / Gemini TTS, Single-Take, Linear Normalized)
        print("\n🎙️  STAGE 2: Generating Studio Voiceover (ElevenLabs Liam)...")
        master_audio_path = str(proj_dir / "audio" / "master_audio.wav")
        if not (os.path.exists(master_audio_path) and os.path.getsize(master_audio_path) > 10000):
            generate_achird_audio(script_text, master_audio_path)
        actual_audio_dur = verify_audio_file(master_audio_path, video_format="SHORT_45_SEC")
        print(f"✅ Studio voiceover ready: {actual_audio_dur:.2f}s (Static linear normalization, -1.0 dBFS)")

        # STAGE 3: Subtitle Generation (Arc Reactor Cyan HUD ASS)
        print("\n📝 STAGE 3: Generating Arc Reactor Cyan HUD Synchronized Subtitles...")
        subtitles_json_path = str(proj_dir / "subtitles.json")
        ass_path = str(proj_dir / "subtitles.ass")
        if not (os.path.exists(ass_path) and os.path.getsize(ass_path) > 500):
            cards = generate_timed_subtitles(
                audio_path=master_audio_path,
                script_text=script_text,
                total_duration=actual_audio_dur,
                cache_json_path=subtitles_json_path
            )
            build_ass_subtitles(cards, ass_path, video_format="SHORT_45_SEC")
        print(f"✅ Subtitles ready: {ass_path}")

        if dry_run:
            print("\n🏁 DRY-RUN COMPLETE: Topic, Brief, Audio, and Subtitles successfully created!")
            return {
                "status": "DRY_RUN_COMPLETE",
                "topic_slug": topic_slug,
                "project_dir": str(proj_dir),
                "brief_file": str(proj_dir / "brief.md"),
                "audio_file": master_audio_path,
                "audio_duration": actual_audio_dur,
                "subtitles_file": ass_path
            }

        # STAGE 4: Footage Acquisition & Beat Slicing
        print("\n🎬 STAGE 4: Acquiring Footage & Slicing 70% Cinematic Beats...")
        footage_clips = self.acquire_footage_for_topic(movie_title, scene_desc, topic_slug)
        if not isinstance(footage_clips, list):
            footage_clips = [footage_clips]
        print(f"📼 Source footage pool: {len(footage_clips)} clips available")

        # Parse Graphic Callouts from Brief
        callouts = self.parse_shot_callouts_from_brief(brief_text)

        # Build Beats based on Subtitle Sentences or Even Intervals
        sentences = [s.strip() for s in re.split(r"(?<=[.?!])\s+", script_text) if s.strip()]
        num_beats = max(5, min(9, len(sentences)))
        beat_dur = round(actual_audio_dur / num_beats, 2)
        beats = []
        clip_paths = []

        motions = ["SLOW_PUSH_IN", "SLOW_PAN_LEFT", "SLOW_PUSH_IN", "SLOW_PAN_RIGHT", "FAST_ZOOM", "SLOW_PUSH_IN", "SLOW_PAN_LEFT"]

        print(f"✂️  Slicing {num_beats} beats matching narration cadence across {len(footage_clips)} clips...")
        for i in range(num_beats):
            idx = i + 1
            curr_dur = beat_dur if idx < num_beats else round(actual_audio_dur - (beat_dur * (num_beats - 1)), 2)

            # Cycle through available clips for maximum visual variety
            src_clip = Path(footage_clips[i % len(footage_clips)])
            src_dur = probe_media_duration(src_clip)

            # Safe start offset within source video
            if len(footage_clips) > 1:
                # If we have multiple clips, start near beginning with safety margin
                max_offset = max(0.0, src_dur - curr_dur)
                offset_start = min(0.5, max_offset / 2.0) if max_offset > 0 else 0.0
            else:
                offset_start = (i * (src_dur - curr_dur) / num_beats) if src_dur > curr_dur + 5.0 else (i * 2.5)
                offset_start = max(0.0, min(offset_start, max(0.0, src_dur - curr_dur)))

            motion = motions[i % len(motions)]
            callout = callouts.get(idx)
            out_clip = str(proj_dir / "clips" / f"beat_{idx:02d}.mp4")

            self.render_70pct_clip_clean(
                src_video=str(src_clip),
                start_sec=offset_start,
                duration=curr_dur,
                out_path=out_clip,
                callout_filter=callout,
                motion=motion
            )
            clip_paths.append(out_clip)
            beats.append({
                "beat_id": f"beat_{idx:02d}",
                "start": round(i * beat_dur, 2),
                "duration": curr_dur,
                "source_clip": str(src_clip),
                "motion": motion,
                "has_callout": callout is not None
            })

        # Save Scene Plan
        scene_plan = {
            "movie": movie_title,
            "topic": meta.get("headline", topic_slug),
            "total_duration": actual_audio_dur,
            "beats": beats
        }
        (proj_dir / "scene_plan.json").write_text(json.dumps(scene_plan, indent=2), encoding="utf-8")

        # STAGE 5: 1080p Master Assembly
        print("\n🎞️  STAGE 5: Assembling 1080p Delivery Master with Arc Reactor Cyan HUD Subtitles...")
        master_1080p = str(proj_dir / "out" / f"cinema_decoded_{topic_slug}_1080p.mp4")
        if not (os.path.exists(master_1080p) and os.path.getsize(master_1080p) > 1000000):
            self.assemble_final_1080p(
                clip_paths=clip_paths,
                audio_path=master_audio_path,
                ass_path=ass_path,
                output_mp4=master_1080p,
                total_duration=actual_audio_dur
            )
        dur_1080 = probe_media_duration(master_1080p)
        size_1080_mb = round(os.path.getsize(master_1080p) / (1024 * 1024), 2)
        print(f"✅ 1080p Master ready: {master_1080p} ({dur_1080:.2f}s, {size_1080_mb} MB)")

        # STAGE 6: Apple Silicon Hardware 8K Super-Resolution
        final_8k_repo = FINAL_8K_DIR / f"cinema_xray_{topic_slug}_8k.mp4"
        if upscale_8k:
            print("\n🚀 STAGE 6: Hardware-Accelerated 8K Super-Resolution (4320x7680 @ 85 Mbps)...")
            master_8k_local = str(proj_dir / "out" / f"cinema_decoded_{topic_slug}_8k.mp4")
            if not (os.path.exists(master_8k_local) and os.path.getsize(master_8k_local) > 5000000):
                upgrade_to_super_resolution(
                    input_video=master_1080p,
                    output_video=master_8k_local,
                    target_tier="8K",
                    sharpness=0.55,
                    bitrate="85M"
                )
            if not final_8k_repo.exists() or os.path.getsize(str(final_8k_repo)) != os.path.getsize(master_8k_local):
                shutil.copyfile(master_8k_local, str(final_8k_repo))
            dur_8k = probe_media_duration(str(final_8k_repo))
            size_8k_mb = round(os.path.getsize(str(final_8k_repo)) / (1024 * 1024), 2)
            print(f"🏆 8K Master exported to: {final_8k_repo} ({dur_8k:.2f}s, {size_8k_mb} MB)")
        else:
            final_8k_repo = None
            size_8k_mb = 0

        # STAGE 7: High-CTR Vertical Thumbnail & Quality Control
        print("\n🖼️  STAGE 7: Generating High-CTR Thumbnail & Extracting QC Frames...")
        thumb_local = str(proj_dir / "thumbnail.jpg")
        thumb_global = str(THUMBNAILS_DIR / f"{topic_slug}_thumb.jpg")
        headline_parts = meta.get("headline", "THE HIDDEN TRUTH").split(":")
        t_top = headline_parts[0].strip()[:30]
        t_bot = headline_parts[1].strip()[:35] if len(headline_parts) > 1 else meta.get("movie", "CINEMA DECODED")

        self.generate_vertical_thumbnail(
            src_video=clip_paths[0],
            title_top=t_top,
            title_bottom=t_bot,
            out_path=thumb_local
        )
        shutil.copyfile(thumb_local, thumb_global)

        # QC Frames
        target_video_for_qc = str(final_8k_repo) if final_8k_repo and final_8k_repo.exists() else master_1080p
        qc_frames = self.extract_qc_frames(target_video_for_qc, proj_dir / "qc_frames", actual_audio_dur)

        # Copy QC frames to artifact directory if available
        art_dir = Path("/Users/vinaybt/.gemini/antigravity/brain/f5bbdfa3-43d4-4e1d-a047-6bac52b0ed76")
        if art_dir.exists():
            shutil.copyfile(thumb_local, str(art_dir / f"qc_{topic_slug}_thumbnail.jpg"))
            for qcf in qc_frames:
                shutil.copyfile(qcf, str(art_dir / f"qc_{topic_slug}_{Path(qcf).name}"))

        # STAGE 8: YouTube Upload (Optional / Automated)
        yt_id = None
        yt_url = None
        if upload_youtube and not dry_run:
            print("\n🚀 STAGE 8: Publishing to YouTube...")
            try:
                from pipeline.youtube_uploader import upload_video
                upload_target = final_8k_repo if (final_8k_repo and final_8k_repo.exists()) else Path(master_1080p)
                yt_title = f"{movie_title} — {meta.get('headline', topic.get('topic', 'Analysis'))} #Shorts"[:100]
                yt_desc = (
                    f"{meta.get('central_discovery', scene_desc)}\n\n"
                    f"🎬 Film: {movie_title}\n"
                    f"🎙️ Narration: ElevenLabs Liam (Cinema Decoded Lead Voice)\n"
                    f"📐 Resolution: 8K Super-Resolution (4320x7680) Master\n\n"
                    f"#CinemaDecoded #FilmAnalysis #Shorts #MovieExplained"
                )
                yt_tags = ["Cinema Decoded", "Cinema X-Ray", movie_title, "Film Analysis", "Movie Explained", "Shorts"]
                yt_res = upload_video(
                    file_path=upload_target,
                    title=yt_title,
                    description=yt_desc,
                    tags=yt_tags,
                    privacy_status=privacy_status
                )
                yt_id = yt_res.get("id")
                yt_url = yt_res.get("url")
                print("=" * 70)
                print("✅ YOUTUBE UPLOAD COMPLETE!")
                print(f"   Video ID: {yt_id}")
                print(f"   URL:      {yt_url}")
                print(f"   Privacy:  {privacy_status}")
                print("=" * 70)
            except Exception as e:
                print(f"⚠️ YouTube upload error: {e}")

        # STAGE 9: Register Completed Topic in Database
        print("\n💾 STAGE 9: Registering Topic in Database & Deduplication Gatekeeper...")
        self.topic_db.add_completed_topic(
            topic_slug=topic_slug,
            movie_name=movie_title,
            film_cluster="Cinematic Psychology & Visual Storytelling",
            title=meta.get("headline", topic_slug),
            hook=script_text.split(".")[0],
            core_thesis=meta.get("central_discovery", scene_desc),
            category_lens="Film Scene Analysis",
            scheduled_slot="ANY",
            scheduled_time_iso=None,
            youtube_video_id=yt_id,
            youtube_url=yt_url
        )

        total_time_sec = round(time.time() - start_time, 2)
        print("=" * 70)
        print(f"🎉 PRODUCTION COMPLETED SUCCESSFULLY IN {total_time_sec:.2f}s ({total_time_sec/60:.2f}m)!")
        print(f"   8K Master: {final_8k_repo}")
        print(f"   1080p Delivery: {master_1080p}")
        if yt_url:
            print(f"   YouTube: {yt_url} ({privacy_status})")
        print("=" * 70)

        return {
            "status": "COMPLETED",
            "topic_slug": topic_slug,
            "movie": movie_title,
            "headline": meta.get("headline", topic_slug),
            "script": script_text,
            "audio_duration": actual_audio_dur,
            "master_8k_path": str(final_8k_repo) if final_8k_repo else None,
            "master_8k_size_mb": size_8k_mb,
            "delivery_1080p_path": master_1080p,
            "delivery_1080p_size_mb": size_1080_mb,
            "thumbnail_path": thumb_global,
            "qc_frames": qc_frames,
            "youtube_id": yt_id,
            "youtube_url": yt_url,
            "total_time_seconds": total_time_sec
        }


if __name__ == "__main__":
    engine = AutonomousProductionEngine()
    print("Testing autonomous topic picking & brief generation (dry run)...")
    res = engine.produce(dry_run=True)
    print("Engine Dry Run Result:", res)

