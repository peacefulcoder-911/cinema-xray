"""
Upload Cinema Decoded KGF Chapter 1 (8K Ultra HD) Short to YouTube Channel 'Cinema X-Ray'.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.youtube_uploader import get_youtube_service, get_channel_info
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

VIDEO_FILE = PROJECT_DIR / "out" / "cinema_decoded_kgf_fear_weapon_8k.mp4"
THUMBNAIL_FILE = PROJECT_DIR / "thumbnail.jpg"
METADATA_FILE = PROJECT_DIR / "metadata.json"
RECORD_FILE = PROJECT_DIR / "upload_record.json"

def main():
    print(f"🎬 Initializing YouTube Upload for Cinema Decoded: KGF Chapter 1 (8K UHD)...")
    
    if not VIDEO_FILE.exists():
        raise FileNotFoundError(f"Video file not found: {VIDEO_FILE}")
    
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    title = meta.get("title", "How Rocky Turned FEAR Into His Weapon in KGF #Shorts")
    description = meta.get("description", "")
    tags = meta.get("tags", ["KGF", "Yash", "Cinema Decoded", "Shorts"])
    category_id = str(meta.get("category_id", "1"))
    privacy_status = "public"
    
    service = get_youtube_service()
    channel = get_channel_info(service)
    
    if channel:
        print(f"✅ Verified Channel: {channel['title']} ({channel['url']})")
        print(f"   Subscribers: {channel['subscribers']}")
    else:
        print("⚠️ Channel info not returned, proceeding with authorized service...")
        
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "publicStatsViewable": True
        }
    }
    
    file_size_mb = VIDEO_FILE.stat().st_size / (1024 * 1024)
    chunk_size = 10 * 1024 * 1024  # 10 MB chunks
    media = MediaFileUpload(str(VIDEO_FILE), chunksize=chunk_size, resumable=True, mimetype="video/mp4")
    
    print(f"\n📤 Starting 8K Video Upload:")
    print(f"   Target:  {VIDEO_FILE.name} ({file_size_mb:.2f} MB)")
    print(f"   Title:   {title}")
    print(f"   Privacy: {privacy_status}")
    print(f"   Tags:    {len(tags)} tags")
    
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    retry_count = 0
    max_retries = 5
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
                print(f"   [Retry] Server error {e.resp.status}. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
                
    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"
    
    print(f"\n🎉 8K Video Successfully Uploaded!")
    print(f"   Video ID:   {video_id}")
    print(f"   Watch URL:  {video_url}")
    print(f"   Shorts URL: {shorts_url}")
    print(f"   Privacy:    {privacy_status}")
    
    thumbnail_uploaded = False
    if THUMBNAIL_FILE.exists():
        try:
            print(f"\n🖼️ Setting Custom Thumbnail ({THUMBNAIL_FILE.name})...")
            thumb_media = MediaFileUpload(str(THUMBNAIL_FILE), mimetype="image/jpeg")
            service.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media
            ).execute()
            thumbnail_uploaded = True
            print("   ✅ Custom thumbnail applied successfully!")
        except Exception as e:
            print(f"   ⚠️ Custom thumbnail note: {e}")
            
    upload_record = {
        "video_id": video_id,
        "video_url": video_url,
        "shorts_url": shorts_url,
        "title": title,
        "privacy_status": privacy_status,
        "file_name": VIDEO_FILE.name,
        "file_size_mb": round(file_size_mb, 2),
        "resolution": "4320x7680 (8K Ultra HD)",
        "channel": channel,
        "thumbnail_uploaded": thumbnail_uploaded,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(upload_record, f, indent=2)
    print(f"📄 Upload record saved to: {RECORD_FILE.name}")
    
    # Also record in database/completed_topics.json if present
    db_file = REPO_ROOT / "database" / "completed_topics.json"
    if db_file.exists():
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                db_data = json.load(f)
            new_id = max([t.get("id", 0) for t in db_data.get("topics", [])] + [0]) + 1
            new_topic = {
                "id": new_id,
                "topic_slug": "kgf_chapter_1_rocky_fear_weapon",
                "movie_name": "KGF: Chapter 1",
                "film_cluster": "Indian Action Cinema / Cinema Decoded",
                "title": title,
                "hook": "How does Rocky Bhai conquer KGF where everyone is terrified?",
                "core_thesis": "Inside the gold mines, power was psychological dominance. Garuda ruled because twenty thousand workers believed defiance was impossible. Rocky broke the illusion of fear.",
                "category_lens": "Character Psychology",
                "youtube_video_id": video_id,
                "youtube_url": video_url,
                "scheduled_slot": "INSTANT_PUBLIC",
                "scheduled_time_iso": None,
                "status": "COMPLETED",
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
            db_data["topics"].insert(0, new_topic)
            db_data["total_completed"] = len(db_data["topics"])
            db_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)
            print("🗄️ Recorded topic in database/completed_topics.json")
        except Exception as e:
            print(f"⚠️ Could not update completed_topics.json: {e}")

    return upload_record

if __name__ == "__main__":
    main()

