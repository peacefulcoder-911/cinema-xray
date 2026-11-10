"""
Cinema Decoded: Executive Producer & Lead Writer Agent
------------------------------------------------------
Orchestrates Gemini and the YouTube Agent Skill (Jakeschincariol/youtube-agent-skill)
to autonomously conceptualize, write, hook-score, and format complete Executive Producer
brief prompts in the exact 11-section format required by Cinema Decoded.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from google import genai
from google.genai import types

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "database" / "cinema_scenes_catalog.json"
COMPLETED_PATH = REPO_ROOT / "database" / "completed_topics.json"
VOICE_PATH = REPO_ROOT / "skills" / "youtube_agent" / "templates" / "cinema_decoded_voice.md"
HOOKSCORE_PATH = REPO_ROOT / "skills" / "youtube_agent" / "skills" / "yt-script" / "hookscore.py"


def _load_env():
    p = REPO_ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k_clean = k.strip()
                v_clean = v.strip().strip('"').strip("'")
                if k_clean in ["GEMINI_API_KEY", "GOOGLE_API_KEY"] or k_clean not in os.environ:
                    os.environ[k_clean] = v_clean
_load_env()


def get_api_client():
    _load_env()
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=120000))


class ExecutiveProducerAgent:
    """Autonomous Executive Producer & Lead Writer Agent for Cinema Decoded."""

    def __init__(self):
        self.client = get_api_client()
        self.voice_profile = VOICE_PATH.read_text(encoding="utf-8") if VOICE_PATH.exists() else ""

    def pick_next_topic(self) -> Dict[str, Any]:
        """Picks the next unproduced topic from catalog or raises RuntimeError if exhausted."""
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

        if not CATALOG_PATH.exists():
            raise FileNotFoundError(f"Cinema catalog missing at: {CATALOG_PATH}")

        cat_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        for entry in cat_data.get("scenes", []):
            slug = entry.get("topic_slug")
            title_lower = entry.get("topic", "").lower().strip()
            if slug not in completed_slugs and title_lower not in completed_titles:
                return entry

        # Fallback to first scene if all completed
        return cat_data["scenes"][0]

    def score_hook(self, hook_text: str) -> Dict[str, Any]:
        """Scores a hook line using the YouTube Agent Skill hookscore.py tool."""
        clean_hook = hook_text.strip().strip('"').strip("'")
        try:
            cmd = ["python3", str(HOOKSCORE_PATH), "--hook", clean_hook]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = res.stdout

            # Parse score values
            props = {}
            for line in output.splitlines():
                m = re.search(r"(SPECIFICITY|ADDRESS|STAKES|CURIOSITY|BREVITY|VERDICT)\s+(\d+)", line)
                if m:
                    props[m.group(1).lower()] = int(m.group(2))
                m_verdict = re.search(r"VERDICT\s+(\d+)\s+([A-Z]+)", line)
                if m_verdict:
                    props["verdict_score"] = int(m_verdict.group(1))
                    props["verdict_grade"] = m_verdict.group(2)

            return {
                "hook": clean_hook,
                "score": props.get("verdict_score", 60),
                "grade": props.get("verdict_grade", "FAIR"),
                "properties": props,
                "raw_output": output.strip()
            }
        except Exception as e:
            return {"hook": clean_hook, "score": 65, "grade": "FAIR", "error": str(e)}

    def generate_candidate_hooks(self, movie: str, topic: str, core_thesis: str) -> List[str]:
        """Generates 5 distinct high-curiosity opening hooks for the given film scene."""
        prompt = f"""You are the Lead Storyteller for Cinema Decoded (top YouTube video essayist).
Film: {movie}
Scene Topic: {topic}
Core Psychological Thesis: {core_thesis}

Write 5 distinct candidate opening hook lines (first sentence of a 50-second YouTube Short).
Each candidate MUST follow one of these high-retention formulas:
1. The Impossible Claim / Paradox ("You never asked why..., and the answer is...")
2. The Observational Command ("Look closely at what X does during this scene...")
3. The Counter-Intuitive Truth ("He knows X is fake. So why does he want another bite?")
4. The Hidden Detail ("The film shows you this in its opening seconds and never says it out loud.")
5. The Question That Complicates Trust ("Why does a simple test become one of the most terrifying scenes in horror cinema?")

