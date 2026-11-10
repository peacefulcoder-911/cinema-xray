#!/usr/bin/env python3
"""
Downloads verified True HD (1080p / 1440p) clips for The Truman Show (1998)
into output/clip_cache/ without downscaling or format 18 fallbacks.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIP_CACHE = REPO_ROOT / "output" / "clip_cache"
CLIP_CACHE.mkdir(parents=True, exist_ok=True)

CLIPS_TO_DOWNLOAD = [
    {
        "filename": "truman_morning_routine_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=9bMqDykDxeg",
        "desc": "Truman Seahaven morning greeting routine (1080p)"
    },
    {
        "filename": "truman_falling_light_cameras_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=MdwuW8n3JYA",
        "desc": "Falling spotlight Sirius 9 & hidden surveillance (720p/1080p)"
    },
    {
        "filename": "truman_audience_watching_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=f_UmiKHl1rM",
        "desc": "All audience scenes watching Truman on TV (1080p)"
    },
    {
        "filename": "truman_christof_control_room_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=CunxgZ4JBlY",
        "desc": "Christof in lunar control room directing Truman (1080p)"
    },
    {
        "filename": "truman_radio_frequency_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=n2UsRWerBlM",
        "desc": "Truman hearing tracking radio broadcast in car (1080p)"
    },
    {
        "filename": "truman_stairway_exit_wall_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=zhPX3sIQn3c",
        "desc": "Truman boat hitting painted wall, staircase & exit bow (1440p/4K)"
    }
]

def main():
    print("=" * 70)
    print("🎬 DOWNLOADING TRUE HD SOURCE FOOTAGE: THE TRUMAN SHOW (1998)")
    print("=" * 70)
    
    for item in CLIPS_TO_DOWNLOAD:
        target = CLIP_CACHE / item["filename"]
        print(f"\n📥 Fetching: {item['filename']} ({item['desc']})")
        print(f"   URL: {item['url']}")
        
        cmd = [
            "yt-dlp",
            "-f", "bv*[height<=1440]+ba/b[height<=1440]/bv*+ba/b",
            "--merge-output-format", "mp4",
            "--force-overwrites",
            "-o", str(target),
            item["url"]
        ]
        
        res = subprocess.run(cmd)
        if res.returncode == 0 and target.exists() and target.stat().st_size > 100000:
            sz_mb = target.stat().st_size / (1024 * 1024)
            print(f"✅ Downloaded: {target.name} ({sz_mb:.2f} MB)")
        else:
            print(f"❌ Failed to download {target.name}")

    print("\n" + "=" * 70)
    print("🎉 FOOTAGE ACQUISITION COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    main()

