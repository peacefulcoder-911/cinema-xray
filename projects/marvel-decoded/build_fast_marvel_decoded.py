import os
import subprocess

PROJECT_DIR = "/Users/vinaybt/Downloads/marvel-decoded"
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
RAW_DIR = os.path.join(PROJECT_DIR, "raw_video")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
SCRIPT_DIR = os.path.join(PROJECT_DIR, "script")

ULTRON_VID = os.path.join(RAW_DIR, "ultron_hammer.mp4")
ENDGAME_VID = os.path.join(RAW_DIR, "endgame_mjolnir.mp4")
VOICEOVER_WAV = os.path.join(AUDIO_DIR, "voiceover_fast.wav")
ASS_SUBTITLES = os.path.join(SCRIPT_DIR, "marvel_decoded_fast.ass")

FINAL_MP4 = os.path.join(OUT_DIR, "marvel_decoded_fast_final.mp4")

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

def run_cmd(cmd, desc=""):
    print(f"\n--- {desc} ---")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:")
        print(res.stderr)
        raise RuntimeError(f"FFmpeg failed: {res.stderr}")
    return res

def make_video_segment(in_vid, start_t, dur, out_name):
    """Render a normal speed video segment with 9:16 vertical layout (blurred bg + sharp fg)"""
    out_path = os.path.join(CLIPS_DIR, out_name)
    filter_str = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];"
        "[0:v]scale=1080:608:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
    cmd = [
        "ffmpeg", "-y", "-ss", str(start_t), "-t", str(dur),
        "-i", in_vid,
        "-filter_complex", filter_str,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        out_path
    ]
    run_cmd(cmd, f"Generating {out_name}")
    return out_path

def make_image_freeze_segment(img_path, dur, out_name, zoom_type="none", zoom_start=1.0, zoom_end=1.0):
    """Render a freeze frame image with optional smooth zoom (in or out)"""
    out_path = os.path.join(CLIPS_DIR, out_name)
    
    if zoom_type == "out":
        fg_scale = f"scale=eval=frame:w=trunc(1080*({zoom_start}-({zoom_start}-{zoom_end})*(t/{dur}))/2)*2:h=trunc(608*({zoom_start}-({zoom_start}-{zoom_end})*(t/{dur}))/2)*2"
    elif zoom_type == "in":
        fg_scale = f"scale=eval=frame:w=trunc(1080*({zoom_start}+({zoom_end}-{zoom_start})*(t/{dur}))/2)*2:h=trunc(608*({zoom_start}+({zoom_end}-{zoom_start})*(t/{dur}))/2)*2"
    else:
        fg_scale = "scale=1080:608:force_original_aspect_ratio=decrease"

    filter_str = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];"
        f"[0:v]{fg_scale}[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1",
        "-i", img_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", filter_str,
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        out_path
    ]
    run_cmd(cmd, f"Generating freeze segment {out_name} (zoom={zoom_type})")
    return out_path

def concat_clips(clip_list, out_name):
    out_path = os.path.join(CLIPS_DIR, out_name)
    list_file = os.path.join(CLIPS_DIR, f"concat_{out_name}.txt")
    with open(list_file, "w") as f:
        for c in clip_list:
            f.write(f"file '{c}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        out_path
    ]
    run_cmd(cmd, f"Concatenating into {out_name}")
    return out_path

