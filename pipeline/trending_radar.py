"""
Cinema X-Ray: Trending & Release Radar Engine
---------------------------------------------
Implements Upgrade 3:
  - Tracks high-momentum blockbuster trailers, upcoming theatrical releases,
    and cultural anniversaries generating organic search spikes.
  - Automatically boosts topic prioritization for movies in active public awareness.
  - Feeds directly into the Trending Production Mode.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class TrendingRadarItem:
    movie_name: str
    event_type: str        # TRAILER_DROP, UPCOMING_BLOCKBUSTER, VIRAL_RESURGENCE
    release_window: str
    target_director: str
    search_buzz_rating: float  # 0 to 100
    recommended_angle: str
    key_characters: List[str]


ACTIVE_RADAR_ENTRIES: List[TrendingRadarItem] = [
    TrendingRadarItem(
        movie_name="Avengers: Doomsday",
        event_type="UPCOMING_BLOCKBUSTER",
        release_window="May 2026",
        target_director="Anthony & Joe Russo",
        search_buzz_rating=99.5,
        recommended_angle="Doctor Doom wearing Tony Stark's face as a psychological weapon against the Avengers",
        key_characters=["Doctor Doom", "Thor", "Reed Richards", "Doctor Strange"]
    ),
    TrendingRadarItem(
        movie_name="The Batman: Part II",
        event_type="UPCOMING_BLOCKBUSTER",
        release_window="October 2026",
        target_director="Matt Reeves",
        search_buzz_rating=96.0,
        recommended_angle="Gotham's Court of Owls architecture and the corruption of the Wayne legacy",
        key_characters=["Bruce Wayne / Batman", "The Penguin", "Jim Gordon", "Court of Owls"]
    ),
    TrendingRadarItem(
        movie_name="Spider-Man: Brand New Day",
        event_type="UPCOMING_BLOCKBUSTER",
        release_window="July 2026",
        target_director="Destin Daniel Cretton",
        search_buzz_rating=97.0,
        recommended_angle="Peter Parker completely isolated with zero Stark tech and zero allies",
        key_characters=["Peter Parker / Spider-Man", "Daredevil", "Kraven"]
    ),
    TrendingRadarItem(
        movie_name="GTA VI",
        event_type="TRAILER_DROP",
        release_window="Fall 2025/2026",
        target_director="Sam Houser / Rockstar",
        search_buzz_rating=100.0,
        recommended_angle="Cinematic Bonnie & Clyde tragedy and social media satire in Leonida",
        key_characters=["Lucia", "Jason"]
    ),
    TrendingRadarItem(
        movie_name="Dune: Messiah",
        event_type="UPCOMING_BLOCKBUSTER",
        release_window="December 2026",
        target_director="Denis Villeneuve",
        search_buzz_rating=94.5,
        recommended_angle="Paul Atreides realizing he cannot stop the 61-billion-death Holy War he started",
        key_characters=["Paul Atreides / Muad'Dib", "Chani", "Irulan", "Alia"]
    ),
    TrendingRadarItem(
        movie_name="Oppenheimer",
        event_type="VIRAL_RESURGENCE",
        release_window="Award & Streaming Milestone",
        target_director="Christopher Nolan",
        search_buzz_rating=92.0,
        recommended_angle="The final conversation between Einstein and Oppenheimer: the world already destroyed",
        key_characters=["J. Robert Oppenheimer", "Albert Einstein", "Lewis Strauss"]
    )
]


class TrendingRadar:
    """Detects and ranks upcoming trending films and active trailer releases."""

    def __init__(self):
        self.radar_items = ACTIVE_RADAR_ENTRIES

    def get_radar_summary(self) -> List[Dict[str, Any]]:
        """Returns sorted list of current high-buzz movies."""
        sorted_items = sorted(self.radar_items, key=lambda x: x.search_buzz_rating, reverse=True)
        return [asdict(item) for item in sorted_items]

    def is_trending_movie(self, movie_name: str) -> Tuple[bool, Optional[TrendingRadarItem]]:
        """Checks if a film is currently tracking on the radar."""
        clean_name = re.sub(r"\s*\(\d{4}\)", "", movie_name).strip().lower()
        for item in self.radar_items:
            if item.movie_name.lower() in clean_name or clean_name in item.movie_name.lower():
                return True, item
        return False, None
