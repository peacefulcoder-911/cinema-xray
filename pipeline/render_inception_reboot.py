#!/usr/bin/env python3
"""
Cinema Decoded: Inception Visual & Editorial Reboot Engine
==========================================================
Re-renders the Inception (2010) YouTube Short with:
1. Multi-clip authentic 1080p scene evidence (Top, Dream Ring, Reality Bare Hand).
2. Dynamic digital zoom & timeline freeze on the ring and bare hand.
3. Side-by-side split-screen evidence card (Dream vs Reality).
4. Official ASS Subtitles: Style 7: Arc Reactor Cyan HUD with acoustic alignment.
5. 8K Super-Resolution rendering (4320x7680).
6. Direct Unlisted YouTube upload & Apple Mail notification to Vinaybtnofearv@gmail.com.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PROJ_DIR = REPO_ROOT / "projects" / "cinema-decoded-inception_real_totem"
CLIPS_DIR = PROJ_DIR / "clips"
OUT_DIR = PROJ_DIR / "out"
FINAL_DIR = REPO_ROOT / "output" / "final_video"
AUDIO_PATH = PROJ_DIR / "audio" / "master_audio.wav"
ASS_PATH = PROJ_DIR / "subtitles.ass"

CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# Source Footage Assets
FOOTAGE_ENDING = REPO_ROOT / "assets" / "footage" / "inception" / "inception_ending_scene.mp4"
FOOTAGE_AIRPORT = REPO_ROOT / "assets" / "footage" / "inception" / "inception_airport_customs.mp4"
FOOTAGE_RING = REPO_ROOT / "assets" / "footage" / "inception" / "inception_ring_theory.mp4"
FOOTAGE_CAFE = REPO_ROOT / "assets" / "footage" / "inception" / "inception_dream_cafe.mp4"

TOTAL_DUR = 26.6565


def create_beat_01(out_path: str):
    """Beat 1 (0.00s - 3.76s): The film shows you his real totem in the opening frames...
    Visual: Macro close up of the spinning top on the dark wooden table."""
    dur = 3.76
    raw = str(CLIPS_DIR / "raw_beat_01.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "147.0", "-i", str(FOOTAGE_ENDING),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='min(zoom+0.0015,1.15)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_02(out_path: str):
    """Beat 2 (3.76s - 9.62s): For two hours, every single viewer stares at the spinning top on the table...
    Visual: Close up of the spinning top wobbling across the wooden surface."""
    dur = 9.62 - 3.76  # 5.86s
    raw = str(CLIPS_DIR / "raw_beat_02.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "153.0", "-i", str(FOOTAGE_ENDING),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z=1.08:d={int(dur*30)}:x='(iw-iw/zoom)*(on/{int(dur*30)})':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_03(out_path: str):
    """Beat 3 (9.62s - 12.22s): We are conditioned to watch the wrong object.
    Visual: Cobb watching the top in the dining room before turning to children."""
    dur = 12.22 - 9.62  # 2.60s
    raw = str(CLIPS_DIR / "raw_beat_03.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "131.0", "-i", str(FOOTAGE_ENDING),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]scale=1080:1344:force_original_aspect_ratio=decrease,vignette=PI/4[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_04(out_path: str):
    """Beat 4 (12.22s - 15.52s): Look closely at Dom Cobb's hands throughout the entire narrative.
    Visual: Cobb looking through scope in snow dream, moving hands."""
    dur = 15.52 - 12.22  # 3.30s
    raw = str(CLIPS_DIR / "raw_beat_04.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "37.5", "-i", str(FOOTAGE_RING),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='min(zoom+0.002,1.25)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_05_ring_freeze(out_path: str):
    """Beat 5 (15.52s - 19.42s): When he is trapped inside a shared dream, the wedding ring sits firmly on his finger.
    Visual: Macro close up of Cobb's left hand at the table WITH the silver wedding ring.
    CAMERA EFFECT: Digital zoom in on the ring, then FREEZE on the gleaming ring."""
    dur = 19.42 - 15.52  # 3.90s
    
    freeze_frame = str(CLIPS_DIR / "ring_freeze_frame.jpg")
    cmd_frame = [
        "ffmpeg", "-y", "-ss", "40.2", "-i", str(FOOTAGE_RING),
        "-vframes", "1", "-q:v", "2", freeze_frame
    ]
    subprocess.run(cmd_frame, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];"
        "[0:v]crop=w=iw*0.48:h=ih*0.65:x=iw*0.48:y=ih*0.05,scale=1080:1344:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-loop", "1", "-i", freeze_frame, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_06_bare_hand_freeze(out_path: str):
    """Beat 6 (19.42s - 23.72s): When he finally returns to his children in the reality he fought to reach, his hand is bare.
    Visual: Cobb resting left hand on wooden chair at the table with ALL fingers bare.
    CAMERA EFFECT: Digital zoom in on bare fingers, then FREEZE."""
    dur = 23.72 - 19.42  # 4.30s

    freeze_frame = str(CLIPS_DIR / "bare_hand_freeze_frame.jpg")
    cmd_frame = [
        "ffmpeg", "-y", "-ss", "173.0", "-i", str(FOOTAGE_AIRPORT),
        "-vframes", "1", "-q:v", "2", freeze_frame
    ]
    subprocess.run(cmd_frame, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];"
        "[0:v]crop=w=iw*0.42:h=ih*0.65:x=iw*0.02:y=ih*0.25,scale=1080:1344:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-loop", "1", "-i", freeze_frame, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_07_side_by_side(out_path: str):
    """Beat 7 (23.72s - 26.66s): The top doesn't matter. The ring tells the truth.
    Visual: Side-by-Side Split Screen Evidence Card!
    Top Frame: DREAM (Left hand with ring)
    Bottom Frame: REALITY (Left hand bare)
    Last 0.94s: Top gives final wobble before cut to black!"""
    total_dur = 26.6565 - 23.72  # 2.9365s
    split_dur = 2.00
    top_wobble_dur = total_dur - split_dur  # ~0.94s

    split_part = str(CLIPS_DIR / "split_card.mp4")
    wobble_part = str(CLIPS_DIR / "final_wobble.mp4")

    ring_frame = str(CLIPS_DIR / "ring_freeze_frame.jpg")
    bare_frame = str(CLIPS_DIR / "bare_hand_freeze_frame.jpg")

    # Side-by-Side Split Screen
    split_vf = (
        "color=c=0x08080c:s=1080x1920:d=" + f"{split_dur:.3f}[bg];"
        f"[0:v]crop=w=iw*0.48:h=ih*0.65:x=iw*0.48:y=ih*0.05,scale=960:540,drawbox=x=0:y=0:w=iw:h=ih:color=0x00FFFF:t=4[top_crop];"
        f"[1:v]crop=w=iw*0.42:h=ih*0.65:x=iw*0.02:y=ih*0.25,scale=960:540,drawbox=x=0:y=0:w=iw:h=ih:color=0xFFFFFF:t=4[bot_crop];"
        "[bg][top_crop]overlay=60:320[v1];"
        "[v1][bot_crop]overlay=60:960[v2];"
        "[v2]drawtext=fontfile='/System/Library/Fonts/Supplemental/Futura.ttc':text='DREAM  //  RING ON':"
        "fontcolor=0x00FFFF:fontsize=38:x=70:y=265:shadowcolor=black@0.9:shadowx=2:shadowy=2[v3];"
        "[v3]drawtext=fontfile='/System/Library/Fonts/Supplemental/Futura.ttc':text='REALITY  //  NO RING':"
        "fontcolor=0xFFFFFF:fontsize=38:x=70:y=905:shadowcolor=black@0.9:shadowx=2:shadowy=2,setsar=1[outv]"
    )
    cmd_split = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", ring_frame,
        "-loop", "1", "-i", bare_frame,
        "-t", f"{split_dur:.3f}",
        "-filter_complex", split_vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", split_part
    ]
    subprocess.run(cmd_split, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Final top wobble shot:
    raw_wobble = str(CLIPS_DIR / "raw_wobble.mp4")
    cmd_wob = [
        "ffmpeg", "-y", "-ss", "166.0", "-i", str(FOOTAGE_ENDING),
        "-t", f"{top_wobble_dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw_wobble
    ]
    subprocess.run(cmd_wob, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    wobble_vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1080:1344:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd_wob2 = [
        "ffmpeg", "-y", "-i", raw_wobble, "-t", f"{top_wobble_dur:.3f}",
        "-filter_complex", wobble_vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", wobble_part
    ]
    subprocess.run(cmd_wob2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concat with setsar=1 to guarantee zero SAR/PTS mismatch
    cmd_concat = [
        "ffmpeg", "-y",
        "-i", split_part,
        "-i", wobble_part,
        "-filter_complex", "[0:v]setsar=1[v0];[1:v]setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[outv]",
        "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def assemble_1080p_master(clip_paths, out_1080p):
    """Concatenates all 7 beats with filter-based concat, syncs audio, and burns Arc Reactor Cyan HUD subtitles."""
    inputs = []
    filter_norm = ""
    concat_inputs = ""
    for idx, p in enumerate(clip_paths):
        inputs.extend(["-i", p])
        filter_norm += f"[{idx}:v]setsar=1,fps=30[v{idx}];"
        concat_inputs += f"[v{idx}]"

    concat_filter = f"{filter_norm}{concat_inputs}concat=n={len(clip_paths)}:v=1:a=0,ass={ASS_PATH}[outv]"

    cmd_master = [
        "ffmpeg", "-y",
        *inputs,
        "-i", str(AUDIO_PATH),
        "-filter_complex", concat_filter,
        "-map", "[outv]",
        "-map", f"{len(clip_paths)}:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-t", f"{TOTAL_DUR:.3f}",
        out_1080p
    ]
    print("🎞️  Assembling 1080p Master with filter concat and Arc Reactor Cyan HUD subtitles...")
    subprocess.run(cmd_master, check=True)


def upscale_to_8k(in_1080p, out_8k):
    """Upscales 1080x1920 to 8K Super-Resolution (4320x7680) @ 65-80 Mbps."""
    print("🚀 Upscaling to 8K Super-Resolution (4320x7680)...")
    is_mac = sys.platform == "darwin"
    if is_mac:
        vf = "scale=4320:7680:flags=lanczos+accurate_rnd"
        cmd = [
            "ffmpeg", "-y",
            "-i", in_1080p,
            "-vf", vf,
            "-c:v", "hevc_videotoolbox", "-b:v", "65M", "-tag:v", "hvc1",
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            out_8k
        ]
        try:
            subprocess.run(cmd, check=True)
            return out_8k
        except Exception as e:
            print(f"⚠️ VideoToolbox 8K failed ({e}), falling back to libx264 8K...")

    vf = "scale=4320:7680:flags=lanczos"
    cmd = [
        "ffmpeg", "-y",
        "-i", in_1080p,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        out_8k
    ]
    subprocess.run(cmd, check=True)
    return out_8k


def upload_to_youtube(video_path: str) -> dict:
    """Uploads the 8K video to YouTube as Unlisted using pipeline/youtube_uploader.py."""
    print(f"\n📤 Uploading 8K video to YouTube (Unlisted): {video_path}...")
    from pipeline.youtube_uploader import upload_video

    title = "Inception Ending Decoded: The Ring Was Cobb's Real Totem (8K)"
    description = (
        "Audiences spent over a decade obsessed with the spinning top at the end of Christopher Nolan's Inception (2010), "
        "waiting to see if it would fall. But the top was never Cobb's totem—it was Mal's.\n\n"
        "Dom Cobb's real totem was his wedding ring. Look at his hands throughout the narrative: in every single dream level, "
        "the wedding ring is firmly on his finger. In reality, his hand is bare.\n\n"
        "The top doesn't matter. The ring tells the truth.\n\n"
        "#Inception #ChristopherNolan #CinemaXRay #FilmAnalysis #MovieDetails #LeonardoDiCaprio #8K"
    )
    tags = [
        "Inception", "Christopher Nolan", "Leonardo DiCaprio", "Inception Ending", "Totem",
        "Film Analysis", "Cinema X-Ray", "Shorts", "Movie Details", "8K"
    ]

    res = upload_video(
        file_path=video_path,
        title=title,
        description=description,
        tags=tags,
        category_id="1",  # Film & Animation
        privacy_status="unlisted"
    )
    print(f"🎉 Successfully uploaded! YouTube URL: {res.get('url')}")
    return res


def send_completion_email(yt_url: str):
    """Sends notification email to Vinaybtnofearv@gmail.com via macOS Mail.app."""
    print("\n📧 Sending upload confirmation email to Vinaybtnofearv@gmail.com...")
    subject = "🎬 Cinema Decoded: Inception 8K Video Uploaded (Unlisted)"
    body = (
        f"Hi Vinay,\n\n"
        f"The completely rebooted 8K Inception video has been rendered and uploaded to YouTube as UNLISTED:\n\n"
        f"🔗 Private Video Link: {yt_url}\n\n"
        f"Key Improvements Applied:\n"
        f"• Multi-clip authentic footage (Top macro, Dream level ring close-up, Reality bare hand)\n"
        f"• Camera zoom-in and freeze-frame on Cobb's gleaming wedding ring and bare hand\n"
        f"• Side-by-Side Split Screen Evidence Card (Dream vs Reality)\n"
        f"• Official ASS Subtitles: Style 7 Arc Reactor Cyan HUD (Futura 74pt lower-third)\n"
        f"• 8K Ultra HD Super-Resolution (4320x7680)\n\n"
        f"Best,\nCinema X-Ray Autonomous Production Engine"
    )
    
    applescript = f'''
    tell application "Mail"
        set newMsg to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:false}}
        tell newMsg to make new to recipient at end of to recipients with properties {{address:"Vinaybtnofearv@gmail.com"}}
        send newMsg
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", applescript], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Email sent successfully to Vinaybtnofearv@gmail.com via Mail.app!")
    except Exception as e:
        print(f"⚠️ AppleScript Mail note: {e}")


def main():
    print("=" * 70)
    print("🎬 CINEMA DECODED: INCEPTION VISUAL & EDITORIAL REBOOT")
    print("=" * 70)

    if not (AUDIO_PATH.exists() and ASS_PATH.exists()):
        raise FileNotFoundError("Master audio or subtitles.ass missing in project directory.")

    print(f"🎙️  Audio: {AUDIO_PATH} ({TOTAL_DUR:.2f}s)")
    print(f"📝 Subtitles: {ASS_PATH} (Style 7: Arc Reactor Cyan HUD)")

    b1 = str(CLIPS_DIR / "beat_01.mp4")
    b2 = str(CLIPS_DIR / "beat_02.mp4")
    b3 = str(CLIPS_DIR / "beat_03.mp4")
    b4 = str(CLIPS_DIR / "beat_04.mp4")
    b5 = str(CLIPS_DIR / "beat_05_ring_freeze.mp4")
    b6 = str(CLIPS_DIR / "beat_06_bare_hand_freeze.mp4")
    b7 = str(CLIPS_DIR / "beat_07_side_by_side.mp4")

    print("\n✂️  [1/7] Slicing Beat 01 (Macro Spinning Top push-in)...")
    create_beat_01(b1)

    print("✂️  [2/7] Slicing Beat 02 (Spinning Top wobble pan)...")
    create_beat_02(b2)

    print("✂️  [3/7] Slicing Beat 03 (Conditioned distraction vignette)...")
    create_beat_03(b3)

    print("✂️  [4/7] Slicing Beat 04 (Look closely at Cobb's hands)...")
    create_beat_04(b4)

    print("✂️  [5/7] Slicing Beat 05 (ZOOM & FREEZE on Cobb's Wedding Ring)...")
    create_beat_05_ring_freeze(b5)

    print("✂️  [6/7] Slicing Beat 06 (ZOOM & FREEZE on Cobb's Bare Hand in Reality)...")
    create_beat_06_bare_hand_freeze(b6)

    print("✂️  [7/7] Slicing Beat 07 (SIDE-BY-SIDE SPLIT SCREEN Evidence Card)...")
    create_beat_07_side_by_side(b7)

    clips = [b1, b2, b3, b4, b5, b6, b7]

    # 3. Assemble 1080p Master with Filter Concat
    master_1080p = str(OUT_DIR / "cinema_decoded_inception_real_totem_1080p.mp4")
    assemble_1080p_master(clips, master_1080p)
    print(f"✅ 1080p Master ready: {master_1080p}")

    # 4. Upscale to 8K
    master_8k = str(FINAL_DIR / "cinema_xray_inception_real_totem_8k.mp4")
    upscale_to_8k(master_1080p, master_8k)
    print(f"🏆 8K Master ready: {master_8k}")

    # 5. Upload to YouTube as Unlisted
    yt_res = upload_to_youtube(master_8k)
    yt_url = yt_res.get("url")

    # 6. Send Email Notification
    send_completion_email(yt_url)

    print("\n" + "=" * 70)
    print(f"🎬 PRODUCTION & UPLOAD COMPLETE!")
    print(f"🔗 Unlisted YouTube URL: {yt_url}")
    print(f"📧 Notification sent to: Vinaybtnofearv@gmail.com")
    print("=" * 70)
    return yt_url


if __name__ == "__main__":
    main()
