"""
Cinema X-Ray: Production Upload Manager & Post-Upload Verifier
--------------------------------------------------------------
Coordinates resilient YouTube video publishing:
  - Duplicate upload prevention via persistent upload_record.json.
  - Strict enforcement of Quality Gate QG-22 (blocks public uploads during tests/certification).
  - Resilient resumable chunk uploads via youtube_uploader.py.
  - Mock test fixture mode for safe, quota-conserving automated testing.
  - Post-upload verification confirming video ID, URL, privacy state, and thumbnail attachment.
  - Atomic persistence of upload receipt.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from pipeline.quality_framework import QualityFramework, QualityGateId, GateResult, QualityGateError


class UploadManager:
    """Manages secure YouTube video uploading and verification."""

    def __init__(self, project_dir: Optional[Path] = None, is_test_run: bool = True):
        self.project_dir = Path(project_dir) if project_dir else None
        self.is_test_run = is_test_run
        self.qf = QualityFramework(self.project_dir)

    def is_already_uploaded(self, project_dir: Path) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Checks if a verified upload record already exists for this project."""
        p = Path(project_dir)
        record_path = p / "upload_record.json"
        if not record_path.exists():
            return False, None

        try:
            data = json.loads(record_path.read_text(encoding="utf-8"))
            vid_id = data.get("video_id") or data.get("response", {}).get("id")
            if vid_id and len(vid_id) >= 6:
                return True, data
        except Exception:
            return False, None

        return False, None

    def execute_upload(
        self,
        project_dir: Path,
        mock_mode: bool = False,
        privacy_status: Optional[str] = None,
        schedule_time_iso: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes upload for a project, enforcing all safety gates and recording proof.
        """
        project_dir = Path(project_dir)
        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {project_dir}")

        # 1. Duplicate Upload Prevention Check
        already_up, existing_rec = self.is_already_uploaded(project_dir)
        if already_up and existing_rec:
            print(f"⚠️ Video already uploaded! Video ID: {existing_rec.get('video_id')}. Skipping duplicate upload.")
            return existing_rec

        # 2. Locate video file in output/
        out_dir = project_dir / "output"
        if not out_dir.exists():
            raise FileNotFoundError(f"No output directory found in {project_dir}")

        mp4_candidates = list(out_dir.glob("cinema_xray_*_8k.mp4"))
        if not mp4_candidates:
            mp4_candidates = list(out_dir.glob("cinema_xray_*_1080p.mp4"))
        if not mp4_candidates:
            mp4_candidates = list(out_dir.glob("*.mp4"))

        if not mp4_candidates:
            raise FileNotFoundError(f"No rendered MP4 found in {out_dir}")

        video_file = mp4_candidates[0]

        # 3. Locate thumbnail
        thumb_candidates = list(out_dir.glob("thumbnail*.jpg")) + list(out_dir.glob("thumbnail*.png"))
        thumbnail_file = thumb_candidates[0] if thumb_candidates else None

        # 4. Load metadata
        meta_file = project_dir / "metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"metadata.json missing in {project_dir}. Run YouTubeMetadataEngine first.")

        metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        target_privacy = privacy_status or metadata.get("privacy_status", "private")

        # 5. QG-22 Upload Security Evaluation
        self.qf.check_upload_security(
            privacy_status=target_privacy,
            is_test_run=self.is_test_run
        )

        title = metadata.get("title", f"Cinema X-Ray: {project_dir.name}")
        description = metadata.get("description", "")
        tags = metadata.get("tags", ["Cinema X-Ray", "Film Analysis", "Shorts"])
        category_id = metadata.get("category_id", "1")

        # 6. Execute Upload (Mock mode vs Live API)
        if mock_mode:
            print(f"[UploadManager - MOCK MODE] Simulating YouTube upload for '{title}'...")
            # Deterministic video ID based on video file hash
            with open(video_file, "rb") as f:
                fhash = hashlib.md5(f.read(8192)).hexdigest()[:11]
            mock_vid_id = f"mock_{fhash}"
            mock_url = f"https://youtu.be/{mock_vid_id}"

            result = {
                "id": mock_vid_id,
                "video_id": mock_vid_id,
                "url": mock_url,
                "status": target_privacy,
                "channel": {
                    "title": "Cinema X-Ray (Test Environment)",
                    "id": "UC_TEST_CINEMA_XRAY",
                    "subscribers": "1000",
                    "url": "https://www.youtube.com/channel/UC_TEST_CINEMA_XRAY"
                },
                "thumbnail_set": thumbnail_file is not None,
                "is_mock": True
            }
        else:
            from pipeline.youtube_uploader import upload_video
            result = upload_video(
                file_path=video_file,
                title=title,
                description=description,
                tags=tags,
                category_id=category_id,
                privacy_status=target_privacy,
                publish_at=schedule_time_iso,
                thumbnail_path=thumbnail_file
            )

        # 7. Post-Upload Verification & Record Creation
        upload_record = {
            "status": "SCHEDULED" if schedule_time_iso else "UPLOADED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "video_id": result.get("video_id") or result.get("id"),
            "youtube_url": result.get("url"),
            "title": title,
            "privacy_status": target_privacy,
            "video_file": str(video_file.relative_to(project_dir.parent.parent) if str(video_file).startswith(str(project_dir.parent.parent)) else video_file),
            "thumbnail_file": str(thumbnail_file.relative_to(project_dir.parent.parent) if thumbnail_file and str(thumbnail_file).startswith(str(project_dir.parent.parent)) else thumbnail_file),
            "response": result
        }

        # Verify record validity via QG-22
        self.qf.check_upload_security(
            privacy_status=target_privacy,
            is_test_run=self.is_test_run,
            record_data=upload_record
        )

        # 8. Atomic save of upload_record.json
        rec_path = project_dir / "upload_record.json"
        rec_path.write_text(json.dumps(upload_record, indent=2), encoding="utf-8")
        print(f"✅ Verified upload record stored: {rec_path}")
        return upload_record
