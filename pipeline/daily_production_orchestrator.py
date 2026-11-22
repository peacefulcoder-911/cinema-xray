"""
Cinema X-Ray: 2-Video Daily Production Orchestrator
---------------------------------------------------
Architected for the future autonomous 2-video daily production requirement:
  - Slot 1 (Morning): 12:30 PM IST (07:00 UTC)
  - Slot 2 (Evening): 8:30 PM IST (15:00 UTC)
  - Strict Movie Diversity: No two videos from the same movie on the same day.
  - Complete Pipeline Isolation: Independent workspaces, renders, audio, and QC.
  - Fault Isolation: Slot 2 execution is shielded from Slot 1 failure.
  - Safety Lockdown: Autonomous daily scheduler remains DISABLED per engineering rules.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.topic_database import TopicDatabase
from pipeline.quality_framework import QualityFramework, QualityGateId
from pipeline.production_state_manager import ProductionStateManager, ProductionState
from pipeline.upload_manager import UploadManager
from pipeline.youtube_metadata_engine import YouTubeMetadataEngine


@dataclass
class ProductionSlot:
    slot_id: str
    slot_name: str
    target_publish_ist: str
    target_publish_utc_iso: str
    topic_slug: str
    movie_name: str
    title: str
    core_thesis: str
    director: str
    project_dir: Path


class DailyProductionOrchestrator:
    """Orchestrates daily 2-video production batches with complete workspace isolation."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else REPO_ROOT
        self.db = TopicDatabase()
        self.qf = QualityFramework()

    def plan_daily_batch(self, count: int = 2) -> List[ProductionSlot]:
        """
        Selects candidate topics and schedules them into distinct morning and evening slots.
        Enforces topic reservation and movie diversity.
        """
        candidates = self.db.select_daily_batch(count=count)
        if len(candidates) < count:
            raise RuntimeError(f"Insufficient unique candidates available (found {len(candidates)}, needed {count}).")

        now_utc = datetime.now(timezone.utc)
        # Target tomorrow 07:00 UTC (12:30 PM IST) and 15:00 UTC (8:30 PM IST)
        tomorrow = now_utc.date() + timedelta(days=1)
        morning_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0, 0, tzinfo=timezone.utc)
        evening_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0, tzinfo=timezone.utc)

        slots_def = [
            ("SLOT_1_MORNING", "Morning Prime (12:30 PM IST)", "12:30 PM IST", morning_dt.isoformat()),
            ("SLOT_2_EVENING", "Evening Prime (8:30 PM IST)", "8:30 PM IST", evening_dt.isoformat())
        ]

        production_slots: List[ProductionSlot] = []

        for i, cand in enumerate(candidates[:count]):
            s_id, s_name, ist_desc, utc_iso = slots_def[i]
            slug = cand["topic_slug"]
            movie = cand["movie_name"]
            proj_name = f"cinema-decoded-{slug}"
            proj_dir = self.repo_root / "projects" / proj_name

            # Reserve topic in database
            reserved = self.db.reserve_topic(
                topic_slug=slug,
                movie_name=movie,
                title=cand["title"],
                worker_id=f"daily_orchestrator_{s_id}"
            )
            if not reserved:
                print(f"⚠️ Topic {slug} could not be reserved (already active).")

            slot = ProductionSlot(
                slot_id=s_id,
                slot_name=s_name,
                target_publish_ist=ist_desc,
                target_publish_utc_iso=utc_iso,
                topic_slug=slug,
                movie_name=movie,
                title=cand["title"],
                core_thesis=cand.get("core_thesis", ""),
                director=cand.get("director", ""),
                project_dir=proj_dir
            )
            production_slots.append(slot)

        return production_slots

    def display_plan(self, slots: List[ProductionSlot]) -> None:
        """Prints formatted production schedule plan."""
        print(f"\n{'='*75}")
        print("🎬 CINEMA X-RAY: 2-VIDEO DAILY PRODUCTION SCHEDULE PLAN")
        print(f"{'='*75}")
        for s in slots:
            print(f"\n▶ [{s.slot_id}] {s.slot_name}")
            print(f"  • Scheduled Release: {s.target_publish_ist} ({s.target_publish_utc_iso})")
            print(f"  • Film:              {s.movie_name} (Dir: {s.director})")
            print(f"  • Topic:             {s.title}")
            print(f"  • Thesis:            {s.core_thesis}")
            print(f"  • Workspace:         {s.project_dir.name}")
        print(f"\n{'='*75}")
        print("🔒 SAFETY NOTICE: Recurring autonomous daily scheduler is DISABLED.")
        print("   This plan demonstrates architectural readiness for autonomous activation.")
        print(f"{'='*75}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cinema X-Ray Daily Production Orchestrator")
    parser.add_argument("--plan", action="store_true", help="Inspect and display planned 2-video daily schedule")
    args = parser.parse_args()

    orchestrator = DailyProductionOrchestrator()
    slots = orchestrator.plan_daily_batch(count=2)
    orchestrator.display_plan(slots)
