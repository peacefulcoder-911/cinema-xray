"""
Cinema X-Ray Completed Topics Database & Deduplication Gatekeeper
-----------------------------------------------------------------
Maintains a persistent SQLite & JSON registry of all produced videos to guarantee:
1. Zero topic duplication across daily autonomous batches.
2. Cross-referencing against film titles, analytical lenses, and core theses.
3. GitOps-friendly persistence (committed back to GitHub repo after each run).
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = REPO_ROOT / "database"
DB_PATH = DB_DIR / "completed_topics.db"
JSON_EXPORT_PATH = DB_DIR / "completed_topics.json"


class TopicDatabase:
    """Persistent SQLite database manager for tracking produced Cinema X-Ray topics."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.json_path = self.db_path.parent / "completed_topics.json"
        self._init_db()

    def _init_db(self):
        """Create tables and indexes if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS completed_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_slug TEXT UNIQUE NOT NULL,
                movie_name TEXT NOT NULL,
                film_cluster TEXT NOT NULL,
                title TEXT NOT NULL,
                hook TEXT,
                core_thesis TEXT NOT NULL,
                category_lens TEXT NOT NULL,
                youtube_video_id TEXT,
                youtube_url TEXT,
                scheduled_slot TEXT NOT NULL DEFAULT 'ANY',
                scheduled_time_iso TEXT,
                status TEXT NOT NULL DEFAULT 'COMPLETED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topics_movie ON completed_topics(movie_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topics_slug ON completed_topics(topic_slug);")
            conn.commit()

    def seed_initial_history(self):
        """Seed the database with all historic productions if currently empty."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM completed_topics;")
            count = cur.fetchone()[0]
            if count > 0:
                return

            if self.json_path.exists():
                try:
                    data = json.loads(self.json_path.read_text(encoding="utf-8"))
                    topics = data.get("topics", [])
                    if topics:
                        for t in topics:
                            cur.execute("""
                            INSERT OR IGNORE INTO completed_topics
                            (id, topic_slug, movie_name, film_cluster, title, hook, core_thesis, category_lens, scheduled_slot, scheduled_time_iso, youtube_video_id, youtube_url, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                t.get("id"),
                                t.get("topic_slug"),
                                t.get("movie_name"),
                                t.get("film_cluster"),
                                t.get("title"),
                                t.get("hook"),
                                t.get("core_thesis"),
                                t.get("category_lens"),
                                t.get("scheduled_slot"),
                                t.get("scheduled_time_iso"),
                                t.get("youtube_video_id"),
                                t.get("youtube_url"),
                                t.get("status", "COMPLETED"),
                                t.get("created_at")
                            ))
                        conn.commit()
                        return
                except Exception as e:
                    print(f"Warning: could not seed from json: {e}")

            initial_records = [
                {
                    "topic_slug": "interstellar_ticking_clock_meaning",
                    "movie_name": "Interstellar",
                    "film_cluster": "Christopher Nolan Cinema",
                    "title": "The Secret Meaning of the Ticking Clock on Miller's Planet",
                    "hook": "Every tick in Hans Zimmer's soundtrack is exactly 1.25 seconds apart.",
                    "core_thesis": "Because 1 hour on Miller's planet equals 7 Earth years, each 1.25-second tick represents an entire 24-hour day passing on Earth.",
                    "category_lens": "Hidden Details & Symbolism",
                    "scheduled_slot": "NIGHT"
                },
                {
                    "topic_slug": "batman_begins_fear_as_weapon",
                    "movie_name": "Batman Begins",
                    "film_cluster": "Christopher Nolan Cinema",
                    "title": "Batman Turns His Childhood Fear Into a Weapon",
                    "hook": "Batman was built from the very thing Bruce Wayne feared most.",
                    "core_thesis": "Bruce does not overcome his fear of bats; he masters what fear does to the human psyche and weaponizes it into an immortal symbol.",
                    "category_lens": "Character Psychology",
                    "scheduled_slot": "MORNING"
                },
                {
                    "topic_slug": "cap_mjolnir_worthiness_truth",
                    "movie_name": "Avengers: Endgame",
                    "film_cluster": "Marvel Cinematic Universe (MCU)",
                    "title": "The Exact Second Cap Became Worthy",
                    "hook": "Did Cap suddenly become worthy in Endgame, or did he fake it in Age of Ultron?",
                    "core_thesis": "Worthiness is binary. The second Mjolnir budged in Age of Ultron, Steve stopped pulling to spare Thor's pride in front of the Avengers.",
                    "category_lens": "Character Psychology",
                    "scheduled_slot": "AFTERNOON"
                },
                {
                    "topic_slug": "tony_nanotech_secret_panic",
                    "movie_name": "Avengers: Infinity War",
                    "film_cluster": "Marvel Cinematic Universe (MCU)",
                    "title": "Why Tony's Nanotech Suit Consumes His Clothes",
                    "hook": "When Tony tapped his reactor, the nanotech vaporized his sunglasses and jacket.",
                    "core_thesis": "Driven by severe PTSD, Tony designed the Mark 50 to consume whatever fabric he was wearing into raw carbon plating to deploy defense in milliseconds.",
                    "category_lens": "Hidden Details & Symbolism",
                    "scheduled_slot": "MORNING"
                },
                {
                    "topic_slug": "dark_knight_hospital_explosion_truth",
                    "movie_name": "The Dark Knight",
                    "film_cluster": "Christopher Nolan Cinema",
                    "title": "The Truth Behind the Joker Hospital Detonation",
                    "hook": "Heath Ledger's detonator pause was not an accident—it was masterwork calculation.",
                    "core_thesis": "Nolan and Ledger rehearsed the delay to mirror the Joker's theatrical control over chaos.",
                    "category_lens": "Cinematic Storytelling & Film Language",
                    "scheduled_slot": "AFTERNOON"
                }
            ]

            for rec in initial_records:
                cur.execute("""
                INSERT OR IGNORE INTO completed_topics 
                (topic_slug, movie_name, film_cluster, title, hook, core_thesis, category_lens, scheduled_slot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec["topic_slug"],
                    rec["movie_name"],
                    rec["film_cluster"],
                    rec["title"],
                    rec["hook"],
                    rec["core_thesis"],
                    rec["category_lens"],
                    rec["scheduled_slot"]
                ))
            conn.commit()

        self.export_to_json()

    def get_completed_topics(self) -> List[Dict[str, Any]]:
        """Retrieve all completed topics ordered by date."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM completed_topics ORDER BY id DESC;")
            return [dict(r) for r in cur.fetchall()]

    get_all_completed_topics = get_completed_topics
    all_completed_topics = get_completed_topics
    list_completed_topics = get_completed_topics

    def is_duplicate(self, title: str, movie_name: str = "", core_thesis: str = "") -> Tuple[bool, str]:
        """
        Check if a candidate topic duplicates an existing record.
        Returns (is_duplicate: bool, reason: str).
        """
        norm_title = re.sub(r'[^a-z0-9 ]', '', title.lower()).strip()
        words_title = set(norm_title.split())

        norm_thesis = re.sub(r'[^a-z0-9 ]', '', core_thesis.lower()).strip()
        words_thesis = set(norm_thesis.split())

        records = self.get_completed_topics()
        for r in records:
            past_title = re.sub(r'[^a-z0-9 ]', '', r["title"].lower()).strip()
            # 1. Exact or near-exact title match
            if norm_title == past_title or past_title in norm_title or norm_title in past_title:
                return True, f"Duplicate of past title: '{r['title']}' (ID #{r['id']})"

            # 2. Token overlap similarity on title
            past_words = set(past_title.split())
            if words_title and past_words:
                jaccard = len(words_title & past_words) / len(words_title | past_words)
                if jaccard > 0.65:
                    return True, f"High title similarity ({jaccard:.2f}) with: '{r['title']}'"

            # 3. Same movie + overlapping core thesis
            if movie_name and r["movie_name"].lower() == movie_name.lower():
                past_thesis_words = set(re.sub(r'[^a-z0-9 ]', '', r["core_thesis"].lower()).split())
                if words_thesis and past_thesis_words:
                    thesis_overlap = len(words_thesis & past_thesis_words) / len(words_thesis | past_thesis_words)
                    if thesis_overlap > 0.55:
                        return True, f"Core thesis already analyzed for '{movie_name}': '{r['core_thesis']}'"

        return False, ""

    def add_completed_topic(
        self,
        topic_slug: str,
        movie_name: str,
        film_cluster: str,
        title: str,
        hook: str,
        core_thesis: str,
        category_lens: str,
        scheduled_slot: str = "ANY",
        scheduled_time_iso: Optional[str] = None,
        youtube_video_id: Optional[str] = None,
        youtube_url: Optional[str] = None
    ) -> int:
        """Add a newly produced and verified topic into the completed database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO completed_topics
            (topic_slug, movie_name, film_cluster, title, hook, core_thesis, category_lens, scheduled_slot, scheduled_time_iso, youtube_video_id, youtube_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(topic_slug) DO UPDATE SET
                movie_name=excluded.movie_name,
                film_cluster=excluded.film_cluster,
                title=excluded.title,
                hook=excluded.hook,
                core_thesis=excluded.core_thesis,
                category_lens=excluded.category_lens,
                scheduled_slot=excluded.scheduled_slot,
                scheduled_time_iso=excluded.scheduled_time_iso,
                youtube_video_id=COALESCE(excluded.youtube_video_id, completed_topics.youtube_video_id),
                youtube_url=COALESCE(excluded.youtube_url, completed_topics.youtube_url),
                status='COMPLETED'
            """, (
                topic_slug,
                movie_name,
                film_cluster,
                title,
                hook,
                core_thesis,
                category_lens,
                scheduled_slot,
                scheduled_time_iso,
                youtube_video_id,
                youtube_url
            ))
            row_id = cur.lastrowid
            conn.commit()

        self.export_to_json()
        return row_id

    def export_to_json(self):
        """Export database to formatted JSON for clean git tracking and human review."""
        topics = self.get_completed_topics()
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump({
                "database_version": "1.0",
                "total_completed": len(topics),
                "last_updated": datetime.now().isoformat(),
                "topics": topics
            }, f, indent=2)


if __name__ == "__main__":
    db = TopicDatabase()
    db.seed_initial_history()
    completed = db.get_completed_topics()
    print(f"✅ TopicDatabase initialized. Total topics: {len(completed)}")
    for t in completed:
        print(f"  • [{t['movie_name']}] {t['title']} (Slot: {t['scheduled_slot']})")