def build_fast_scenes():
    print("=== BUILDING FAST MARVEL DECODED (31.96s) ===")
    
    freeze_ul_pull = os.path.join(CLIPS_DIR, "freeze_ul_pull.jpg")
    freeze_ul_shock = os.path.join(CLIPS_DIR, "freeze_ul_shock.jpg")
    freeze_ul_relieved = os.path.join(CLIPS_DIR, "freeze_ul_relieved.jpg")
    freeze_eg_catch = os.path.join(CLIPS_DIR, "freeze_eg_catch.jpg")
    freeze_eg_hero = os.path.join(CLIPS_DIR, "freeze_eg_hero.jpg")

    scenes = []

    # SCENE 1 (4.70s): Steve pulls Mjolnir (3.2s normal + 1.5s freeze with subtle zoom-in)
    p1a = make_video_segment(ULTRON_VID, 18.5, 3.2, "fast_s1_a.mp4")
    p1b = make_image_freeze_segment(freeze_ul_pull, 1.5, "fast_s1_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.15)
    s1 = concat_clips([p1a, p1b], "fast_scene_01.mp4")
    scenes.append(s1)

    # SCENE 2 (3.50s): Mjolnir flies & Cap catches (1.7s motion + 1.8s FREEZE & DYNAMIC ZOOM-OUT 1.5x -> 1.0x)
    p2a = make_video_segment(ENDGAME_VID, 10.0, 1.7, "fast_s2_a.mp4")
    p2b = make_image_freeze_segment(freeze_eg_catch, 1.8, "fast_s2_b.mp4", zoom_type="out", zoom_start=1.5, zoom_end=1.0)
    s2 = concat_clips([p2a, p2b], "fast_scene_02.mp4")
    scenes.append(s2)

    # SCENE 3 (5.10s): Thor "I knew it!" (2.8s) + Party table reaction (2.3s)
    p3a = make_video_segment(ENDGAME_VID, 16.5, 2.8, "fast_s3_a.mp4")
    p3b = make_video_segment(ULTRON_VID, 5.0, 2.3, "fast_s3_b.mp4")
    s3 = concat_clips([p3a, p3b], "fast_scene_03.mp4")
    scenes.append(s3)

    # SCENE 4 (3.80s): Mjolnir clink (1.0s) + Thor alarmed face FREEZE & DRAMATIC ZOOM-IN 1.0x -> 1.35x (2.8s)
    p4a = make_video_segment(ULTRON_VID, 20.5, 1.0, "fast_s4_a.mp4")
    p4b = make_image_freeze_segment(freeze_ul_shock, 2.8, "fast_s4_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.35)
    s4 = concat_clips([p4a, p4b], "fast_scene_04.mp4")
    scenes.append(s4)

    # SCENE 5 (5.40s): Steve realizing stakes & letting go (4.1s) + PAUSE on Thor relieved laugh (1.3s)
    p5a = make_video_segment(ULTRON_VID, 23.5, 4.1, "fast_s5_a.mp4")
    p5b = make_image_freeze_segment(freeze_ul_relieved, 1.3, "fast_s5_b.mp4")
    s5 = concat_clips([p5a, p5b], "fast_scene_05.mp4")
    scenes.append(s5)

    # SCENE 6 (4.50s): Endgame stakes (2.2s Thanos blade + 2.3s Cap charging & smashing Thanos)
    p6a = make_video_segment(ENDGAME_VID, 7.0, 2.2, "fast_s6_a.mp4")
    p6b = make_video_segment(ENDGAME_VID, 24.0, 2.3, "fast_s6_b.mp4")
    s6 = concat_clips([p6a, p6b], "fast_scene_06.mp4")
    scenes.append(s6)

    # SCENE 7 (4.96s): Lightning strike (3.0s) + FINAL HEROIC FREEZE & FADE OUT (1.96s)
    p7a = make_video_segment(ENDGAME_VID, 32.5, 3.0, "fast_s7_a.mp4")
    p7b = make_image_freeze_segment(freeze_eg_hero, 1.96, "fast_s7_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.10)
    s7 = concat_clips([p7a, p7b], "fast_scene_07.mp4")
    scenes.append(s7)

    raw_stitched = concat_clips(scenes, "fast_stitched_scenes.mp4")
    return raw_stitched

def render_fast_master(raw_stitched):
    print("\n=== RENDERING FINAL FAST MASTER WITH AUDIO & SUBTITLES ===")
    filter_complex = (
        "[1:a]volume=1.0[v_aud];"
        "[0:a]volume=0.22[m_aud];"
        "[v_aud][m_aud]amix=inputs=2:duration=first:dropout_transition=2[a_out];"
        f"[0:v]subtitles='{ASS_SUBTITLES}'[v_out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", raw_stitched,
        "-i", VOICEOVER_WAV,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        FINAL_MP4
    ]
    run_cmd(cmd, "Rendering Fast Master Video")
    print(f"\n🎉 FAST MASTER VIDEO COMPLETE: {FINAL_MP4}")

if __name__ == "__main__":
    stitched = build_fast_scenes()
    render_fast_master(stitched)
