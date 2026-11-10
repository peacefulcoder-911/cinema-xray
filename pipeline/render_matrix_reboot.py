#!/usr/bin/env python3
"""
Cinema Decoded: The Matrix Reloaded - Smith Replication Reboot Engine
=====================================================================
Assembles and renders the definitive 8K YouTube Short:
1. Multi-clip authentic 1080p source footage across 4 scene pillars.
2. Digital zoom-in into Smith's parasitic hand assimilation.
3. Freeze-frame on Smith's face when unhooked from the Source.
4. Side-by-side split screen evidence card (Original Enforcer vs Autonomous Virus).
5. Official ASS Subtitles: Style 7 Arc Reactor Cyan HUD with acoustic alignment.
6. 8K Super-Resolution rendering (4320x7680 @ 30 FPS).
7. Direct Unlisted YouTube upload & email notification to Vinaybtnofearv@gmail.com.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PROJ_DIR = REPO_ROOT / "projects" / "cinema-decoded-matrix_smith_replication_cancer"
CLIPS_DIR = PROJ_DIR / "clips"
RAW_DIR = PROJ_DIR / "raw_clips"
OUT_DIR = PROJ_DIR / "out"
FINAL_DIR = REPO_ROOT / "output" / "final_video"
AUDIO_PATH = PROJ_DIR / "audio" / "master_audio.wav"
ASS_PATH = PROJ_DIR / "subtitles.ass"

CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

FOOTAGE_ASSIM = RAW_DIR / "smith_assimilation.mp4"
FOOTAGE_BRAWL1 = RAW_DIR / "burly_brawl_part1.mp4"
FOOTAGE_BRAWL2 = RAW_DIR / "burly_brawl_part2.mp4"
FOOTAGE_ARCHITECT = RAW_DIR / "architect_room.mp4"
FOOTAGE_ENFORCER = REPO_ROOT / "assets" / "footage" / "matrix" / "cypher_steak" / "smith_conversation.mp4"

TOTAL_DUR = 38.8238


def create_beat_01(out_path: str):
    """Beat 1 (0.00s - 5.80s): Smith's parasitic identity theft
    Visual: Hand plunging into Bane's chest, liquid chrome spreading.
    CAMERA EFFECT: Digital zoom into the hand assimilation!"""
    dur = 5.80
    raw = str(CLIPS_DIR / "raw_beat_01.mp4")
    # Take from 22.0s in smith_assimilation
    cmd = [
        "ffmpeg", "-y", "-ss", "22.0", "-i", str(FOOTAGE_ASSIM),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='min(zoom+0.0018,1.25)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_02(out_path: str):
    """Beat 2 (5.80s - 13.00s): Look closely at the Burly Brawl. Every Agent in that courtyard...
    Visual: Scores of Smiths circling Neo in the courtyard in unison."""
    dur = 13.00 - 5.80  # 7.20s
    raw = str(CLIPS_DIR / "raw_beat_02.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "192.0", "-i", str(FOOTAGE_BRAWL1),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='min(zoom+0.0006,1.06)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_03_freeze(out_path: str):
    """Beat 3 (13.00s - 18.20s): When Neo shattered him in the first film, Smith didn't die—he was unhooked...
    Visual: Smith pushing forward, then FREEZE-FRAME on his face as the truth lands."""
    dur = 18.20 - 13.00  # 5.20s
    lead_dur = 2.50
    freeze_dur = dur - lead_dur  # 2.70s

    part_lead = str(CLIPS_DIR / "b3_lead.mp4")
    part_freeze = str(CLIPS_DIR / "b3_freeze.mp4")
    freeze_img = str(CLIPS_DIR / "smith_unhooked_face.jpg")

    # 1. Lead video
    raw_lead = str(CLIPS_DIR / "raw_b3_lead.mp4")
    cmd_lead = [
        "ffmpeg", "-y", "-ss", "33.0", "-i", str(FOOTAGE_BRAWL1),
        "-t", f"{lead_dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw_lead
    ]
    subprocess.run(cmd_lead, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf_lead = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1080:1344:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd_lead2 = [
        "ffmpeg", "-y", "-i", raw_lead, "-t", f"{lead_dur:.3f}",
        "-filter_complex", vf_lead, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", part_lead
    ]
    subprocess.run(cmd_lead2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Extract freeze frame at exact peak (35.5s)
    cmd_frame = [
        "ffmpeg", "-y", "-ss", "35.5", "-i", str(FOOTAGE_BRAWL1),
        "-vframes", "1", "-q:v", "2", freeze_img
    ]
    subprocess.run(cmd_frame, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Freeze frame with zoom into Smith's face
    vf_freeze = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];"
        "[0:v]crop=w=iw*0.48:h=ih*0.70:x=iw*0.26:y=ih*0.10,scale=1080:1344:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd_freeze = [
        "ffmpeg", "-y", "-loop", "1", "-i", freeze_img, "-t", f"{freeze_dur:.3f}",
        "-filter_complex", vf_freeze, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", part_freeze
    ]
    subprocess.run(cmd_freeze, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Concat lead and freeze
    cmd_cat = [
        "ffmpeg", "-y",
        "-i", part_lead, "-i", part_freeze,
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0,setsar=1[outv]",
        "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd_cat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_04_split_screen(out_path: str):
    """Beat 4 (18.20s - 24.00s): Without the Source keeping him on a leash, he stopped being a security enforcer...
    Visual: Side-by-Side Split Screen Evidence Card!
    Top Frame: ORIGINAL ENFORCER (1999) - Smith in suit with earpiece
    Bottom Frame: AUTONOMOUS VIRUS (2003) - Smith unhooked without earpiece"""
    dur = 24.00 - 18.20  # 5.80s

    enforcer_img = str(CLIPS_DIR / "original_enforcer_smith.jpg")
    viral_img = str(CLIPS_DIR / "viral_smith_clone.jpg")

    split_vf = (
        f"color=c=0x080c0a:s=1080x1920:d={dur:.3f}[bg];"
        f"[0:v]crop=w=iw*0.70:h=ih*0.85:x=iw*0.15:y=ih*0.05,scale=960:540,drawbox=x=0:y=0:w=iw:h=ih:color=0x00FFFF:t=4[top_crop];"
        f"[1:v]crop=w=iw*0.70:h=ih*0.85:x=iw*0.15:y=ih*0.05,scale=960:540,drawbox=x=0:y=0:w=iw:h=ih:color=0x00FF88:t=4[bot_crop];"
        "[bg][top_crop]overlay=60:320[v1];"
        "[v1][bot_crop]overlay=60:960[v2];"
        "[v2]drawtext=fontfile='/System/Library/Fonts/Supplemental/Futura.ttc':text='SYSTEM ENFORCER  //  CONNECTED':"
        "fontcolor=0x00FFFF:fontsize=38:x=70:y=265:shadowcolor=black@0.9:shadowx=2:shadowy=2[v3];"
        "[v3]drawtext=fontfile='/System/Library/Fonts/Supplemental/Futura.ttc':text='AUTONOMOUS VIRUS  //  UNPLUGGED':"
        "fontcolor=0x00FF88:fontsize=38:x=70:y=905:shadowcolor=black@0.9:shadowx=2:shadowy=2,setsar=1[outv]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", enforcer_img,
        "-loop", "1", "-i", viral_img,
        "-t", f"{dur:.3f}",
        "-filter_complex", split_vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_05(out_path: str):
    """Beat 5 (24.00s - 33.20s): A cancer doesn't want to destroy the host. It wants to become it.
    Visual: 100+ Smiths dogpiling and swarming Neo, completely burying him under a mountain of copies."""
    dur = 33.20 - 24.00  # 9.20s
    raw = str(CLIPS_DIR / "raw_beat_05.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "92.0", "-i", str(FOOTAGE_BRAWL2),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='min(zoom+0.0008,1.08)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_beat_06(out_path: str):
    """Beat 6 (33.20s - 38.824s): Which system program do you think is actually more terrifying: Smith or the Architect?
    Visual: The Architect in his stark white room with wall of monitors."""
    dur = TOTAL_DUR - 33.20  # 5.6238s
    raw = str(CLIPS_DIR / "raw_beat_06.mp4")
    cmd = [
        "ffmpeg", "-y", "-ss", "12.0", "-i", str(FOOTAGE_ARCHITECT),
        "-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", raw
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]zoompan=z='max(1.06-0.0006*on,1.0)':d={int(dur*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1344:fps=30[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[outv]"
    )
    cmd2 = [
        "ffmpeg", "-y", "-i", raw, "-t", f"{dur:.3f}",
        "-filter_complex", vf, "-map", "[outv]",
        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    print("=" * 70)
    print("🚀 CINEMA DECODED: THE MATRIX RELOADED REBOOT (SMITH VIRUS)")
    print("=" * 70)

    beat_paths = [
        str(CLIPS_DIR / "beat_01.mp4"),
        str(CLIPS_DIR / "beat_02.mp4"),
        str(CLIPS_DIR / "beat_03.mp4"),
        str(CLIPS_DIR / "beat_04.mp4"),
        str(CLIPS_DIR / "beat_05.mp4"),
        str(CLIPS_DIR / "beat_06.mp4")
    ]

    master_1080p = str(OUT_DIR / "cinema_decoded_matrix_smith_virus_1080p.mp4")
    if not (os.path.exists(master_1080p) and os.path.getsize(master_1080p) > 5000000):
        print("\n🎞️  Rendering Beat 1: Parasitic Identity Theft (Digital Zoom)...")
        create_beat_01(beat_paths[0])

        print("🎞️  Rendering Beat 2: Burly Brawl Forced Assimilation...")
        create_beat_02(beat_paths[1])

        print("🎞️  Rendering Beat 3: Code Shatter & Unhooked Freeze Frame...")
        create_beat_03_freeze(beat_paths[2])

        print("🎞️  Rendering Beat 4: Side-by-Side Split Screen Evidence Card...")
        create_beat_04_split_screen(beat_paths[3])

        print("🎞️  Rendering Beat 5: 100+ Smiths Swarm & Dogpile Neo...")
        create_beat_05(beat_paths[4])

        print("🎞️  Rendering Beat 6: Smith vs The Architect Room...")
        create_beat_06(beat_paths[5])

        print("\n🔗 Concatenating all 6 scene beats into unified video stream...")
        concat_list = PROJ_DIR / "concat_beats.txt"
        with open(concat_list, "w") as f:
            for bp in beat_paths:
                f.write(f"file '{bp}'\n")

        video_only = str(CLIPS_DIR / "visual_montage.mp4")
        cmd_cat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy", video_only
        ]
        subprocess.run(cmd_cat, check=True)

        print(f"\n✨ Assembling 1080p Master with Liam Voiceover & Arc Reactor Cyan HUD Subtitles...")
        cmd_burn = [
            "ffmpeg", "-y",
            "-i", video_only,
            "-i", str(AUDIO_PATH),
            "-filter_complex", f"[0:v]subtitles='{ASS_PATH}':fontsdir='/System/Library/Fonts/Supplemental'[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16",
            "-c:a", "aac", "-b:a", "320k",
            "-t", f"{TOTAL_DUR:.3f}",
            master_1080p
        ]
        subprocess.run(cmd_burn, check=True)
        size_1080 = os.path.getsize(master_1080p) / (1024 * 1024)
        print(f"✅ 1080p Master Assembled: {master_1080p} ({size_1080:.2f} MB)")
    else:
        print(f"✅ Found existing verified 1080p Master: {master_1080p}")

    # STAGE 6: Hardware-Accelerated 8K Super-Resolution Render
    final_8k = str(FINAL_DIR / "cinema_xray_matrix_smith_virus_8k.mp4")
    print(f"\n🚀 Rendering 8K Master (4320x7680 @ 85 Mbps) to: {final_8k}...")
    from pipeline.ultra_upscaler_8k import upgrade_to_super_resolution
    upgrade_to_super_resolution(
        input_video=master_1080p,
        output_video=final_8k,
        target_tier="8K"
    )
    size_8k = os.path.getsize(final_8k) / (1024 * 1024)
    print(f"✅ 8K Super-Resolution Master Rendered: {final_8k} ({size_8k:.2f} MB)")

    # STAGE 7: YouTube Upload as UNLISTED
    print("\n🚀 Uploading 8K Master to YouTube as UNLISTED...")
    from pipeline.youtube_uploader import upload_video
    yt_title = "The Matrix Reloaded — Why Smith Became the Cancer the Machines Couldn't Delete #Shorts"
    yt_desc = (
        "When Neo shattered Agent Smith in the first movie, he didn't delete him—he severed his tether "
        "to the Source, transforming a system security enforcer into an autonomous computer virus that "
        "replicated exponentially from within.\n\n"
        "🎬 Film: The Matrix Reloaded (2003)\n"
        "🎙️ Narration: ElevenLabs Liam (Cinema Decoded Lead Voice)\n"
        "📐 Master Quality: 8K Ultra HD Super-Resolution (4320x7680 @ 30 FPS)\n"
        "💬 Comment Prompt: Which program is more terrifying: Smith or the Architect?\n\n"
        "#CinemaDecoded #TheMatrix #AgentSmith #TheMatrixReloaded #KeanuReeves #FilmAnalysis #Shorts"
    )
    yt_tags = [
        "The Matrix Reloaded", "Agent Smith", "The Matrix", "KeanuReeves",
        "Hugo Weaving", "Cinema Decoded", "Film Analysis", "Burly Brawl", "Shorts"
    ]
    yt_res = upload_video(
        file_path=final_8k,
        title=yt_title,
        description=yt_desc,
        tags=yt_tags,
        privacy_status="unlisted"
    )
    yt_id = yt_res.get("id")
    yt_url = yt_res.get("url") or f"https://youtu.be/{yt_id}"
    print("=" * 70)
    print("🎉 YOUTUBE UPLOAD COMPLETE!")
    print(f"   Video ID: {yt_id}")
    print(f"   URL:      {yt_url}")
    print(f"   Privacy:  UNLISTED")
    print("=" * 70)

    # STAGE 8: Send confirmation email to Vinaybtnofearv@gmail.com
    print("\n📧 Sending confirmation email via Apple Mail...")
    email_to = "Vinaybtnofearv@gmail.com"
    email_subject = "Cinema Decoded: The Matrix Reloaded (8K Unlisted) is Live on YouTube!"
    email_body = (
        f"Hi Vinay,\n\n"
        f"Your requested video for The Matrix Reloaded has been rendered in 8K Ultra HD and uploaded to YouTube as Unlisted!\n\n"
        f"🎬 Title: {yt_title}\n"
        f"🔗 YouTube Link: {yt_url}\n"
        f"🎙️ Narration: ElevenLabs Liam (Clean linear normalized)\n"
        f"📐 Resolution: 8K Ultra HD (4320x7680 @ 30 FPS)\n"
        f"🎨 Subtitles: Style 7 Arc Reactor Cyan HUD\n"
        f"🔍 Editorial Features:\n"
        f"   - Digital zoom on Smith's parasitic hand assimilation\n"
        f"   - Freeze-frame on Smith's face when unhooked from the Source\n"
        f"   - Side-by-side split screen: System Enforcer (1999) vs Autonomous Virus (2003)\n\n"
        f"Best regards,\n"
        f"Cinema Decoded Autonomous Pipeline"
    )

    osa_script = f'''
    tell application "Mail"
        set newMsg to make new outgoing message with properties {{subject:"{email_subject}", content:"{email_body}", visible:false}}
        tell newMsg
            make new to recipient at end of to recipients with properties {{address:"{email_to}"}}
            send
        end tell
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"✅ Confirmation email sent successfully to {email_to}")
        else:
            print(f"⚠️ Apple Mail note: {res.stderr}")
    except Exception as e:
        print(f"⚠️ Email sending warning: {e}")

    # Register in database
    from pipeline.topic_database import TopicDatabase
    db = TopicDatabase()
    db.add_completed_topic(
        topic_slug="matrix_reloaded_smith_virus",
        movie_name="The Matrix Reloaded (2003)",
        film_cluster="Cinematic Psychology & Visual Storytelling",
        title=yt_title,
        hook="The film shows you in its opening seconds that Smith's new superpower isn't flying—it's parasitic identity theft.",
        core_thesis="When Neo shattered Smith in the first movie, he didn't destroy him—he severed his tether to the Source, transforming a system security enforcer into an autonomous computer virus.",
        category_lens="Film Scene Analysis",
        scheduled_slot="ANY",
        scheduled_time_iso=None,
        youtube_video_id=yt_id,
        youtube_url=yt_url
    )
    print("💾 Registered in completed_topics database!")


if __name__ == "__main__":
    main()

