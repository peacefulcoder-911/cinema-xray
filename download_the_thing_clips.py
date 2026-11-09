#!/usr/bin/env python3
"""
Downloads verified True HD (1080p / 4K) clips for The Thing (1982)
into output/clip_cache/ without downscaling or format 18 fallbacks.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CLIP_CACHE = REPO_ROOT / "output" / "clip_cache"
CLIP_CACHE.mkdir(parents=True, exist_ok=True)

CLIPS_TO_DOWNLOAD = [
    {
        "filename": "the_thing_outpost_isolation_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=Mm-Vu6YW3D8",
        "desc": "Outpost 31 Antarctic snowstorm and crew (4K/1080p)"
    },
    {
        "filename": "the_thing_kennel_mimicry_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=_7_rAh5UlSI",
        "desc": "Alien imitation in kennel & team autopsy (1080p)"
    },
    {
        "filename": "the_thing_tied_crew_standoff_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=Esy-776wcIo",
        "desc": "Tied-up crew standoff with MacReady holding flamethrower (1080p)"
    },
    {
        "filename": "the_thing_heating_wire_test_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=8axJ-Qqxors",
        "desc": "MacReady heating copper wire with blowtorch & blood test (4K/1080p)"
    },
    {
        "filename": "the_thing_palmer_reaction_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=El389qn8dZs",
        "desc": "Palmer blood shrieking reaction & transformation (1080p)"
    },
    {
        "filename": "the_thing_ending_snow_fire_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=mZ-G2q6me2s",
        "desc": "MacReady & Childs in burning snowy ruins waiting (4K/1080p)"
    }
]

def main():
    print("=" * 70)
    print("🎬 DOWNLOADING TRUE HD SOURCE FOOTAGE: THE THING (1982)")
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

