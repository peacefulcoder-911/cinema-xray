import os
import subprocess

PROJECT_DIR = "/Users/vinaybt/Downloads/marvel-decoded"
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
RAW_DIR = os.path.join(PROJECT_DIR, "raw_video")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
SCRIPT_DIR = os.path.join(PROJECT_DIR, "script")

ELEVATOR_VID = os.path.join(RAW_DIR, "elevator_scene.mp4")
ENDING_VID = os.path.join(RAW_DIR, "elevator_ending.mp4")
VOICEOVER_WAV = os.path.join(AUDIO_DIR, "elevator_voiceover.wav")
ASS_SUBTITLES = os.path.join(SCRIPT_DIR, "elevator_fast.ass")

FINAL_MP4 = os.path.join(OUT_DIR, "elevator_decoded_final.mp4")

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

def build_elevator_scenes():
    print("=== BUILDING ELEVATOR DECODED FAST SCENES (30.80s) ===")

    freeze_step = os.path.join(CLIPS_DIR, "freeze_el_step.jpg")
    freeze_look = os.path.join(CLIPS_DIR, "freeze_el_look.jpg")
    freeze_line = os.path.join(CLIPS_DIR, "freeze_el_line.jpg")
    freeze_sweat = os.path.join(CLIPS_DIR, "freeze_el_sweat.jpg")
    freeze_hesitate = os.path.join(CLIPS_DIR, "freeze_el_hesitate.jpg")
    freeze_cuff = os.path.join(CLIPS_DIR, "freeze_el_cuff.jpg")
    freeze_hero = os.path.join(CLIPS_DIR, "freeze_el_hero.jpg")

    scenes = []

    # SCENE 1 (3.40s): Steve steps into elevator surrounded (2.2s motion + 1.2s freeze with zoom-in)
    p1a = make_video_segment(ELEVATOR_VID, 20.0, 2.2, "el_s1_a.mp4")
    p1b = make_image_freeze_segment(freeze_step, 1.2, "el_s1_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.12)
    s1 = concat_clips([p1a, p1b], "el_scene_01.mp4")
    scenes.append(s1)

    # SCENE 2 (2.80s): Steve looking around calmly (1.6s motion + 1.2s freeze with subtle zoom-in)
    p2a = make_video_segment(ELEVATOR_VID, 41.5, 1.6, "el_s2_a.mp4")
    p2b = make_image_freeze_segment(freeze_look, 1.2, "el_s2_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.15)
    s2 = concat_clips([p2a, p2b], "el_scene_02.mp4")
    scenes.append(s2)

    # SCENE 3 (2.80s): "Does anyone want to get out?" (1.4s Steve speaking + 1.4s DRAMATIC FREEZE & ZOOM-IN 1.0x -> 1.30x)
    p3a = make_video_segment(ELEVATOR_VID, 63.0, 1.4, "el_s3_a.mp4")
    p3b = make_image_freeze_segment(freeze_line, 1.4, "el_s3_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.30)
    s3 = concat_clips([p3a, p3b], "el_scene_03.mp4")
    scenes.append(s3)

    # SCENE 4 (4.80s): Resetting OODA loop (2.4s wide elevator + 2.4s FREEZE & DYNAMIC ZOOM-OUT 1.45x -> 1.0x)
    p4a = make_video_segment(ELEVATOR_VID, 60.0, 2.4, "el_s4_a.mp4")
    p4b = make_image_freeze_segment(freeze_step, 2.4, "el_s4_b.mp4", zoom_type="out", zoom_start=1.45, zoom_end=1.0)
    s4 = concat_clips([p4a, p4b], "el_scene_04.mp4")
    scenes.append(s4)

    # SCENE 5 (5.20s): Micro-tells (1.8s sweating neck freeze zoom + 1.6s baton drawn + 1.8s Steve glance)
    p5a = make_image_freeze_segment(freeze_sweat, 1.8, "el_s5_a.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.12)
    p5b = make_video_segment(ELEVATOR_VID, 67.5, 1.6, "el_s5_b.mp4")
    p5c = make_video_segment(ELEVATOR_VID, 35.0, 1.8, "el_s5_c.mp4")
    s5 = concat_clips([p5a, p5b, p5c], "el_scene_05.mp4")
    scenes.append(s5)

    # SCENE 6 (4.00s): Cognitive Hesitation (2.0s agents looking + 2.0s FREEZE on Rumlow & ZOOM-OUT 1.35x -> 1.0x)
    p6a = make_video_segment(ELEVATOR_VID, 65.5, 2.0, "el_s6_a.mp4")
    p6b = make_image_freeze_segment(freeze_hesitate, 2.0, "el_s6_b.mp4", zoom_type="out", zoom_start=1.35, zoom_end=1.0)
    s6 = concat_clips([p6a, p6b], "el_scene_06.mp4")
    scenes.append(s6)

    # SCENE 7 (3.20s): Ambush & Magnetic Cuffs (1.6s motion + 1.6s FREEZE & ZOOM-IN on cuff clamp 1.0x -> 1.25x)
    p7a = make_video_segment(ELEVATOR_VID, 72.0, 1.6, "el_s7_a.mp4")
    p7b = make_image_freeze_segment(freeze_cuff, 1.6, "el_s7_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.25)
    s7 = concat_clips([p7a, p7b], "el_scene_07.mp4")
    scenes.append(s7)

    # SCENE 8 (4.60s): Climax & Shield (1.8s Steve throws Rumlow + 1.4s shield kick + 1.4s FINAL HEROIC FREEZE)
    p8a = make_video_segment(ENDING_VID, 24.5, 1.8, "el_s8_a.mp4")
    p8b = make_video_segment(ENDING_VID, 36.5, 1.4, "el_s8_b.mp4")
    p8c = make_image_freeze_segment(freeze_hero, 1.4, "el_s8_c.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.10)
    s8 = concat_clips([p8a, p8b, p8c], "el_scene_08.mp4")
    scenes.append(s8)

    raw_stitched = concat_clips(scenes, "el_stitched_scenes.mp4")
    return raw_stitched

def render_master(raw_stitched):
    print("\n=== RENDERING FINAL ELEVATOR MASTER WITH AUDIO & SUBTITLES ===")
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
    run_cmd(cmd, "Rendering Elevator Master Video")
    print(f"\n🎉 ELEVATOR DECODED VIDEO COMPLETE: {FINAL_MP4}")

if __name__ == "__main__":
    stitched = build_elevator_scenes()
    render_master(stitched)
