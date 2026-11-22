"""
Cinema X-Ray: Production-Grade YouTube Metadata & Packaging Engine
-------------------------------------------------------------------
Generates high-CTR, algorithm-optimized YouTube packaging:
  - 10 multi-angle candidate titles across 4 psychological categories:
      1. Pure Curiosity
      2. Hidden Meaning
      3. Character Psychology & Stakes
      4. Director / Filmmaking Technique
  - Primary title selection adhering to strict YouTube character limits (<70 chars recommended, <=100 strict).
  - Anti-clickbait enforcement (bans generic sensationalism: 'You won\'t believe', 'Shocking', etc.).
  - Rich SEO description with analytical thesis, cast/director credits, and timestamped scene chapters.
  - Multi-tier search tag taxonomy.
  - 3 distinct thumbnail visual concepts with 3-4 word high-contrast overlay copy.
  - Machine-enforceable validation against QualityGate QG-21.
  - Dual export: metadata.json and METADATA.md.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

from pipeline.quality_framework import QualityFramework, QualityGateId, GateResult


BANNED_CLICKBAIT_TERMS = [
    "you won't believe", "you wont believe", "shocking", "mind-blowing",
    "insane trick", "went viral", "this changes everything", "screwed up",
    "omg", "jaw-dropping", "cops called", "gone wrong"
]


@dataclass
class TitleCandidate:
    category: str
    title: str
    char_count: int
    score: float


@dataclass
class ThumbnailConcept:
    concept_id: str
    title: str
    visual_focal_point: str
    text_overlay: str
    color_palette: str
    composition_guide: str


@dataclass
class VideoPackage:
    movie: str
    topic: str
    selected_title: str
    title_candidates: List[TitleCandidate]
    description: str
    tags: List[str]
    thumbnail_concepts: List[ThumbnailConcept]
    chapters: List[Dict[str, Any]]
    category_id: str = "1"  # Film & Animation
    privacy_status: str = "private"


class YouTubeMetadataEngine:
    """Production metadata and packaging generator for Cinema X-Ray videos."""

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = Path(project_dir) if project_dir else None
        self.qf = QualityFramework(self.project_dir)

    def extract_chapters_from_scene_plan(self, scene_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Converts scene plan cuts into YouTube-compatible chapter timestamps."""
        scenes = scene_plan.get("scenes", [])
        if not scenes:
            return [
                {"timestamp": "00:00", "title": "The Hook"},
                {"timestamp": "00:10", "title": "The Hidden Detail"},
                {"timestamp": "00:25", "title": "Psychological Breakdown"},
                {"timestamp": "00:40", "title": "The Masterstroke"}
            ]

        chapters = []
        cum_sec = 0.0

        for i, sc in enumerate(scenes):
            m = int(cum_sec // 60)
            s = int(cum_sec % 60)
            ts_str = f"{m:02d}:{s:02d}"

            raw_title = sc.get("title", f"Scene {i+1}")
            # Clean "Beat X: WORD" to legible label
            clean_title = re.sub(r"^Beat\s*\d+\s*:\s*", "", raw_title).strip()
            if not clean_title:
                clean_title = sc.get("callout", f"Part {i+1}").strip()

            chapters.append({
                "timestamp": ts_str,
                "seconds": round(cum_sec, 2),
                "title": clean_title.title()
            })
            cum_sec += float(sc.get("duration_sec", 3.0))

        # Filter down so chapters are separated by at least 8-10 seconds
        consolidated = []
        last_s = -99.0
        for ch in chapters:
            if ch["seconds"] - last_s >= 8.0:
                consolidated.append(ch)
                last_s = ch["seconds"]

        if not consolidated or consolidated[0]["seconds"] > 0:
            consolidated.insert(0, {"timestamp": "00:00", "seconds": 0.0, "title": "The Revelation"})

        return consolidated

    def generate_candidate_titles(self, movie: str, topic: str, character_or_element: str) -> List[TitleCandidate]:
        """Generates 10 distinct title candidates across 4 psychological categories."""
        cands = [
            # 1. Pure Curiosity
            TitleCandidate(
                category="Pure Curiosity",
                title=f"The {character_or_element} Detail Everyone Missed in {movie} #shorts",
                char_count=len(f"The {character_or_element} Detail Everyone Missed in {movie} #shorts"),
                score=94.0
            ),
            TitleCandidate(
                category="Pure Curiosity",
                title=f"Why Nobody Talks About This {movie} Scene #shorts",
                char_count=len(f"Why Nobody Talks About This {movie} Scene #shorts"),
                score=92.0
            ),
            TitleCandidate(
                category="Pure Curiosity",
                title=f"The Unspoken Rule in {movie} That Changes Everything #shorts",
                char_count=len(f"The Unspoken Rule in {movie} That Changes Everything #shorts"),
                score=90.0
            ),
            # 2. Hidden Meaning
            TitleCandidate(
                category="Hidden Meaning",
                title=f"The Secret Meaning Behind {movie}'s Most Chilling Moment #shorts",
                char_count=len(f"The Secret Meaning Behind {movie}'s Most Chilling Moment #shorts"),
                score=93.0
            ),
            TitleCandidate(
                category="Hidden Meaning",
                title=f"What {movie} Was ACTUALLY Warning Us About #shorts",
                char_count=len(f"What {movie} Was ACTUALLY Warning Us About #shorts"),
                score=91.0
            ),
            TitleCandidate(
                category="Hidden Meaning",
                title=f"The Hidden Visual Clue in {movie} Explained #shorts",
                char_count=len(f"The Hidden Visual Clue in {movie} Explained #shorts"),
                score=89.0
            ),
            # 3. Character Psychology & Stakes
            TitleCandidate(
                category="Character Psychology",
                title=f"The Dark Psychology of {character_or_element} in {movie} #shorts",
                char_count=len(f"The Dark Psychology of {character_or_element} in {movie} #shorts"),
                score=95.0
            ),
            TitleCandidate(
                category="Character Psychology",
                title=f"Why {character_or_element} Was Right All Along in {movie} #shorts",
                char_count=len(f"Why {character_or_element} Was Right All Along in {movie} #shorts"),
                score=92.5
            ),
            # 4. Filmmaking Technique & Narrative Craft
            TitleCandidate(
                category="Filmmaking Technique",
                title=f"How {movie} Uses Pure Visual Storytelling #shorts",
                char_count=len(f"How {movie} Uses Pure Visual Storytelling #shorts"),
                score=88.0
            ),
            TitleCandidate(
                category="Filmmaking Technique",
                title=f"The Masterclass in Subtext Hidden in {movie} #shorts",
                char_count=len(f"The Masterclass in Subtext Hidden in {movie} #shorts"),
                score=87.5
            )
        ]

        # Filter out any accidental clickbait clichés
        valid_cands = []
        for c in cands:
            low = c.title.lower()
            if not any(b in low for b in BANNED_CLICKBAIT_TERMS) and c.char_count <= 100:
                valid_cands.append(c)

        # Sort by score descending
        valid_cands.sort(key=lambda x: x.score, reverse=True)
        return valid_cands

    def generate_thumbnail_concepts(self, movie: str, topic: str, character_or_element: str) -> List[ThumbnailConcept]:
        """Creates 3 distinct high-impact visual thumbnail concepts with 3-4 word text overlays."""
        # Clean 3-4 word overlay text
        words = [w for w in character_or_element.upper().split() if len(w) > 2]
        hook_words = " ".join(words[:2]) if words else "NEVER NOTICED"

        return [
            ThumbnailConcept(
                concept_id="THUMB_01_CHARACTER_CLOSEUP",
                title="Emotional Intensity / Face Breakdown",
                visual_focal_point=f"Ultra-high contrast medium-close frame of {character_or_element} from {movie}, eyes illuminated with rim lighting, background deep desaturated black.",
                text_overlay=f"THE REAL {hook_words[:12]}",
                color_palette="Deep Cinema Amber (#ffb703), Charcoal Black (#101010), Pure White (#FFFFFF)",
                composition_guide="70% central viewport framing. Text locked in top-middle third with drop-shadow to clear bottom YouTube Short UI."
            ),
            ThumbnailConcept(
                concept_id="THUMB_02_VISUAL_PARADOX",
                title="Clashing Elements / Split Contrast",
                visual_focal_point=f"Split-screen or mirrored visual showing the dramatic turning point of {topic}. Left side shows surface perception, right side exposes the underlying truth.",
                text_overlay="HE NEVER EXISTED" if "narrator" in topic.lower() or "tyler" in topic.lower() else "BOTH DIE FIRST",
                color_palette="Electric Cyan (#00e5ff), Blood Crimson (#d90429), High-Contrast White (#FFFFFF)",
                composition_guide="Vertical split down center. High-contrast typography with 12px solid black outline for mobile legibility."
            ),
            ThumbnailConcept(
                concept_id="THUMB_03_SYMBOLIC_DETAIL",
                title="Key Prop / Hidden Cinematic Clue",
                visual_focal_point=f"Tight macro shot of the critical object or clue in {movie} that proves the entire thesis, with dramatic directional lighting.",
                text_overlay="LOOK CLOSER",
                color_palette="Goldenrod (#e5a93c), Midnight Navy (#0a1128), White (#FFFFFF)",
                composition_guide="Tight central object framing with golden 3px viewport border accentuating cinematic detail."
            )
        ]

    def build_package(
        self,
        movie: str,
        topic: str,
        script_text: str,
        director: str = "",
        release_year: str = "",
        cast_members: Optional[List[str]] = None,
        scene_plan: Optional[Dict[str, Any]] = None,
        dossier: Optional[Dict[str, Any]] = None
    ) -> VideoPackage:
        """Assembles the complete metadata and packaging structure."""
        cast_members = cast_members or []
        scene_plan = scene_plan or {}
        dossier = dossier or {}

        # Determine prominent element/character
        elem = topic.split("—")[0].strip() if "—" in topic else topic.split("-")[0].strip()
        elem = re.sub(r"(the\s+|why\s+|how\s+)", "", elem, flags=re.IGNORECASE).strip()

        # Generate titles
        title_cands = self.generate_candidate_titles(movie, topic, elem)
        selected_title = title_cands[0].title if title_cands else f"{movie}: The Untold Truth #shorts"

        # Generate Chapters
        chapters = self.extract_chapters_from_scene_plan(scene_plan)
        chapter_str = "\n".join([f"{ch['timestamp']} - {ch['title']}" for ch in chapters])

        # Generate Tags
        clean_movie_no_col = movie.replace(":", "").replace("'", "")
        tags = [
            clean_movie_no_col,
            movie,
            "Cinema X-Ray",
            "Film Analysis",
            "Movie Breakdown",
            "Cinema Decoded",
            "Screenwriting",
            "Cinematography",
            "Shorts",
            "#Shorts",
            elem
        ]
        if director:
            tags.append(director)
        for act in cast_members[:3]:
            tags.append(act)
        # Deduplicate preserving order
        unique_tags = []
        for t in tags:
            if t and t not in unique_tags:
                unique_tags.append(t)

        # Generate Description
        first_sentence = script_text.strip().split(".")[0] + "." if script_text else f"A deep breakdown of {movie}."
        credit_line = f"Director: {director}" if director else ""
        if release_year:
            credit_line += f" | Year: {release_year}"
        if cast_members:
            credit_line += f" | Starring: {', '.join(cast_members[:3])}"

        description = (
            f"{first_sentence}\n\n"
            f"In this episode of Cinema X-Ray, we dissect {movie} and uncover {topic}. "
            f"Beyond the surface plot lies a masterclass in visual storytelling and character psychology.\n\n"
            f"🎬 CHAPTERS:\n{chapter_str}\n\n"
            f"📌 FILM CREDITS:\n{credit_line if credit_line else movie}\n\n"
            f"Subscribe to Cinema X-Ray for daily frame-by-frame analyses of cinema's greatest masterstrokes.\n\n"
            f"#{clean_movie_no_col.replace(' ', '')} #FilmAnalysis #MovieBreakdown #CinemaXRay #Shorts"
        )

        # Generate Thumbnail Concepts
        thumbnails = self.generate_thumbnail_concepts(movie, topic, elem)

        pkg = VideoPackage(
            movie=movie,
            topic=topic,
            selected_title=selected_title,
            title_candidates=title_cands,
            description=description,
            tags=unique_tags[:20],
            thumbnail_concepts=thumbnails,
            chapters=chapters,
            category_id="1",
            privacy_status="private"
        )

        # Validate with QualityFramework
        self.qf.check_metadata(pkg.selected_title, pkg.description, pkg.tags)
        return pkg

    def export_package(self, pkg: VideoPackage, target_dir: Path) -> Tuple[Path, Path]:
        """Saves metadata.json and METADATA.md to the project directory."""
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Structured metadata.json (Directly compatible with YouTube uploader)
        json_data = {
            "title": pkg.selected_title,
            "topic": pkg.topic,
            "movie": pkg.movie,
            "channel": "Cinema X-Ray",
            "category_id": pkg.category_id,
            "privacy_status": pkg.privacy_status,
            "description": pkg.description,
            "tags": pkg.tags,
            "chapters": pkg.chapters,
            "title_candidates": [asdict(t) for t in pkg.title_candidates],
            "thumbnail_concepts": [asdict(c) for c in pkg.thumbnail_concepts],
            "generated_at": datetime.utcnow().isoformat()
        }
        json_path = target_dir / "metadata.json"
        json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

        # 2. Human-Readable METADATA.md
        md_lines = [
            f"# YouTube Video Package & Metadata: {pkg.movie}",
            f"**Topic**: {pkg.topic}  ",
            f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Category**: Film & Animation (1) | **Target Privacy**: {pkg.privacy_status.upper()}",
            "",
            "---",
            "",
            "## 1. Selected Title",
            f"> `{pkg.selected_title}`",
            f"*Length: {len(pkg.selected_title)} characters (Recommended <70 chars, Max 100)*",
            "",
            "### Candidate Titles by Psychological Angle",
            "| Angle | Candidate Title | Chars | Score |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for t in pkg.title_candidates:
            md_lines.append(f"| {t.category} | {t.title} | {t.char_count} | {t.score:.1f} |")

        md_lines.extend([
            "",
            "---",
            "",
            "## 2. YouTube Video Description",
            "```text",
            pkg.description,
            "```",
            "",
            "---",
            "",
            "## 3. High-Relevance Search Tags",
            f"`{', '.join(pkg.tags)}`",
            "",
            "---",
            "",
            "## 4. High-CTR Thumbnail Concepts",
            ""
        ])

        for c in pkg.thumbnail_concepts:
            md_lines.extend([
                f"### {c.concept_id}: {c.title}",
                f"- **Visual Focal Point**: {c.visual_focal_point}",
                f"- **Text Overlay (Max 3-4 Words)**: `{c.text_overlay}`",
                f"- **Color Palette**: {c.color_palette}",
                f"- **Composition Framing**: {c.composition_guide}",
                ""
            ])

        md_path = target_dir / "METADATA.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        print(f"✅ Generated YouTube metadata package:")
        print(f"   • JSON: {json_path}")
        print(f"   • Markdown: {md_path}")
        return json_path, md_path
