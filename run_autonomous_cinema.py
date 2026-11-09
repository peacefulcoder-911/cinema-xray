#!/usr/bin/env python3
"""
Cinema Decoded: Master Autonomous Production CLI
================================================
Command-line interface to autonomously conceptualize, write, narrate, and render
broadcast-grade 8K YouTube Shorts for Cinema Decoded.

Usage:
  # 1. Fully autonomous next video:
  python3 run_autonomous_cinema.py --auto

  # 2. Targeted movie and scene:
  python3 run_autonomous_cinema.py --movie "Whiplash" --scene "Why Fletcher called the wrong chart Caravan"

  # 3. From an existing Executive Producer Brief file:
  python3 run_autonomous_cinema.py --brief /path/to/brief.md

  # 4. Dry-run (Brief generation + Achird voiceover only, no video render):
  python3 run_autonomous_cinema.py --auto --dry-run

  # 5. List all topics in catalog and their status:
  python3 run_autonomous_cinema.py --list-catalog
"""

import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.autonomous_production_engine import AutonomousProductionEngine
from pipeline.topic_database import TopicDatabase

CATALOG_PATH = REPO_ROOT / "database" / "cinema_scenes_catalog.json"
COMPLETED_PATH = REPO_ROOT / "database" / "completed_topics.json"


def list_catalog():
    print("=" * 70)
    print("🎬 CINEMA DECODED: SCENE CATALOG STATUS")
    print("=" * 70)
    if not CATALOG_PATH.exists():
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        return

    completed_slugs = set()
    completed_titles = set()
    if COMPLETED_PATH.exists():
        try:
            data = json.loads(COMPLETED_PATH.read_text(encoding="utf-8"))
            for t in data.get("topics", []):
                completed_slugs.add(t.get("topic_slug"))
                if t.get("title"):
                    completed_titles.add(t.get("title").lower().strip())
        except Exception:
            pass

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    scenes = catalog.get("scenes", [])
    print(f"Total catalog scenes: {len(scenes)}\n")

    for idx, s in enumerate(scenes, 1):
        slug = s.get("topic_slug")
        title_lower = s.get("topic", "").lower().strip()
        is_done = slug in completed_slugs or title_lower in completed_titles
        status_icon = "✅ COMPLETED" if is_done else "⏳ READY TO PRODUCE"
        print(f"[{idx:02d}] {s.get('movie')} — {s.get('topic')}")
        print(f"     Slug: {slug} | Status: {status_icon}")
        print(f"     Thesis: {s.get('core_thesis')[:80]}...")
        print("-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Cinema Decoded Autonomous YouTube Shorts Production System"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Autonomously pick the next unproduced topic from catalog and produce it."
    )
    parser.add_argument(
        "--movie",
        type=str,
        help="Specific film title to analyze."
    )
    parser.add_argument(
        "--scene",
        type=str,
        help="Specific scene or core concept to analyze."
    )
    parser.add_argument(
        "--brief",
        type=str,
        help="Path to an existing Executive Producer Brief markdown file."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate brief, script, and studio voiceover without rendering video."
    )
    parser.add_argument(
        "--no-8k",
        action="store_true",
        help="Skip 8K upscaling (output 1080p delivery only for quick testing)."
    )
    parser.add_argument(
        "--list-catalog",
        action="store_true",
        help="List all catalog topics with completion status."
    )

    args = parser.parse_args()

    if args.list_catalog:
        list_catalog()
        return

    engine = AutonomousProductionEngine()

    if args.brief:
        print(f"▶️  Executing production from brief: {args.brief}")
        res = engine.produce(
            brief_file=args.brief,
            dry_run=args.dry_run,
            upscale_8k=not args.no_8k
        )
    elif args.movie and args.scene:
        print(f"▶️  Executing production for film: {args.movie} — {args.scene}")
        res = engine.produce(
            movie=args.movie,
            scene=args.scene,
            dry_run=args.dry_run,
            upscale_8k=not args.no_8k
        )
    elif args.auto:
        print("▶️  Executing autonomous production for next catalog topic...")
        res = engine.produce(
            dry_run=args.dry_run,
            upscale_8k=not args.no_8k
        )
    else:
        parser.print_help()
        print("\n💡 Example: python3 run_autonomous_cinema.py --auto")
        sys.exit(1)

    print("\n✅ Execution Finished!")
    if res.get("status") == "COMPLETED":
        print(f"   8K Master: {res.get('master_8k_path')}")
        print(f"   1080p Delivery: {res.get('delivery_1080p_path')}")
        print(f"   Thumbnail: {res.get('thumbnail_path')}")


if __name__ == "__main__":
    main()

