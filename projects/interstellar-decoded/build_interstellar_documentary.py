import os
import subprocess
import json

BASE_DIR = "/Users/vinaybt/Downloads/interstellar-decoded"
RAW_DIR = os.path.join(BASE_DIR, "raw_video")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
SCRIPT_DIR = os.path.join(BASE_DIR, "script")
OUT_DIR = os.path.join(BASE_DIR, "out")

THEME_MUSIC = os.path.join(AUDIO_DIR, "interstellar_theme.mp3")
MASTER_MP4 = os.path.join(OUT_DIR, "interstellar_scientific_concepts_explained.mp4")

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

def run_cmd(cmd, desc=""):
    print(f"\n>>> {desc} <<<")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in {desc}:")
        print(res.stderr[-1000:])
        raise RuntimeError(f"FFmpeg failed: {res.stderr[-500:]}")
    return res

def render_subclip(in_vid, start_t, dur, out_name):
    """Normalize raw video cuts to 1920x1080 @ 30fps with stereo audio"""
    out_path = os.path.join(CLIPS_DIR, out_name)
    filter_str = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1"
    cmd = [
        "ffmpeg", "-y", "-ss", str(start_t), "-t", str(dur),
        "-i", in_vid,
        "-vf", filter_str,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        out_path
    ]
    run_cmd(cmd, f"Rendering Subclip {out_name}")
    return out_path

def concat_video_tracks(clip_paths, out_name):
    """Concat video cuts into chapter visual track"""
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
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-ar", "44100", "-ac", "2",
        out_path
    ]
    run_cmd(cmd, f"Concatenating {out_name}")
    return out_path

def build_chapter(cid, raw_cuts, voice_wav, ass_sub, music_offset, target_dur):
    """Assemble a complete chapter with visuals, 3-layer mixed audio, and title/subtitles"""
    chapter_mp4 = os.path.join(CLIPS_DIR, f"{cid}_chapter.mp4")
    
    # 1. Render all subclips
    subclips = []
    for idx, (raw_file, s_t, dur) in enumerate(raw_cuts, 1):
        sc = render_subclip(raw_file, s_t, dur, f"{cid}_cut_{idx}.mp4")
        subclips.append(sc)
    
    # 2. Concat subclips
    stitched_visual = concat_video_tracks(subclips, f"{cid}_stitched.mp4")
    
    # 3. Master render chapter with audio mix & ASS subtitles
    # Inputs:
    # 0: stitched_visual (contains movie ambient sound)
    # 1: voice_wav (Achird narration)
    # 2: THEME_MUSIC (Hans Zimmer score)
    filter_complex = (
        f"[1:a]volume=1.0,apad=whole_dur={target_dur}[voice];"
        f"[2:a]atrim=start={music_offset}:duration={target_dur},volume=0.18,afade=t=in:st=0:d=1.5,afade=t=out:st={target_dur-1.5}:d=1.5[theme];"
        f"[0:a]volume=0.15[movie_sfx];"
        f"[voice][theme][movie_sfx]amix=inputs=3:duration=first:dropout_transition=2[a_out];"
        f"[0:v]subtitles='{ass_sub}'[v_out]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", stitched_visual,
        "-i", voice_wav,
        "-i", THEME_MUSIC,
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(target_dur),
        chapter_mp4
    ]
    run_cmd(cmd, f"Rendering Master Chapter: {cid}")
    return chapter_mp4

