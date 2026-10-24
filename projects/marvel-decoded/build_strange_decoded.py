import os
import subprocess

PROJECT_DIR = "/Users/vinaybt/Downloads/marvel-decoded"
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
RAW_DIR = os.path.join(PROJECT_DIR, "raw_video")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
SCRIPT_DIR = os.path.join(PROJECT_DIR, "script")

FUTURES_VID = os.path.join(RAW_DIR, "strange_futures.mp4")
TIMESTONE_VID = os.path.join(RAW_DIR, "strange_time_stone.mp4")
ENDGAME_VID = os.path.join(RAW_DIR, "strange_endgame_finger.mp4")

VOICEOVER_WAV = os.path.join(AUDIO_DIR, "strange_voiceover.wav")
ASS_SUBTITLES = os.path.join(SCRIPT_DIR, "strange_fast.ass")

FINAL_MP4 = os.path.join(OUT_DIR, "strange_decoded_final.mp4")

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
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];"
        f"[0:v]{fg_scale}[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(dur),
        "-i", img_path,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", filter_str,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac",
        "-shortest",
        out_path
    ]
    run_cmd(cmd, f"Generating Freeze {out_name}")
    return out_path

def concat_clips(clip_paths, out_name):
    """Concatenate video clips using FFmpeg concat filter"""
    out_path = os.path.join(CLIPS_DIR, out_name)
    inputs = []
    filter_inputs = ""
    for idx, cp in enumerate(clip_paths):
        inputs.extend(["-i", cp])
        filter_inputs += f"[{idx}:v][{idx}:a]"
    
    filter_complex = f"{filter_inputs}concat=n={len(clip_paths)}:v=1:a=1[v][a]"
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        out_path
    ]
    run_cmd(cmd, f"Concatenating into {out_name}")
    return out_path

def build_strange_scenes():
    print("=== BUILDING DOCTOR STRANGE 14M FUTURES SCENES ===")
    scenes = []

    freeze_futures = os.path.join(CLIPS_DIR, "freeze_st_futures.jpg")
    freeze_face = os.path.join(CLIPS_DIR, "freeze_st_face.jpg")
    freeze_stone = os.path.join(CLIPS_DIR, "freeze_st_stone.jpg")
    freeze_calc = os.path.join(CLIPS_DIR, "freeze_st_calculating.jpg")
    freeze_thanos = os.path.join(CLIPS_DIR, "freeze_st_thanos.jpg")
    freeze_tony = os.path.join(CLIPS_DIR, "freeze_st_tony.jpg")
    freeze_hand = os.path.join(CLIPS_DIR, "freeze_st_hand.jpg")
    freeze_finger = os.path.join(CLIPS_DIR, "freeze_st_finger.jpg")

    # SCENE 1 (3.35s): Doctor Strange viewed 14,000,605 futures (1.85s motion + 1.50s freeze zoom-in)
    p1a = make_video_segment(FUTURES_VID, 15.0, 1.85, "st_s1_a.mp4")
    p1b = make_image_freeze_segment(freeze_futures, 1.50, "st_s1_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.25)
    s1 = concat_clips([p1a, p1b], "st_scene_01.mp4")
    scenes.append(s1)

    # SCENE 2 (2.60s): ...and saw only ONE where they won (1.20s motion + 1.40s freeze zoom-in)
    p2a = make_video_segment(FUTURES_VID, 1.0, 1.20, "st_s2_a.mp4")
    p2b = make_image_freeze_segment(freeze_face, 1.40, "st_s2_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.15)
    s2 = concat_clips([p2a, p2b], "st_scene_02.mp4")
    scenes.append(s2)

    # SCENE 3 (4.25s): Handed Thanos the most dangerous weapon (2.15s motion + 2.10s freeze zoom-out)
    p3a = make_video_segment(TIMESTONE_VID, 32.5, 2.15, "st_s3_a.mp4")
    p3b = make_image_freeze_segment(freeze_stone, 2.10, "st_s3_b.mp4", zoom_type="out", zoom_start=1.40, zoom_end=1.0)
    s3 = concat_clips([p3a, p3b], "st_scene_03.mp4")
    scenes.append(s3)

    # SCENE 4 (4.00s): Why surrender? Backward Induction (1.80s motion + 2.20s freeze zoom-in)
    p4a = make_video_segment(TIMESTONE_VID, 51.0, 1.80, "st_s4_a.mp4")
    p4b = make_image_freeze_segment(freeze_calc, 2.20, "st_s4_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.22)
    s4 = concat_clips([p4a, p4b], "st_scene_04.mp4")
    scenes.append(s4)

    # SCENE 5 (4.70s): Thanos was mathematically unstoppable on Titan (2.30s motion + 2.40s freeze zoom-out)
    p5a = make_video_segment(TIMESTONE_VID, 20.0, 2.30, "st_s5_a.mp4")
    p5b = make_image_freeze_segment(freeze_thanos, 2.40, "st_s5_b.mp4", zoom_type="out", zoom_start=1.35, zoom_end=1.0)
    s5 = concat_clips([p5a, p5b], "st_scene_05.mp4")
    scenes.append(s5)

    # SCENE 6 (4.15s): Tony Stark was only mind capable of time travel (2.05s motion + 2.10s freeze zoom-in)
    p6a = make_video_segment(TIMESTONE_VID, 13.5, 2.05, "st_s6_a.mp4")
    p6b = make_image_freeze_segment(freeze_tony, 2.10, "st_s6_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.22)
    s6 = concat_clips([p6a, p6b], "st_scene_06.mp4")
    scenes.append(s6)

    # SCENE 7 (4.20s): Surrendering wasn't defeat, it was an investment (2.10s motion + 2.10s freeze zoom-out)
    p7a = make_video_segment(TIMESTONE_VID, 55.0, 2.10, "st_s7_a.mp4")
    p7b = make_image_freeze_segment(freeze_hand, 2.10, "st_s7_b.mp4", zoom_type="out", zoom_start=1.30, zoom_end=1.0)
    s7 = concat_clips([p7a, p7b], "st_scene_07.mp4")
    scenes.append(s7)

    # SCENE 8 (3.59s): Initiated the Endgame - Strange raising ONE finger (1.60s motion + 1.99s freeze zoom-in)
    p8a = make_video_segment(ENDGAME_VID, 7.5, 1.60, "st_s8_a.mp4")
    p8b = make_image_freeze_segment(freeze_finger, 1.99, "st_s8_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.30)
    s8 = concat_clips([p8a, p8b], "st_scene_08.mp4")
    scenes.append(s8)

    raw_stitched = concat_clips(scenes, "st_stitched_scenes.mp4")
    return raw_stitched

def render_master(raw_stitched):
    print("\n=== RENDERING FINAL STRANGE MASTER WITH AUDIO & SUBTITLES ===")
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
    run_cmd(cmd, "Rendering Strange Master Video")
    print(f"\n🎉 STRANGE DECODED MASTER VIDEO COMPLETE: {FINAL_MP4}")

if __name__ == "__main__":
    stitched = build_strange_scenes()
    render_master(stitched)
