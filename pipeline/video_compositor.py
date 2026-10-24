import os
import subprocess
from pathlib import Path

def detect_letterbox_crop(video_path: str, sample_sec: float = 10.0) -> str:
    """Detects active video rectangle to strip hardcoded letterbox bars from 2.39:1 films."""
    try:
        cmd = [
            "ffmpeg", "-ss", str(sample_sec),
            "-i", str(video_path),
            "-vframes", "5",
            "-vf", "cropdetect=24:16:0",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in reversed(res.stderr.splitlines()):
            if "crop=" in line:
                import re
                m = re.search(r"crop=([0-9:]+)", line)
                if m:
                    return f"crop={m.group(1)},"
    except Exception:
        pass
    # Fallback for cinemascope: 140px top and bottom letterbox bars
    return "crop=in_w:800:0:140,"

def render_70pct_scene_clip(input_video: str, start_sec: float, duration: float, output_path: str, fps: int = 30):
    """
    Renders a 9:16 vertical clip where movie footage takes 70% of screen height (1344px out of 1920px),
    stripping letterbox bars and featuring a dynamically blurred, vibrant ambient background.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    crop_filter = detect_letterbox_crop(input_video, sample_sec=start_sec + 1.0)
    
    vf = (
        f"[0:v]{crop_filter}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45,eq=brightness=-0.05:contrast=1.1:saturation=1.3[bg];"
        f"[0:v]{crop_filter}scale=-1:1344,crop=1080:1344:(in_w-1080)/2:0[fg];"
        f"[bg][fg]overlay=0:288,setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-t", f"{duration:.3f}",
        "-i", str(input_video),
        "-filter_complex", vf,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for clip {output_path}: {res.stderr[:300]}")
    return output_path

def render_100pct_fullscreen_clip(input_video: str, start_sec: float, duration: float, output_path: str, x_offset: int = 0, fps: int = 30):
    """
    Renders a 9:16 vertical clip where movie footage fills 100% of the screen (full bleed 1080x1920),
    stripping letterbox bars and applying subject-focused pan & scan.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    crop_filter = detect_letterbox_crop(input_video, sample_sec=start_sec + 1.0)
    
    crop_x = f"(in_w-1080)/2+{x_offset}" if x_offset != 0 else "(in_w-1080)/2"
    vf = f"[0:v]{crop_filter}scale=-1:1920,crop=1080:1920:{crop_x}:0,setsar=1"

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-t", f"{duration:.3f}",
        "-i", str(input_video),
        "-filter_complex", vf,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for clip {output_path}: {res.stderr[:300]}")
    return output_path

def assemble_final_video(
    scene_clips: list,
    audio_path: str,
    ass_subtitle_path: str,
    output_mp4: str,
    temp_dir: str
):
    """Concatenates video clips, mixes audio with ambient score, and burns subtitles."""
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    # 1. Write concat list
    concat_list_file = os.path.join(temp_dir, "concat_clips.txt")
    with open(concat_list_file, "w") as f:
        for p in scene_clips:
            f.write(f"file '{os.path.abspath(p)}'\n")

    raw_video = os.path.join(temp_dir, "raw_concatenated.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        raw_video
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL)

    # 2. Synthesize subtle cinematic tension score & mix with voiceover
    ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path]
    dur_str = subprocess.check_output(ffprobe_cmd).decode().strip()
    total_dur = float(dur_str)

    mixed_audio = os.path.join(temp_dir, "mixed_audio.wav")
    mix_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=f=55:d={total_dur},volume=0.07,lowpass=f=120",
        "-f", "lavfi", "-i", f"anoisesrc=d={total_dur}:c=pink:r=24000:a=0.02,lowpass=f=400,volume=0.10",
        "-i", audio_path,
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=first[amb];[2:a]volume=1.25[vocal];[amb][vocal]amix=inputs=2:duration=first:dropout_transition=2[outa]",
        "-map", "[outa]",
        "-c:a", "pcm_s16le",
        mixed_audio
    ]
    subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL)

    # 3. Burn ASS subtitles and output final 1080x1920 MP4
    print("Burning in Center Bold Subtitles and exporting 1080p Master...")
    final_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", mixed_audio,
        "-vf", f"ass={ass_subtitle_path}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    subprocess.run(final_cmd, check=True)
    print(f"🎉 1080p Cinema X-Ray Video: {output_mp4}")
    return output_mp4

def export_4k_uhd(input_mp4: str, output_4k_mp4: str):
    """Upscales 1080x1920 video to pristine 4K UHD (2160x3840) using hardware acceleration."""
    os.makedirs(os.path.dirname(output_4k_mp4), exist_ok=True)
    print(f"🚀 Upscaling to 4K UHD (2160x3840)...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_mp4),
        "-vf", "scale=2160:3840:flags=lanczos",
        "-c:v", "h264_videotoolbox",
        "-b:v", "40M",
        "-c:a", "copy",
        str(output_4k_mp4)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Falling back to CPU 4K upscale...")
        cmd_cpu = [
            "ffmpeg", "-y",
            "-i", str(input_mp4),
            "-vf", "scale=2160:3840:flags=lanczos",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "17",
            "-c:a", "copy",
            str(output_4k_mp4)
        ]
        subprocess.run(cmd_cpu, check=True)
    
    print(f"🌟 4K UHD Cinema X-Ray Video: {output_4k_mp4}")
    return output_4k_mp4
