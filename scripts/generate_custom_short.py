import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.audio_generator import generate_achird_audio
from pipeline.subtitle_engine import generate_timed_subtitles, build_ass_subtitles
from pipeline.video_compositor import render_70pct_scene_clip, assemble_final_video
from pipeline.thumbnail_generator import extract_best_keyframe, apply_cinema_xray_theme
from pipeline.qa_gatekeeper import inspect_final_render

def create_tony_nanotech_short():
    print("="*70)
    print("🚀 GENERATING NEW SHORT-FORM VIDEO: TONY STARK'S NANOTECH SECRET")
    print("="*70)
    
    job_slug = "tony_nanotech_secret"
    output_dir = REPO_ROOT / "output"
    
    # 1. Script
    script_text = (
        "When Tony Stark double-tapped his chest in Infinity War, you missed the most chilling detail in the entire MCU. "
        "Notice the nanotech didn't just deploy from the housing unit. It instantly vaporized his sunglasses and dissolved the fabric of his jacket into raw carbon. "
        "Because after the Battle of New York, Tony developed severe PTSD. He realized that half a second was the difference between saving Earth and watching everyone die. "
        "The Mark Fifty wasn't engineered for comfort. It was a panic button designed to consume whatever he was wearing, sacrificing his own clothes to form protective plating before an alien blade could pierce his heart."
    )
    
    script_file = output_dir / "script" / f"{job_slug}_script.txt"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text(script_text, encoding="utf-8")
    print(f"📝 Script written: {len(script_text.split())} words")
    
    # 2. Studio Audio (Gemini Achird)
    audio_file = output_dir / "audio" / f"{job_slug}_voiceover.wav"
    audio_file.parent.mkdir(parents=True, exist_ok=True)
    print("🎙️ Synthesizing Gemini Achird Voiceover...")
    dur = generate_achird_audio(script_text, str(audio_file), video_format="SHORT_45_SEC")
    print(f"✅ Mastered voiceover: {audio_file.name} ({dur:.2f}s)")
    
    # 3. Subtitles (Center Bold Stroke)
    sub_json = output_dir / "script" / f"{job_slug}_subtitles.json"
    ass_path = output_dir / "temp" / f"{job_slug}_subtitles_center_bold.ass"
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    print("💬 Aligning Center Bold Subtitles with faster-whisper...")
    cards = generate_timed_subtitles(str(audio_file), script_text, dur, str(sub_json), video_format="SHORT_45_SEC")
    build_ass_subtitles(cards, str(ass_path), video_format="SHORT_45_SEC")
    print(f"✅ Generated {len(cards)} subtitle cards")
    
    # 4. Video Composition (70% ambient vertical framing)
    source_footage = REPO_ROOT / "projects" / "marvel-decoded" / "raw_video" / "tony_suitup.mp4"
    if not source_footage.exists():
        raise FileNotFoundError(f"Source footage not found: {source_footage}")
    
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    
    titan_footage = REPO_ROOT / "projects" / "marvel-decoded" / "raw_video" / "tony_thanos.mp4"
    cuts = [
        (source_footage, 99.5, 3.5, "Tony double-taps chest reactor"),
        (source_footage, 102.5, 3.5, "Strides forward as nanotech spreads"),
        (source_footage, 104.5, 3.5, "Nanotech gauntlet and arm form"),
        (source_footage, 106.8, 5.0, "Sunglasses off, nanotech crawls neck"),
        (source_footage, 108.8, 4.5, "Full suit locks, helmet seals, eyes ignite"),
        (source_footage, 111.0, 5.2, "Nanotech shield blocks giant hammer"),
        (source_footage, 114.5, 5.0, "Nanotech wings/cannons deploy"),
        (source_footage, 117.2, 3.0, "Massive repulsor blast knocks enemy back"),
        (titan_footage, 97.5, 2.9, "Titan: Thanos with blade and depleted armor"),
    ]

    scene_clips = []
    print(f"🎥 Slicing {len(cuts)} 70% ambient vertical scene clips...")
    for idx, (src_vid, in_sec, dur_sec, desc) in enumerate(cuts, 1):
        c_path = clips_dir / f"{job_slug}_clip_{idx:02d}.mp4"
        render_70pct_scene_clip(
            input_video=str(src_vid),
            start_sec=in_sec,
            duration=dur_sec,
            output_path=str(c_path)
        )
        scene_clips.append(str(c_path))
    
    final_video = output_dir / "final_video" / f"{job_slug}_final.mp4"
    temp_dir = output_dir / "temp"
    print("🎬 Assembling master 1080x1920 Short with sub-bass drone...")
    assemble_final_video(
        scene_clips=scene_clips,
        audio_path=str(audio_file),
        ass_subtitle_path=str(ass_path),
        output_mp4=str(final_video),
        temp_dir=str(temp_dir)
    )
    print(f"✅ Master Short Rendered: {final_video}")
    
    # 5. Thumbnail Cover
    thumb_path = output_dir / "thumbnails_short" / f"{job_slug}_thumb.jpg"
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    print("🖼️ Generating 1080x1920 Cover Thumbnail...")
    keyframe = extract_best_keyframe(str(final_video), start_sec=2.0, end_sec=15.0)
    apply_cinema_xray_theme(
        frame_img=keyframe,
        hook_text="WHY TONY'S SUIT",
        highlight_word="CONSUMES",
        video_format="SHORT_45_SEC",
        job_slug=job_slug
    )
    
    # 6. QA Gatekeeper
    print("🛡️ Inspecting with QA Gatekeeper...")
    passed, diag = inspect_final_render(
        video_path=final_video,
        thumbnail_path=thumb_path,
        video_format="SHORT_45_SEC"
    )
    if passed:
        print(f"✅ QA PASSED: {diag['resolution']} | {diag['duration_sec']}s | {diag['video_size_mb']} MB")
    else:
        print(f"❌ QA Gatekeeper warning: {diag}")

    return final_video, thumb_path

if __name__ == "__main__":
    vid, th = create_tony_nanotech_short()
    print(f"\n🎉 DONE! Video: {vid}\nThumbnail: {th}")