def assemble_documentary():
    print("==================================================")
    print("🎬 BUILDING FULL INTERSTELLAR VIDEO ESSAY (16:9)")
    print("==================================================")
    
    wormhole_vid = os.path.join(RAW_DIR, "wormhole.mp4")
    millers_vid = os.path.join(RAW_DIR, "millers_planet.mp4")
    gargantua_vid = os.path.join(RAW_DIR, "gargantua.mp4")
    tesseract_vid = os.path.join(RAW_DIR, "tesseract.mp4")
    eureka_vid = os.path.join(RAW_DIR, "eureka.mp4")

    # Load chapter durations
    with open(os.path.join(SCRIPT_DIR, "chapter_durations.json")) as f:
        durations = json.load(f)

    chapters_to_render = [
        # Chapter 0: Prologue (38.76s)
        (
            "ch00_prologue",
            [
                (wormhole_vid, 5.0, 12.0),
                (wormhole_vid, 22.0, 13.0),
                (wormhole_vid, 45.0, durations["00_prologue"] - 25.0)
            ],
            os.path.join(AUDIO_DIR, "00_prologue_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_00.ass"),
            0.0,
            durations["00_prologue"]
        ),
        # Chapter 1: Wormhole (50.40s)
        (
            "ch01_wormhole",
            [
                (wormhole_vid, 18.0, 15.0),
                (wormhole_vid, 35.0, 17.0),
                (wormhole_vid, 55.0, durations["01_wormhole"] - 32.0)
            ],
            os.path.join(AUDIO_DIR, "01_wormhole_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_01.ass"),
            35.0,
            durations["01_wormhole"]
        ),
        # Chapter 2: Miller's Planet (66.52s)
        (
            "ch02_millers",
            [
                (millers_vid, 5.0, 15.0),
                (millers_vid, 25.0, 17.0),
                (millers_vid, 48.0, 16.0),
                (millers_vid, 75.0, durations["02_millers_planet"] - 48.0)
            ],
            os.path.join(AUDIO_DIR, "02_millers_planet_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_02.ass"),
            80.0,
            durations["02_millers_planet"]
        ),
        # Chapter 3: Gargantua (55.08s)
        (
            "ch03_gargantua",
            [
                (gargantua_vid, 10.0, 16.0),
                (gargantua_vid, 35.0, 20.0),
                (gargantua_vid, 60.0, durations["03_gargantua"] - 36.0)
            ],
            os.path.join(AUDIO_DIR, "03_gargantua_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_03.ass"),
            140.0,
            durations["03_gargantua"]
        ),
        # Chapter 4: Tesseract (39.44s)
        (
            "ch04_tesseract",
            [
                (tesseract_vid, 5.0, 12.0),
                (tesseract_vid, 22.0, 14.0),
                (tesseract_vid, 45.0, durations["04_tesseract"] - 26.0)
            ],
            os.path.join(AUDIO_DIR, "04_tesseract_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_04.ass"),
            190.0,
            durations["04_tesseract"]
        ),
        # Chapter 5: Quantum Gravity (51.44s)
        (
            "ch05_quantum",
            [
                (eureka_vid, 10.0, 16.0),
                (eureka_vid, 30.0, 16.0),
                (eureka_vid, 50.0, durations["05_quantum_gravity"] - 32.0)
            ],
            os.path.join(AUDIO_DIR, "05_quantum_gravity_achird.wav"),
            os.path.join(SCRIPT_DIR, "chapter_05.ass"),
            225.0,
            durations["05_quantum_gravity"]
        )
    ]

    rendered_chapters = []
    for cid, cuts, voice, sub, m_off, dur in chapters_to_render:
        chap_mp4 = build_chapter(cid, cuts, voice, sub, m_off, dur)
        rendered_chapters.append(chap_mp4)

    # 4. Final Master Concatenation of all 6 chapters
    print("\n=== CONCATENATING ALL 6 CHAPTERS INTO FULL MASTER MOVIE ===")
    inputs = []
    filter_inputs = ""
    for idx, cp in enumerate(rendered_chapters):
        inputs.extend(["-i", cp])
        filter_inputs += f"[{idx}:v][{idx}:a]"
    
    filter_complex = f"{filter_inputs}concat=n={len(rendered_chapters)}:v=1:a=1[v][a]"
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        MASTER_MP4
    ]
    run_cmd(cmd, "Generating Master Interstellar Documentary")
    print(f"\n🎉 COMPLETE INTERSTELLAR VIDEO ESSAY FINISHED: {MASTER_MP4}")

if __name__ == "__main__":
    assemble_documentary()