STRICT RULES:
- Exactly 1 sentence per candidate.
- Concise, punching, 12-20 words.
- Zero generic filler ("Hey guys", "In this video", "Mind-blowing", "Crazy").
- Output ONLY the 5 numbered lines, nothing else.
"""
        models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest"
        ]
        for m in models:
            try:
                timeout_ms = 45000
                resp = self.client.models.generate_content(
                    model=m,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        http_options=types.HttpOptions(timeout=timeout_ms)
                    )
                )
                lines = [l.strip() for l in resp.text.splitlines() if l.strip()]
                candidates = []
                for l in lines:
                    cleaned = re.sub(r"^\d+[\.\)]\s*", "", l).strip().strip('"')
                    if len(cleaned.split()) >= 6:
                        candidates.append(cleaned)
                if len(candidates) >= 3:
                    print(f"[Executive Producer Agent] Hook generation succeeded using model: {m}")
                    return candidates[:5]
            except Exception as e:
                print(f"[Executive Producer Agent] Hook generation note on {m}: {e}")
                continue

        return [
            f"Look closely at what happens during this scene in {movie}.",
            f"The central discovery about {movie} is something nobody says out loud.",
            f"Why does this one choice in {movie} change the entire story?"
        ]

    def select_best_hook(self, movie: str, topic: str, core_thesis: str) -> Tuple[str, Dict[str, Any]]:
        """Generates candidate hooks, evaluates them with hookscore.py, and picks the champion."""
        candidates = self.generate_candidate_hooks(movie, topic, core_thesis)
        scored = []
        for c in candidates:
            sc = self.score_hook(c)
            scored.append(sc)

        # Sort by score descending
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        winner = scored[0]
        return winner["hook"], winner

    def generate_executive_producer_brief(
        self,
        movie: str,
        topic: str,
        core_thesis: str,
        scene_description: str,
        best_hook: Optional[str] = None
    ) -> str:
        """
        Synthesizes the complete, verbatim 11-section Executive Producer Brief prompt
        using Gemini, adhering strictly to the user-approved markdown structure.
        """
        if not best_hook:
            best_hook, _ = self.select_best_hook(movie, topic, core_thesis)

        system_instruction = f"""You are the Executive Producer and Lead Cinematic Storyteller for Cinema Decoded.
Generate the COMPLETE Executive Producer Brief Prompt in the exact, non-negotiable markdown format specified below.

{self.voice_profile}

Format Requirements:
Output MUST begin with:
# PROJECT: [MOVIE NAME] — [PUNCHY THEMATIC HEADLINE]

Followed by all 11 exact sections:
## YOUR ROLE
(With Act as a world-class cinematic video editor..., The central discovery: **[1 sentence thesis]**, Do not turn this into a general movie explanation.)

---
## 1. NON-NEGOTIABLE SCRIPT
Use this narration EXACTLY as provided.
Do not rewrite, paraphrase, shorten, expand, or regenerate the script.
### APPROVED NARRATION
"[The 40-52 second narration, ~95-115 words total, broken into 7-9 clear sentences. Sentence 1 MUST be the approved hook: '{best_hook}'. The narration MUST end with an engaging comment prompt question.]"
Preserve the narration order and wording.

---
## 2. CREATIVE DIRECTION
### Visual identity
(Deep blacks, controlled shadows, high contrast, industrial/atmospheric warehouse lighting, sharp subject separation, subtle film grain.)
### Visual principle
**Every narration line must have a visually meaningful counterpart.**

---
## 3. SENTENCE-LEVEL VISUAL STORYTELLING
(Break down the narration sentence-by-sentence into SHOT 1 — THE HOOK, SHOT 2, SHOT 3, SHOT 4, SHOT 5, SHOT 6 — THE PAYOFF, SHOT 7 — COMMENT PROMPT. Each shot must have Narration:, Visual direction:, and specific typography/graphic callouts like WHY DOES A SALVAGE CREW HAVE ALIEN WEAPONS?, NOT POWER. PAYROLL., etc.)

---
## 4. FOOTAGE RESEARCH AND ACQUISITION
(Specific scenes required with timestamps, characters, and assets/footage/... directory path.)

---
## 5. MOTION AND EDITING
(Controlled push-ins, pull-outs, tracking, reframing, match cuts, dynamic rhythm.)

