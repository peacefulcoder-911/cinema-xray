import os
import subprocess
import glob

PROJECT_DIR = "/Users/vinaybt/Downloads/marvel-decoded"
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
RAW_DIR = os.path.join(PROJECT_DIR, "raw_video")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
SCRIPT_DIR = os.path.join(PROJECT_DIR, "script")

ULTRON_VID = os.path.join(RAW_DIR, "ultron_hammer.mp4")
ENDGAME_VID = os.path.join(RAW_DIR, "endgame_mjolnir.mp4")
VOICEOVER_WAV = os.path.join(AUDIO_DIR, "voiceover.wav")
ASS_SUBTITLES = os.path.join(SCRIPT_DIR, "marvel_decoded.ass")

FINAL_MP4 = os.path.join(OUT_DIR, "marvel_decoded_final.mp4")

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
        # Smooth zoom out: zoom_start -> zoom_end
        fg_scale = f"scale=eval=frame:w=trunc(1080*({zoom_start}-({zoom_start}-{zoom_end})*(t/{dur}))/2)*2:h=trunc(608*({zoom_start}-({zoom_start}-{zoom_end})*(t/{dur}))/2)*2"
    elif zoom_type == "in":
        # Smooth zoom in: zoom_start -> zoom_end
        fg_scale = f"scale=eval=frame:w=trunc(1080*({zoom_start}+({zoom_end}-{zoom_start})*(t/{dur}))/2)*2:h=trunc(608*({zoom_start}+({zoom_end}-{zoom_start})*(t/{dur}))/2)*2"
    else:
        # Static freeze
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
    list_file = os.path.join(CLIPS_DIR, "concat_list.txt")
    with open(list_file, "w") as f:
        for c in clip_list:
            f.write(f"file '{c}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        out_path
    ]
    run_cmd(cmd, f"Concatenating {len(clip_list)} clips into {out_name}")
    return out_path

