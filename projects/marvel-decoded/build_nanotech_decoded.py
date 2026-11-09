import os
import subprocess

BASE_DIR = '/Users/vinaybt/Downloads/marvel-decoded'
RAW_DIR = os.path.join(BASE_DIR, 'raw_video')
CLIPS_DIR = os.path.join(BASE_DIR, 'clips')
SCRIPT_DIR = os.path.join(BASE_DIR, 'script')
AUDIO_DIR = os.path.join(BASE_DIR, 'audio')
OUT_DIR = os.path.join(BASE_DIR, 'out')

SUITUP_VID = os.path.join(RAW_DIR, 'tony_suitup.mp4')
THANOS_VID = os.path.join(RAW_DIR, 'tony_thanos.mp4')
VOICEOVER_MP3 = os.path.join(AUDIO_DIR, 'nanotech_voiceover.mp3')
ASS_SUBTITLES = os.path.join(SCRIPT_DIR, 'nanotech_fast.ass')

FINAL_MP4 = os.path.join(OUT_DIR, 'tony_nanotech_decoded_final.mp4')

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

def run_cmd(cmd, desc=''):
    print('--- ' + desc + ' ---')
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print('Error in ' + desc + ':')
        print(res.stderr)
        raise RuntimeError('FFmpeg failed: ' + res.stderr)
    return res

def make_video_segment(in_vid, start_t, dur, out_name):
    out_path = os.path.join(CLIPS_DIR, out_name)
    filter_str = (
        '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];'
        '[0:v]scale=1080:-2[fg];'
        '[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1'
    )
    cmd = [
        'ffmpeg', '-y', '-ss', str(start_t), '-t', str(dur),
        '-i', in_vid,
        '-filter_complex', filter_str,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
        '-c:a', 'aac', '-ar', '44100', '-ac', '2',
        out_path
    ]
    run_cmd(cmd, 'Generating ' + out_name)
    return out_path

def make_image_freeze_segment(img_path, dur, out_name, zoom_type='none', zoom_start=1.0, zoom_end=1.0):
    out_path = os.path.join(CLIPS_DIR, out_name)
    
    if zoom_type == 'out':
        fg_scale = f'scale=eval=frame:w=trunc(1080*({zoom_start}-({zoom_start}-{zoom_end})*(t/{dur}))/2)*2:h=-2'
    elif zoom_type == 'in':
        fg_scale = f'scale=eval=frame:w=trunc(1080*({zoom_start}+({zoom_end}-{zoom_start})*(t/{dur}))/2)*2:h=-2'
    else:
        fg_scale = 'scale=1080:-2'

    filter_str = (
        f'[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.35[bg];'
        f'[0:v]{fg_scale}[fg];'
        f'[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1'
    )
    
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-t', str(dur),
        '-i', img_path,
        '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-filter_complex', filter_str,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
        '-c:a', 'aac',
        '-shortest',
        out_path
    ]
    run_cmd(cmd, 'Generating Freeze ' + out_name)
    return out_path

def concat_clips(clip_paths, out_name):
    out_path = os.path.join(CLIPS_DIR, out_name)
    inputs = []
    filter_inputs = ''
    for idx, cp in enumerate(clip_paths):
        inputs.extend(['-i', cp])
        filter_inputs += f'[{idx}:v][{idx}:a]'
    
    filter_complex = f'{filter_inputs}concat=n={len(clip_paths)}:v=1:a=1[v][a]'
    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
        '-c:a', 'aac', '-ar', '44100', '-ac', '2',
        out_path
    ]
    run_cmd(cmd, 'Concatenating into ' + out_name)
    return out_path

