#!/usr/bin/env python3
"""
Cinema X-Ray Pinned Comment Manager CLI
Usage:
    python manage_comments.py --auth
    python manage_comments.py --all-existing
    python manage_comments.py --video-id <ID> --text "Your comment"
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.youtube_commenter import (
    get_comment_service,
    post_top_level_comment,
    post_default_comments,
    DEFAULT_COMMENTS
)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cinema X-Ray Pinned Comment Manager")
    parser.add_argument("--auth", action="store_true", help="Authorize YouTube comment permissions in browser")
    parser.add_argument("--video-id", type=str, help="YouTube video ID to comment on")
    parser.add_argument("--text", type=str, help="Comment text")
    parser.add_argument("--all-existing", action="store_true", help="Post highlight comments to all uploaded videos")
    parser.add_argument("--list", action="store_true", help="List prepared highlight comments for all uploaded videos")

    args = parser.parse_args()

    if args.list:
        print("\n" + "="*70)
        print("PREPARED CREATOR HIGHLIGHT COMMENTS FOR UPLOADED VIDEOS")
        print("="*70)
        for vid, text in DEFAULT_COMMENTS.items():
            print(f"\n▶️ Video ID: {vid} (https://youtu.be/{vid})")
            print(f"----------------------------------------------------------------------")
            print(text)
        print("\n" + "="*70 + "\n")
    elif args.auth:
        get_comment_service()
        print("✅ Comment scopes successfully authorized!")
    elif args.video_id and args.text:
        post_top_level_comment(args.video_id, args.text)
    elif args.all_existing:
        post_default_comments()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
