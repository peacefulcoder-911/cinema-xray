#!/usr/bin/env python3
"""
Cinema Decoded: YouTube Batch Scheduler for November 10th, 2026.
Uploads 3 Master 8K Ultra HD Shorts scheduled for release across 3 slots:
  - Slot 1 (MORNING):   10:30 AM IST (05:00 UTC) -> The Truman Show
  - Slot 2 (AFTERNOON): 02:30 PM IST (09:00 UTC) -> The Thing
  - Slot 3 (NIGHT):     08:30 PM IST (15:00 UTC) -> The Incredibles
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.youtube_uploader import get_youtube_service, get_channel_info
from pipeline.topic_database import TopicDatabase

BATCH_CONFIG = [
    {
        "slot_name": "MORNING",
        "film": "The Truman Show",
        "film_cluster": "Psychological & Media Dystopia",
        "topic_slug": "the-truman-show-audience",
        "category_lens": "Media Exploitation & Audience Complicity",
        "publish_at_iso": "2026-11-10T05:00:00Z",
        "local_time_desc": "10:30 AM IST (Tuesday, Nov 10, 2026)",
        "project_dir": REPO_ROOT / "projects" / "cinema-decoded-the-truman-show-audience",
        "video_path": REPO_ROOT / "output" / "final_video" / "cinema_xray_the_truman_show_8k.mp4",
        "thumbnail_path": REPO_ROOT / "output" / "thumbnails_short" / "truman_show_audience_thumb.jpg",
        "metadata_path": REPO_ROOT / "projects" / "cinema-decoded-the-truman-show-audience" / "metadata.json",
        "record_path": REPO_ROOT / "projects" / "cinema-decoded-the-truman-show-audience" / "upload_record.json",
    },
    {
        "slot_name": "AFTERNOON",
        "film": "The Thing",
        "film_cluster": "Psychological Horror & Sci-Fi",
        "topic_slug": "the-thing-paranoia",
        "category_lens": "Paranoia & The Collapse of Trust",
        "publish_at_iso": "2026-11-10T09:00:00Z",
        "local_time_desc": "02:30 PM IST (Tuesday, Nov 10, 2026)",
        "project_dir": REPO_ROOT / "projects" / "cinema-decoded-the-thing-paranoia",
        "video_path": REPO_ROOT / "output" / "final_video" / "cinema_xray_the_thing_8k.mp4",
        "thumbnail_path": REPO_ROOT / "output" / "thumbnails_short" / "the_thing_paranoia_thumb.jpg",
        "metadata_path": REPO_ROOT / "projects" / "cinema-decoded-the-thing-paranoia" / "metadata.json",
        "record_path": REPO_ROOT / "projects" / "cinema-decoded-the-thing-paranoia" / "upload_record.json",
    },
    {
        "slot_name": "NIGHT",
        "film": "The Incredibles",
        "film_cluster": "Animation & Psychological Archetypes",
        "topic_slug": "the-incredibles-syndrome",
        "category_lens": "Villain Psychology & Technological Revenge",
        "publish_at_iso": "2026-11-10T15:00:00Z",
        "local_time_desc": "08:30 PM IST (Tuesday, Nov 10, 2026)",
        "project_dir": REPO_ROOT / "projects" / "cinema-decoded-the-incredibles-syndrome",
        "video_path": REPO_ROOT / "output" / "final_video" / "cinema_xray_the_incredibles_8k.mp4",
        "thumbnail_path": REPO_ROOT / "output" / "thumbnails_short" / "the_incredibles_syndrome_thumb.jpg",
        "metadata_path": REPO_ROOT / "projects" / "cinema-decoded-the-incredibles-syndrome" / "metadata.json",
        "record_path": REPO_ROOT / "projects" / "cinema-decoded-the-incredibles-syndrome" / "upload_record.json",
    }
]


def upload_single_video(service, item: dict):
    video_file = Path(item["video_path"])
    thumb_file = Path(item["thumbnail_path"])
    meta_file = Path(item["metadata_path"])
    
    if not video_file.exists():
        raise FileNotFoundError(f"Missing master 8K video: {video_file}")
    if not meta_file.exists():
        raise FileNotFoundError(f"Missing metadata: {meta_file}")
        
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    title = meta.get("title", f"{item['film']} #Shorts")
    desc = meta.get("description", "")
    tags = meta.get("tags", [item["film"], "Cinema Decoded", "Shorts"])
    category_id = str(meta.get("category_id", "1"))
    publish_at_iso = item["publish_at_iso"]
    
    body = {
        "snippet": {
            "title": title[:100],
            "description": desc[:5000],
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": "private",  # REQUIRED by YouTube API when publishAt is set
            "publishAt": publish_at_iso,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "publicStatsViewable": True
        }
    }
    
    file_size_mb = video_file.stat().st_size / (1024 * 1024)
    chunk_size = 10 * 1024 * 1024  # 10 MB chunks
    media = MediaFileUpload(str(video_file), chunksize=chunk_size, resumable=True, mimetype="video/mp4")
    
    print("\n" + "=" * 70)
    print(f"🎬 UPLOADING TO YOUTUBE: [{item['slot_name']}] {item['film']}")
    print("=" * 70)
    print(f"   Target Video:    {video_file.name} ({file_size_mb:.2f} MB)")
    print(f"   Title:           {title}")
    print(f"   Scheduled For:   {item['local_time_desc']} ({publish_at_iso})")
    print(f"   Privacy:         PRIVATE (auto-publishes to PUBLIC at scheduled time)")
    print(f"   Tags:            {len(tags)} tags")
    
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    retry_count = 0
    max_retries = 6
    start_time = time.time()
    
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                percent = int(status.progress() * 100)
                elapsed = time.time() - start_time
                mb_uploaded = status.progress() * file_size_mb
                speed = mb_uploaded / elapsed if elapsed > 0 else 0
                print(f"   [Upload Progress] {percent:3d}% ({mb_uploaded:.1f}/{file_size_mb:.1f} MB) @ {speed:.2f} MB/s")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retry_count += 1
                if retry_count > max_retries:
                    raise
                wait_time = 2 ** retry_count
                print(f"   ⚠️ Server error ({e.resp.status}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
                
    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n🎉 VIDEO UPLOADED SUCCESSFULLY!")
    print(f"   Video ID:  {video_id}")
    print(f"   Watch URL: {video_url}")
    
    # Custom Thumbnail
    thumbnail_set = False
    if thumb_file.exists():
        try:
            print(f"   Setting custom vertical thumbnail from: {thumb_file.name}...")
            thumb_media = MediaFileUpload(str(thumb_file), mimetype="image/jpeg")
            service.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media
            ).execute()
            thumbnail_set = True
            print(f"   ✅ Custom thumbnail applied successfully!")
        except Exception as e:
            print(f"   ⚠️ Could not set thumbnail: {e}")
            
    # Save project upload record
    record = {
        "status": "SCHEDULED",
        "slot": item["slot_name"],
        "publish_at_iso": publish_at_iso,
        "local_time_desc": item["local_time_desc"],
        "video_id": video_id,
        "youtube_url": video_url,
        "title": title,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "video_file": str(video_file),
        "thumbnail_file": str(thumb_file) if thumbnail_set else None,
        "video_size_mb": round(file_size_mb, 2),
        "youtube_response": response
    }
    with open(item["record_path"], "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        
    return record


def main():
    print("=" * 70)
    print("🚀 CINEMA X-RAY: 3-SLOT YOUTUBE BATCH UPLOADER & SCHEDULER")
    print(f"   Target Date: Tuesday, November 10th, 2026")
    print("=" * 70)
    
    service = get_youtube_service()
    channel = get_channel_info(service)
    
    if channel:
        print(f"✅ Authenticated Channel: {channel['title']} ({channel['url']})")
        print(f"   Subscriber Count:      {channel['subscribers']}")
    else:
        print("⚠️ Channel info not returned, proceeding with authorized service...")
        
    db = TopicDatabase()
    results = []
    
    for item in BATCH_CONFIG:
        res = upload_single_video(service, item)
        results.append(res)
        
        # Save to SQLite TopicDatabase
        try:
            db.add_completed_topic(
                topic_slug=item["topic_slug"],
                movie_name=item["film"],
                film_cluster=item["film_cluster"],
                title=res["title"],
                hook=f"{item['film']} analysis on Cinema Decoded",
                core_thesis=item.get("category_lens", ""),
                category_lens=item.get("category_lens", ""),
                scheduled_slot=item["slot_name"],
                scheduled_time_iso=item["publish_at_iso"],
                youtube_video_id=res["video_id"],
                youtube_url=res["youtube_url"]
            )
            print(f"   ✅ Recorded in TopicDatabase: {item['topic_slug']}")
        except Exception as db_err:
            print(f"   ⚠️ Warning recording to DB: {db_err}")
            
    summary_path = REPO_ROOT / "output" / "upload_batch_nov10_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "target_date": "2026-11-10",
            "channel": channel,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "videos": results
        }, f, indent=2)
        
    print("\n" + "=" * 70)
    print("🎉 ALL 3 VIDEOS SUCCESSFULLY UPLOADED & SCHEDULED FOR NOV 10TH!")
    print("=" * 70)
    for r in results:
        print(f"  • [{r['slot']:9}] {r['title']}")
        print(f"    Release: {r['local_time_desc']} | URL: {r['youtube_url']}")
    print(f"\n📄 Full batch report saved to: {summary_path}")


if __name__ == "__main__":
    main()

