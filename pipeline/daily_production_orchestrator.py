"""
Cinema X-Ray: 2-Video Daily Production Orchestrator
---------------------------------------------------
Implements Upgrade 4 (Flexible Production Modes):
  Mode 1: DAILY (--mode daily)
    - Automatically pulls the 2 highest virality-scored topics from the 100+ candidate pool.
    - Schedules Morning (12:30 PM IST) and Evening (8:30 PM IST) slots.
    - Enforces strict movie diversity (no two videos on the same film on the same day).
  Mode 2: TRENDING (--mode trending)
    - Automatically queries the Trending & Release Radar for active trailer drops and upcoming blockbusters.
    - Prioritizes topics riding organic search spikes (e.g., Avengers: Doomsday, The Batman Part II).
  Mode 3: CUSTOM (--mode custom --movie "..." --topic "...")
    - Allows the user/operator to manually target any film, trailer, or custom scene on demand.

Safety: Autonomous cron scheduling remains strictly disabled per engineering guidelines.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.topic_database import TopicDatabase
from pipeline.topic_ideation_engine import TopicIdeationEngine
from pipeline.trending_radar import TrendingRadar
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
    virality_score: float
    category: str
    project_dir: Path


class DailyProductionOrchestrator:
    """Orchestrates production across Daily, Trending, and Custom modes with complete workspace isolation."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else REPO_ROOT
        self.db = TopicDatabase()
        self.ideation_engine = TopicIdeationEngine()
        self.radar = TrendingRadar()
        self.qf = QualityFramework()

    def plan_daily_batch(self, count: int = 2) -> List[ProductionSlot]:
        """
        MODE 1: DAILY BATCH
        Pulls top virality-scored candidates from the 100+ topic pool,
        enforcing distinct movies for Morning and Evening slots.
        """
        completed = {r["topic_slug"].lower() for r in self.db.get_completed_topics()}
        reserved = {r["topic_slug"].lower() for r in self.db.get_active_reservations()}

        # Query top candidates from 100+ pool
        candidates = self.ideation_engine.get_top_candidates(limit=50)

        selected: List[Dict[str, Any]] = []
        selected_movies = set()

        for cand in candidates:
            slug = cand["topic_slug"].lower()
            m_clean = cand["movie_name"].strip().lower()

            if slug in completed or slug in reserved:
                continue
            if m_clean in selected_movies:
                continue

            selected.append(cand)
            selected_movies.add(m_clean)
            if len(selected) >= count:
                break

        # Fallback to catalog if needed
        if len(selected) < count:
            cat_candidates = self.db.select_daily_batch(count=count)
            for c in cat_candidates:
                if len(selected) >= count:
                    break
                if c["topic_slug"].lower() not in completed and c["movie_name"].lower() not in selected_movies:
                    selected.append(c)
                    selected_movies.add(c["movie_name"].lower())

        now_utc = datetime.now(timezone.utc)
        tomorrow = now_utc.date() + timedelta(days=1)
        morning_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0, 0, tzinfo=timezone.utc)
        evening_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0, tzinfo=timezone.utc)

        slots_def = [
            ("SLOT_1_MORNING", "Morning Prime (12:30 PM IST)", "12:30 PM IST", morning_dt.isoformat()),
            ("SLOT_2_EVENING", "Evening Prime (8:30 PM IST)", "8:30 PM IST", evening_dt.isoformat())
        ]

        production_slots: List[ProductionSlot] = []

        for i, cand in enumerate(selected[:count]):
            s_id, s_name, ist_desc, utc_iso = slots_def[i]
            slug = cand["topic_slug"]
            movie = cand["movie_name"]
            proj_name = f"cinema-decoded-{slug}"
            proj_dir = self.repo_root / "projects" / proj_name

            # Reserve topic in SQLite
            self.db.reserve_topic(
                topic_slug=slug,
                movie_name=movie,
                title=cand["title"],
                worker_id=f"daily_orchestrator_{s_id}"
            )

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
                virality_score=float(cand.get("total_virality_score", 90.0)),
                category=cand.get("category", "Film Analysis"),
                project_dir=proj_dir
            )
            production_slots.append(slot)

        return production_slots

    def plan_trending_batch(self, count: int = 1) -> List[ProductionSlot]:
        """
        MODE 2: TRENDING & RADAR BATCH
        Pulls candidates flagged by the Trending & Release Radar.
        """
        trending_candidates = self.ideation_engine.get_top_candidates(limit=10, trending_only=True)
        if not trending_candidates:
            # Fallback to highest virality candidates
            trending_candidates = self.ideation_engine.get_top_candidates(limit=10)

        now_utc = datetime.now(timezone.utc)
        target_dt = now_utc + timedelta(hours=3)

        slots: List[ProductionSlot] = []
        for i, cand in enumerate(trending_candidates[:count]):
            slug = cand["topic_slug"]
            movie = cand["movie_name"]
            proj_name = f"cinema-decoded-{slug}"
            proj_dir = self.repo_root / "projects" / proj_name

            slot = ProductionSlot(
                slot_id=f"TRENDING_{i+1}",
                slot_name=f"Trending Release Spike ({cand.get('trending_tag', 'Radar')})",
                target_publish_ist="Immediate / Peak Buzz",
                target_publish_utc_iso=target_dt.isoformat(),
                topic_slug=slug,
                movie_name=movie,
                title=cand["title"],
                core_thesis=cand.get("core_thesis", ""),
                director=cand.get("director", ""),
                virality_score=float(cand.get("total_virality_score", 95.0)),
                category=cand.get("category", "Trending Radar"),
                project_dir=proj_dir
            )
            slots.append(slot)

        return slots

    def plan_custom_batch(self, movie: str, topic: str, thesis: Optional[str] = None) -> List[ProductionSlot]:
        """
        MODE 3: CUSTOM / TARGETED TOPIC
        Directs the pipeline to produce a specific movie/topic on demand.
        """
        slug = re.sub(r"[^a-z0-9]+", "-", f"{movie}-{topic[:30]}".lower()).strip("-")
        proj_dir = self.repo_root / "projects" / f"cinema-decoded-{slug}"
        now_utc = datetime.now(timezone.utc)

        slot = ProductionSlot(
            slot_id="CUSTOM_TARGET",
            slot_name="User Directed Target",
            target_publish_ist="Immediate On-Demand",
            target_publish_utc_iso=(now_utc + timedelta(hours=2)).isoformat(),
            topic_slug=slug,
            movie_name=movie,
            title=topic,
            core_thesis=thesis or f"Deep structural analysis of {movie} exploring {topic}.",
            director="Target Filmmaker",
            virality_score=95.0,
            category="Custom Production",
            project_dir=proj_dir
        )
        return [slot]

    def display_plan(self, slots: List[ProductionSlot], mode_name: str = "DAILY") -> None:
        """Prints a human-readable summary of the scheduled plan."""
        print(f"\n{'='*80}")
        print(f"🎬 CINEMA X-RAY: PRODUCTION PLAN [MODE: {mode_name.upper()}]")
        print(f"{'='*80}")
        for s in slots:
            print(f"\n▶ [{s.slot_id}] {s.slot_name}")
            print(f"  • Film:           {s.movie_name} (Dir: {s.director})")
            print(f"  • Category:       {s.category}")
            print(f"  • Virality Score: {s.virality_score:.1f}/100")
            print(f"  • Topic:          {s.title}")
            print(f"  • Thesis:         {s.core_thesis}")
            print(f"  • Target Release: {s.target_publish_ist} ({s.target_publish_utc_iso})")
            print(f"  • Workspace:      {s.project_dir.name}")
        print(f"\n{'='*80}")
        print("🔒 SAFETY NOTICE: Permanent autonomous scheduler is DISABLED.")
        print("   This plan confirms multi-mode architectural readiness.")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cinema X-Ray Multi-Mode Production Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["daily", "trending", "custom"],
        default="daily",
        help="Production mode: 'daily' (2-video batch), 'trending' (radar-driven), or 'custom' (user-specified)"
    )
    parser.add_argument("--movie", type=str, default="", help="Movie title (for custom mode)")
    parser.add_argument("--topic", type=str, default="", help="Specific topic (for custom mode)")
    parser.add_argument("--thesis", type=str, default="", help="Optional thesis statement (for custom mode)")
    parser.add_argument("--plan", action="store_true", help="Display scheduled plan without executing production")

    args = parser.parse_args()

    orchestrator = DailyProductionOrchestrator()

    if args.mode == "trending":
        slots = orchestrator.plan_trending_batch()
        orchestrator.display_plan(slots, mode_name="TRENDING RADAR")
    elif args.mode == "custom":
        if not args.movie or not args.topic:
            print("⚠️ Custom mode requires both --movie and --topic arguments.")
            print("   Example: python daily_production_orchestrator.py --mode custom --movie 'Fight Club' --topic 'Why Tyler Durden Has No Name'")
            sys.exit(1)
        slots = orchestrator.plan_custom_batch(args.movie, args.topic, args.thesis)
        orchestrator.display_plan(slots, mode_name="CUSTOM TARGET")
    else:
        slots = orchestrator.plan_daily_batch(count=2)
        orchestrator.display_plan(slots, mode_name="DAILY 2-VIDEO BATCH")
