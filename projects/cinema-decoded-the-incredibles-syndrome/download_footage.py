#!/usr/bin/env python3
"""
Downloads authentic True HD / 4K clips for Cinema Decoded: The Incredibles.
Uses yt-dlp with --merge-output-format mp4 to output/clip_cache/.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = REPO_ROOT / "output" / "clip_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "filename": "incredibles_incrediboy_intro_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=9-LiOj-saa0",
        "desc": "Scene A: Buddy approaches Mr. Incredible / Incrediboy"
    },
    {
        "filename": "incredibles_mr_incredible_rejection_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=-VGtQoxYbrc",
        "desc": "Scene B: Mr. Incredible rejects Buddy ('I work alone')"
    },
    {
        "filename": "incredibles_syndrome_island_reveal_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=kBUI2cvwhm8",
        "desc": "Scene C: Syndrome adult reveal / Zero Point Energy"
    },
    {
        "filename": "incredibles_omnidroid_battle_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=W_PBXAN3rVw",
        "desc": "Scene D: Mr. Incredible vs Omnidroid lethal testing"
    },
    {
        "filename": "incredibles_syndrome_hero_act_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=uoaX1Ms0nRo",
        "desc": "Scene E: Syndrome staged hero act in Metroville"
    },
    {
        "filename": "incredibles_syndrome_philosophy_1080p.mp4",
        "url": "https://www.youtube.com/watch?v=j6cgIWoUrg0",
        "desc": "Scene F: Syndrome monologue ('When everyone's super, no one will be')"
    }
]

def download_clips():
    print("=" * 70)
    print("🎬 DOWNLOADING AUTHENTIC CINEMATIC FOOTAGE FOR THE INCREDIBLES (2004)")
    print("=" * 70)
    
    for item in CLIPS:
        dest = CACHE_DIR / item["filename"]
        webm_dest = CACHE_DIR / (item["filename"] + ".webm")
        
        # Check if already downloaded as webm or mp4
        if webm_dest.exists() and webm_dest.stat().st_size > 1_000_000 and not dest.exists():
            print(f"🔄 Remuxing {webm_dest.name} -> {dest.name}...")
            subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(webm_dest), "-c", "copy", str(dest)], check=True)
            webm_dest.unlink()

        if dest.exists() and dest.stat().st_size > 1_000_000:
            print(f"✅ Already cached: {item['filename']} ({dest.stat().st_size / (1024*1024):.2f} MB)")
            continue
            
        print(f"\n⬇️  Downloading: {item['filename']}")
        print(f"   Description: {item['desc']}")
        print(f"   URL: {item['url']}")
        
        cmd = [
            "yt-dlp",
            "-f", "bv*[height<=1440]+ba/b[height<=1440]/bv*+ba/b",
            "--merge-output-format", "mp4",
            "--force-overwrites",
            "--no-playlist",
            "-o", str(dest),
            item["url"]
        ]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"⚠️ Primary download failed for {item['filename']}. Retrying with best...")
            fallback_cmd = [
                "yt-dlp",
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "--force-overwrites",
                "--no-playlist",
                "-o", str(dest),
                item["url"]
            ]
            subprocess.run(fallback_cmd, check=True)
            
        if not dest.exists() and webm_dest.exists():
            subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(webm_dest), "-c", "copy", str(dest)], check=True)
            webm_dest.unlink()

        if dest.exists():
            print(f"✅ Downloaded: {dest} ({dest.stat().st_size / (1024*1024):.2f} MB)")
        else:
            print(f"❌ Failed to locate: {dest}")

if __name__ == "__main__":
    download_clips()
