#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
"""
Cinema Decoded: ChatGPT Automated Production Runner
==================================================
Connects to a ChatGPT shared conversation, extracts the generated breakdown script,
executes the complete local deployment pipeline (voiceover, subtitles, 70% cinematic framing,
Apple Silicon 8K upscaling, QC checks, and YouTube publishing), and records completion.

Usage:
  # 1. Produce video from the linked ChatGPT shared conversation:
  python3 run_chatgpt_cinema.py --url "https://chatgpt.com/share/6af91b43-5120-83e8-846e-2888ec4e2a77" --upload

  # 2. Dry-run test (extract, voiceover & subtitles only, no video render):
  python3 run_chatgpt_cinema.py --url "https://chatgpt.com/share/6af91b43-5120-83e8-846e-2888ec4e2a77" --dry-run

  # 3. Daily sync mode (checks for new scripts daily or runs autonomous generator):
  python3 run_chatgpt_cinema.py --url "https://chatgpt.com/share/6af91b43-5120-83e8-846e-2888ec4e2a77" --daily --upload
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.chatgpt_bridge import ChatGPTBridge
from pipeline.autonomous_production_engine import AutonomousProductionEngine
from pipeline.topic_database import TopicDatabase

DEFAULT_CHAT_URL = "https://chatgpt.com/share/6af91b43-5120-83e8-846e-2888ec4e2a77"
COMPLETED_PATH = REPO_ROOT / "database" / "completed_topics.json"


def is_topic_already_completed(slug: str, title: str) -> bool:
    """Checks database/completed_topics.json to prevent duplicate production."""
    if not COMPLETED_PATH.exists():
        return False
    try:
        data = json.loads(COMPLETED_PATH.read_text(encoding="utf-8"))
        completed_slugs = {t.get("topic_slug") for t in data.get("topics", [])}
        completed_titles = {t.get("title", "").lower().strip() for t in data.get("topics", [])}
        return slug in completed_slugs or title.lower().strip() in completed_titles
    except Exception:
        return False


def produce_from_chatgpt(
    url: str = DEFAULT_CHAT_URL,
    dry_run: bool = False,
    upscale_8k: bool = True,
    upload_youtube: bool = False,
    privacy: str = "unlisted",
    force: bool = False
) -> Dict[str, Any]:
    print("=" * 70)
    print("🤖 CINEMA DECODED: CHATGPT AUTOMATED PRODUCTION PIPELINE")
    print("=" * 70)
    print(f"🔗 Connecting to ChatGPT conversation: {url}")

    bridge = ChatGPTBridge(url)
    parsed = bridge.find_latest_script_or_prompt()

    movie = parsed["movie"]
    headline = parsed["headline"]
    slug = parsed["topic_slug"]
    script_text = parsed["script_text"]
    concept = parsed["central_discovery"]

    print("\n🎬 EXTRACTED BREAKDOWN METADATA:")
    print(f"   Film Title:     {movie}")
    print(f"   Headline:       {headline}")
    print(f"   Topic Slug:     {slug}")
    print(f"   Script Length:  {len(script_text.split())} words")
    print("-" * 70)
    print("📝 PRODUCTION SCRIPT:")
    for line in script_text.split("\n"):
        if line.strip():
            print(f"   {line}")
    print("-" * 70)

    # Check deduplication
    if not force and is_topic_already_completed(slug, headline):
        print(f"\n⚠️  Topic '{headline}' ({slug}) has already been produced and recorded in database!")
        print("   Use --force if you wish to rebuild and re-upload.")
        return {"status": "ALREADY_COMPLETED", "topic_slug": slug}

    # Format complete 11-section Executive Producer Brief for the production engine
    brief_content = f"""# PROJECT: {movie.upper()} — {headline.upper()}

## 1. OBJECTIVE
Produce a broadcast-grade 8K YouTube Short investigating the hidden cinematic psychology underneath {movie}.
The central discovery:
**{concept}**

---
## 2. NON-NEGOTIABLE SCRIPT

### APPROVED NARRATION
"{script_text}"

Preserve the narration verbatim.

---
## 3. SCENE SPECIFICATIONS & SHOT MAP
- Focus Movie: {movie}
- Target Concept: {concept}
- Visual Style: Dark, high contrast, immersive, 70% active cinematic framing with ambient blur backdrop.

---
## 4. TECHNICAL SPECIFICATIONS
- Platform: YouTube Shorts (9:16 vertical)
- Master Resolution: 8K Super-Resolution (4320x7680 @ 85 Mbps)
- Delivery Resolution: 1080x1920 @ 30 FPS
- Narration: Studio single-take voiceover mastered to EBU R128 (-14 LUFS / -1.0 dBFS TP)
- Subtitles: Arc Reactor Cyan HUD ASS (Futura Bold 74pt)
"""

    # Setup project directory
    proj_dir = REPO_ROOT / "projects" / f"cinema-decoded-{slug}"
    proj_dir.mkdir(parents=True, exist_ok=True)
    brief_file = proj_dir / "brief.md"
    brief_file.write_text(brief_content, encoding="utf-8")
    (proj_dir / "script.txt").write_text(script_text, encoding="utf-8")

    print(f"\n📁 Initialized Project Folder: {proj_dir}")
    print(f"📄 Saved Executive Brief:     {brief_file}")

    # Hand off to master AutonomousProductionEngine
    print("\n🚀 Handing off to Autonomous Production Engine...")
    engine = AutonomousProductionEngine()

    result = engine.produce(
        brief_file=str(brief_file),
        dry_run=dry_run,
        upscale_8k=upscale_8k,
        upload_youtube=upload_youtube,
        privacy_status=privacy
    )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Cinema Decoded: ChatGPT Automated Video Production Engine"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_CHAT_URL,
        help="ChatGPT shared conversation URL"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Synthesize audio and subtitles without full video rendering"
    )
    parser.add_argument(
        "--no-8k",
        action="store_true",
        help="Skip 8K upscaling (1080p delivery only)"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the final 8K video to YouTube"
    )
    parser.add_argument(
        "--privacy",
        type=str,
        default="unlisted",
        choices=["unlisted", "public", "private"],
        help="YouTube video privacy status (default: unlisted)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force production even if topic was already produced"
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Run daily polling loop to check for new scripts"
    )

    args = parser.parse_args()

    if args.daily:
        print("⏰ Starting Daily ChatGPT Polling Mode...")
        print(f"   Monitoring: {args.url}")
        print("   Checking every 24 hours (or upon new script detection)...")
        while True:
            try:
                res = produce_from_chatgpt(
                    url=args.url,
                    dry_run=args.dry_run,
                    upscale_8k=not args.no_8k,
                    upload_youtube=args.upload,
                    privacy=args.privacy,
                    force=False
                )
                print(f"Cycle completed at {time.strftime('%Y-%m-%d %H:%M:%S')}: {res.get('status')}")
            except Exception as e:
                print(f"⚠️ Error during daily sync: {e}")
            
            # Sleep 24 hours
            time.sleep(86400)
    else:
        produce_from_chatgpt(
            url=args.url,
            dry_run=args.dry_run,
            upscale_8k=not args.no_8k,
            upload_youtube=args.upload,
            privacy=args.privacy,
            force=args.force
        )


if __name__ == "__main__":
    main()
