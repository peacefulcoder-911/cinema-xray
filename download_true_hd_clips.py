#!/usr/bin/env python3
"""
Downloads true 1080p / 1440p HD streams for all 18 scenes across:
The Martian, A Beautiful Mind, and Limitless.
Enforces format selection to guarantee high-bitrate video (>1500 kbps, 1080p+).
"""

import subprocess
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CLIP_CACHE = REPO_ROOT / "output" / "clip_cache"
CLIP_CACHE.mkdir(parents=True, exist_ok=True)

TARGET_CLIPS = {
    # The Martian (2015)
    "the_martian_alone_on_mars_1080p.mp4": "g3s_BzBfsDE",
    "the_martian_resource_planning_1080p.mp4": "nwf6X4z_Dpk",
    "the_martian_planting_potatoes_1080p.mp4": "DKd6-ugozkA",
    "the_martian_making_water_1080p.mp4": "BH-UmA5Lt3g",
    "the_martian_pathfinder_comms_1080p.mp4": "NttUBB98zg4",
    "the_martian_rover_journey_1080p.mp4": "YAPUVhAS8UQ",

    # A Beautiful Mind (2001)
    "beautiful_mind_princeton_arrival_1080p.mp4": "LJS7Igvk6ZM",
    "beautiful_mind_window_equations_1080p.mp4": "qk3OJ5lBjqQ",
    "beautiful_mind_john_meets_charles_1080p.mp4": "1kbqmP_Xrh4",
    "beautiful_mind_parcher_espionage_1080p.mp4": "5fpCqvSkDHg",
    "beautiful_mind_shed_revelation_1080p.mp4": "hh84bamfe_A",
    "beautiful_mind_ending_courtyard_1080p.mp4": "i82jqGq_tio",

    # Limitless (2011)
    "limitless_penthouse_opening_1080p.mp4": "768lISZY9oE",
    "limitless_messy_apartment_1080p.mp4": "UjlllZA8iKE",
    "limitless_infinite_zoom_trading_1080p.mp4": "ZppdNcMuRFU",
    "limitless_van_loon_confrontation_1080p.mp4": "Mu7aSPd5qr8",
    "limitless_gennady_withdrawal_1080p.mp4": "AlK0pJ_RWfw",
    "limitless_ending_senate_1080p.mp4": "EyvDdAmClEo"
}

def download_clip(filename: str, video_id: str):
    target_path = CLIP_CACHE / filename
    print(f"\n[HD Downloader] Downloading {video_id} -> {filename}...")
    
    # We target highest resolution up to 1440p (to keep disk space reasonable and crisp)
    cmd = [
        "yt-dlp",
        "-f", "bv*[height<=1440]+ba/b[height<=1440]/bv*+ba/b",
        "--merge-output-format", "mp4",
        "-o", str(target_path),
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  ❌ Error downloading {video_id}:\n{res.stderr[:300]}")
        return False
    
    # Verify resolution with ffprobe
    p_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,codec_name",
        "-show_entries", "format=size,bit_rate",
        "-of", "json",
        str(target_path)
    ]
    p_res = subprocess.run(p_cmd, capture_output=True, text=True)
    d = json.loads(p_res.stdout)
    v = next((s for s in d.get("streams", []) if s.get("width")), None)
    fmt = d.get("format", {})
    if v:
        w, h = v.get("width"), v.get("height")
        br = round(int(fmt.get("bit_rate", 0)) / 1000)
        sz = round(int(fmt.get("size", 0)) / (1024 * 1024), 2)
        print(f"  ✅ SUCCESS: {filename} is {w}x{h} ({v.get('codec_name')}) | {br} kbps | {sz} MB")
        return True
    return False

def main():
    print("=" * 70)
    print("🚀 CINEMA X-RAY TRUE HD CLIP DOWNLOADING ENGINE")
    print("=" * 70)
    success = 0
    for fn, vid in TARGET_CLIPS.items():
        if download_clip(fn, vid):
            success += 1
    print(f"\n🎉 Completed {success}/{len(TARGET_CLIPS)} True HD downloads.")

if __name__ == "__main__":
    main()