def build_all_scenes():
    print("=== BUILDING MARVEL DECODED SCENES ===")
    
    # Extract reference images for freeze frames
    freeze_ul_pull = os.path.join(CLIPS_DIR, "freeze_ul_pull.jpg")
    freeze_ul_shock = os.path.join(CLIPS_DIR, "freeze_ul_shock.jpg")
    freeze_ul_relieved = os.path.join(CLIPS_DIR, "freeze_ul_relieved.jpg")
    freeze_eg_catch = os.path.join(CLIPS_DIR, "freeze_eg_catch.jpg")
    freeze_eg_hero = os.path.join(CLIPS_DIR, "freeze_eg_hero.jpg")

    run_cmd(["ffmpeg", "-y", "-ss", "21.2", "-i", ULTRON_VID, "-frames:v", "1", "-q:v", "2", freeze_ul_pull], "Extracting freeze_ul_pull")
    run_cmd(["ffmpeg", "-y", "-ss", "23.8", "-i", ULTRON_VID, "-frames:v", "1", "-q:v", "2", freeze_ul_shock], "Extracting freeze_ul_shock")
    run_cmd(["ffmpeg", "-y", "-ss", "27.8", "-i", ULTRON_VID, "-frames:v", "1", "-q:v", "2", freeze_ul_relieved], "Extracting freeze_ul_relieved")
    run_cmd(["ffmpeg", "-y", "-ss", "14.8", "-i", ENDGAME_VID, "-frames:v", "1", "-q:v", "2", freeze_eg_catch], "Extracting freeze_eg_catch")
    run_cmd(["ffmpeg", "-y", "-ss", "36.5", "-i", ENDGAME_VID, "-frames:v", "1", "-q:v", "2", freeze_eg_hero], "Extracting freeze_eg_hero")

    scenes = []

    # SCENE 1 (5.50s): Steve pulls Mjolnir (3.7s normal + 1.8s freeze with subtle zoom-in)
    p1a = make_video_segment(ULTRON_VID, 18.0, 3.7, "s1_a.mp4")
    p1b = make_image_freeze_segment(freeze_ul_pull, 1.8, "s1_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.15)
    s1 = concat_clips([p1a, p1b], "scene_01.mp4")
    scenes.append(s1)

    # SCENE 2 (3.30s): Thor smug smile dropping
    s2 = make_video_segment(ULTRON_VID, 21.8, 3.3, "scene_02.mp4")
    scenes.append(s2)

    # SCENE 3 (3.40s): Endgame Thanos crushing Thor
    s3 = make_video_segment(ENDGAME_VID, 6.0, 3.4, "scene_03.mp4")
    scenes.append(s3)

    # SCENE 4 (4.30s): Mjolnir flies, Cap catches it (2.5s motion + 1.8s FREEZE & DYNAMIC ZOOM OUT 1.45x -> 1.0x)
    p4a = make_video_segment(ENDGAME_VID, 10.0, 2.5, "s4_a.mp4")
    p4b = make_image_freeze_segment(freeze_eg_catch, 1.8, "s4_b.mp4", zoom_type="out", zoom_start=1.45, zoom_end=1.0)
    s4 = concat_clips([p4a, p4b], "scene_04.mp4")
    scenes.append(s4)

    # SCENE 5 (4.50s): Thor "I knew it!" + Cap spinning hammer
    s5 = make_video_segment(ENDGAME_VID, 16.5, 4.5, "scene_05.mp4")
    scenes.append(s5)

    # SCENE 6 (8.50s): Status Preservation breakdown - Avengers watching at the table
    s6 = make_video_segment(ULTRON_VID, 5.0, 8.5, "scene_06.mp4")
    scenes.append(s6)

    # SCENE 7 (8.50s): Millisecond budge (2.5s table clink + 6.0s FREEZE on Thor with SLOW DRAMATIC ZOOM-IN 1.0x -> 1.35x)
    p7a = make_video_segment(ULTRON_VID, 20.0, 2.5, "s7_a.mp4")
    p7b = make_image_freeze_segment(freeze_ul_shock, 6.0, "s7_b.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.35)
    s7 = concat_clips([p7a, p7b], "scene_07.mp4")
    scenes.append(s7)

    # SCENE 8 (8.50s): Steve realizing the stakes, reading Thor's expression (4.5s) + room reaction (4.0s)
    p8a = make_video_segment(ULTRON_VID, 22.5, 4.5, "s8_a.mp4")
    p8b = make_video_segment(ULTRON_VID, 13.5, 4.0, "s8_b.mp4")
    s8 = concat_clips([p8a, p8b], "scene_08.mp4")
    scenes.append(s8)

    # SCENE 9 (3.50s): Steve lets go with smile (2.0s) + 1.5s PAUSE on Thor's relieved laugh
    p9a = make_video_segment(ULTRON_VID, 26.5, 2.0, "s9_a.mp4")
    p9b = make_image_freeze_segment(freeze_ul_relieved, 1.5, "s9_b.mp4")
    s9 = concat_clips([p9a, p9b], "scene_09.mp4")
    scenes.append(s9)

    # SCENE 10 (6.50s): Endgame - No ego left to protect (3.2s Thanos struggle + 3.3s Cap charging with hammer)
    p10a = make_video_segment(ENDGAME_VID, 7.0, 3.2, "s10_a.mp4")
    p10b = make_video_segment(ENDGAME_VID, 20.5, 3.3, "s10_b.mp4")
    s10 = concat_clips([p10a, p10b], "scene_10.mp4")
    scenes.append(s10)

    # SCENE 11 (12.54s): Combat & lightning climax (4.5s combat + 5.0s lightning strike + 3.04s final heroic freeze)
    p11a = make_video_segment(ENDGAME_VID, 24.0, 4.5, "s11_a.mp4")
    p11b = make_video_segment(ENDGAME_VID, 32.5, 5.0, "s11_b.mp4")
    p11c = make_image_freeze_segment(freeze_eg_hero, 3.04, "s11_c.mp4", zoom_type="in", zoom_start=1.0, zoom_end=1.12)
    s11 = concat_clips([p11a, p11b, p11c], "scene_11.mp4")
    scenes.append(s11)

    print(f"Total scenes generated: {len(scenes)}")

    # Concat all 11 scenes
    raw_stitched = concat_clips(scenes, "stitched_scenes.mp4")
    return raw_stitched

def render_final_master(raw_stitched):
    print("\n=== RENDERING FINAL MASTER WITH AUDIO & SUBTITLES ===")
    
    # 1. Mix Voiceover (1.0) + Original Movie Sounds (0.20)
    # 2. Burn in ASS subtitles with libass
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
    run_cmd(cmd, "Rendering Final Master Video")
    print(f"\n🎉 MASTER VIDEO COMPLETE: {FINAL_MP4}")

if __name__ == "__main__":
    stitched = build_all_scenes()
    render_final_master(stitched)