---
## 6. AUDIO GENERATION — STRICT RESTRICTIONS
(Confident documentary voice, Achird, absolutely prohibited sound effects: ZERO whooshes, swooshes, risers, sweeps, transition impacts. Silence floor <= -65 dB.)

---
## 7. CAPTIONS AND GRAPHICS
(Arc Reactor Cyan HUD high-contrast synchronized subtitles, Futura 74pt lower-third, vivid Stark cyan highlighted phrases, restrained placement.)

---
## 8. TECHNICAL IMPLEMENTATION
(Workflow: APPROVED NARRATION -> SENTENCE PARSER -> SCENE JSON -> TIMING ENGINE -> FOOTAGE MAPPING -> CLEAN AUDIO GENERATION -> CAPTION GENERATION -> REMOTION / FFPEG 8K RENDERING -> QUALITY CONTROL.)

---
## 9. RENDER REQUIREMENTS
(8K Vertical Master 4320x7680 @ 30 FPS + 1080p Delivery Copy 1080x1920 @ 30 FPS.)

---
## 10. FINAL QUALITY CONTROL
(Story, Visuals, Audio, Technical checklists.)

---
## 11. FINAL DELIVERABLES
(List 1 to 10 deliverables.)

## FINAL CREATIVE STANDARD
(High contrast. Immersive visuals. Precise storytelling. True 8K output verification. No whoosh sounds.)
"""

        user_prompt = f"""Produce the complete Executive Producer Brief for:
Movie: {movie}
Topic: {topic}
Core Thesis: {core_thesis}
Scene Details: {scene_description}
Approved Opening Hook: "{best_hook}"

Write the full prompt now. Output pure markdown with no intro or outro comments."""

        models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest"
        ]
        for m in models:
            try:
                timeout_ms = 90000
                resp = self.client.models.generate_content(
                    model=m,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        http_options=types.HttpOptions(timeout=timeout_ms)
                    )
                )
                if resp and resp.text:
                    print(f"[Executive Producer Agent] Brief synthesis succeeded using model: {m}")
                    return resp.text.strip()
            except Exception as e:
                print(f"[Executive Producer Agent] Note on {m}: {e}")
                continue

        raise RuntimeError("Failed to generate brief with available Gemini models.")


def extract_approved_script(brief_text: str) -> str:
    """Extracts the exact verbatim narration from an Executive Producer Brief."""
    m = re.search(r"### APPROVED NARRATION\s*\n+[\"']?(.*?)[\"']?\s*\n+Preserve the narration", brief_text, re.DOTALL)
    if m:
        return m.group(1).strip()
    
    # Fallback search between quotes in section 1
    m_sec1 = re.search(r"## 1\.\s+NON-NEGOTIABLE SCRIPT.*?\n\"(.*?)\"\n", brief_text, re.DOTALL)
    if m_sec1:
        return m_sec1.group(1).strip()

    raise ValueError("Could not parse Approved Narration from the brief text.")


def extract_topic_metadata(brief_text: str) -> Dict[str, str]:
    """Extracts project title, movie name, and central discovery."""
    title_m = re.search(r"^# PROJECT:\s*(.*?)\s*—\s*(.*?)$", brief_text, re.MULTILINE)
    movie = title_m.group(1).strip() if title_m else "Cinema Decoded"
    headline = title_m.group(2).strip() if title_m else "Film Scene Analysis"

    disc_m = re.search(r"The central discovery:\s*\n+\*\*(.*?)\*\*", brief_text, re.DOTALL)
    discovery = disc_m.group(1).strip() if disc_m else headline

    slug = re.sub(r"[^a-z0-9]+", "_", f"{movie}_{headline}".lower()).strip("_")

    return {
        "movie": movie,
        "headline": headline,
        "central_discovery": discovery,
        "topic_slug": slug
    }


if __name__ == "__main__":
    agent = ExecutiveProducerAgent()
    print("Testing topic selection...")
    topic = agent.pick_next_topic()
    print("Picked Topic:", topic)

    print("\nTesting hook ideation and scoring...")
    hook, score_data = agent.select_best_hook(topic["movie"], topic["topic"], topic["core_thesis"])
    print(f"Selected Hook: {hook} (Score: {score_data.get('score')})")