def build_all_scenes():
    print('=== BUILDING TONY STARK NANOTECH DECODED SCENES ===')
    scenes = []

    f_glasses = os.path.join(CLIPS_DIR, 'freeze_nano_glasses.jpg')
    f_liquid = os.path.join(CLIPS_DIR, 'freeze_nano_liquid.jpg')
    f_eyes = os.path.join(CLIPS_DIR, 'freeze_nano_eyes.jpg')
    f_cannon = os.path.join(CLIPS_DIR, 'freeze_nano_cannon.jpg')
    f_housing = os.path.join(CLIPS_DIR, 'freeze_nano_housing.jpg')
    f_legs = os.path.join(CLIPS_DIR, 'freeze_nano_legs.jpg')
    f_barehead = os.path.join(CLIPS_DIR, 'freeze_nano_barehead.jpg')
    f_stab = os.path.join(CLIPS_DIR, 'freeze_nano_stab.jpg')
    f_respect = os.path.join(CLIPS_DIR, 'freeze_nano_respect.jpg')

    # SCENE 1 (4.50s): The Terrifying Detail (2.30s motion + 2.20s freeze zoom-in)
    p1a = make_video_segment(SUITUP_VID, 96.0, 2.30, 'nano_s1_a.mp4')
    p1b = make_image_freeze_segment(f_glasses, 2.20, 'nano_s1_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.25)
    scenes.append(concat_clips([p1a, p1b], 'nano_scene_01.mp4'))

    # SCENE 2 (4.20s): Double tap chest, swarming nanobots (2.40s motion + 1.80s freeze zoom-in)
    p2a = make_video_segment(SUITUP_VID, 100.5, 2.40, 'nano_s2_a.mp4')
    p2b = make_image_freeze_segment(f_liquid, 1.80, 'nano_s2_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.20)
    scenes.append(concat_clips([p2a, p2b], 'nano_scene_02.mp4'))

    # SCENE 3 (2.50s): Comic book magic (1.30s motion + 1.20s freeze zoom-out)
    p3a = make_video_segment(SUITUP_VID, 107.0, 1.30, 'nano_s3_a.mp4')
    p3b = make_image_freeze_segment(f_eyes, 1.20, 'nano_s3_b.mp4', zoom_type='out', zoom_start=1.25, zoom_end=1.0)
    scenes.append(concat_clips([p3a, p3b], 'nano_scene_03.mp4'))

    # SCENE 4 (5.50s): Law of Physics - Conservation of Mass (3.00s motion + 2.50s freeze zoom-in)
    p4a = make_video_segment(SUITUP_VID, 114.0, 3.00, 'nano_s4_a.mp4')
    p4b = make_image_freeze_segment(f_cannon, 2.50, 'nano_s4_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.25)
    scenes.append(concat_clips([p4a, p4b], 'nano_scene_04.mp4'))

    # SCENE 5 (4.00s): Stored in RT housing on Titan (2.00s motion + 2.00s freeze zoom-in)
    p5a = make_video_segment(THANOS_VID, 33.0, 2.00, 'nano_s5_a.mp4')
    p5b = make_image_freeze_segment(f_housing, 2.00, 'nano_s5_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.22)
    scenes.append(concat_clips([p5a, p5b], 'nano_scene_05.mp4'))

    # SCENE 6 (6.00s): Thanos Power Stone beam + Watch legs (3.20s motion + 2.80s freeze zoom-in)
    p6a = make_video_segment(THANOS_VID, 39.5, 3.20, 'nano_s6_a.mp4')
    p6b = make_image_freeze_segment(f_legs, 2.80, 'nano_s6_b.mp4', zoom_type='in', zoom_start=1.05, zoom_end=1.30)
    scenes.append(concat_clips([p6a, p6b], 'nano_scene_06.mp4'))

    # SCENE 7 (6.50s): Final stand blade + helmet dissolves (3.20s motion + 3.30s freeze zoom-in)
    p7a = make_video_segment(THANOS_VID, 76.5, 3.20, 'nano_s7_a.mp4')
    p7b = make_image_freeze_segment(f_barehead, 3.30, 'nano_s7_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.25)
    scenes.append(concat_clips([p7a, p7b], 'nano_scene_07.mp4'))

    # SCENE 8 (4.80s): Not invincible - stabbed (2.50s motion + 2.30s freeze zoom-out)
    p8a = make_video_segment(THANOS_VID, 80.5, 2.50, 'nano_s8_a.mp4')
    p8b = make_image_freeze_segment(f_stab, 2.30, 'nano_s8_b.mp4', zoom_type='out', zoom_start=1.25, zoom_end=1.0)
    scenes.append(concat_clips([p8a, p8b], 'nano_scene_08.mp4'))

    # SCENE 9 (7.98s): Choosing which organ to sacrifice (4.00s motion + 3.98s freeze zoom-in)
    p9a = make_video_segment(THANOS_VID, 84.5, 4.00, 'nano_s9_a.mp4')
    p9b = make_image_freeze_segment(f_respect, 3.98, 'nano_s9_b.mp4', zoom_type='in', zoom_start=1.0, zoom_end=1.18)
    scenes.append(concat_clips([p9a, p9b], 'nano_scene_09.mp4'))

    stitched = concat_clips(scenes, 'nano_stitched_scenes.mp4')
    return stitched

def render_master(stitched_vid):
    print('=== RENDERING FINAL MASTER WITH AUDIO & SUBTITLES ===')
    filter_complex = (
        '[1:a]volume=1.0[v_aud];'
        '[0:a]volume=0.22[m_aud];'
        '[v_aud][m_aud]amix=inputs=2:duration=first:dropout_transition=2[a_out];'
        f"[0:v]subtitles='{ASS_SUBTITLES}'[v_out]"
    )

    cmd = [
        'ffmpeg', '-y',
        '-i', stitched_vid,
        '-i', VOICEOVER_MP3,
        '-filter_complex', filter_complex,
        '-map', '[v_out]',
        '-map', '[a_out]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        FINAL_MP4
    ]
    run_cmd(cmd, 'Rendering Final Master Video')
    print('MASTER VIDEO COMPLETE: ' + FINAL_MP4)

if __name__ == '__main__':
    raw_stitched = build_all_scenes()
    render_master(raw_stitched)
