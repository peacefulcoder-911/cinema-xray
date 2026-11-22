"""
Cinema X-Ray: Script Storytelling & Retention Engine
---------------------------------------------------
Implements the Milestone 5 Script Development Framework:
1. Multi-candidate hook generation and objective scoring (QG-07).
2. Retention design via micro-story beats (Hook -> Misconception -> Evidence -> Revelation -> Payoff).
3. Dedicated script evaluation and anti-filler enforcement (QG-06, QG-08, QG-09).
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

REPO_ROOT = Path(__file__).resolve().parent.parent
from pipeline.quality_framework import QualityFramework, QualityGateId


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


class HookCandidate(BaseModel):
    approach: str = Field(description="PARADOX_QUESTION, HIDDEN_CLUE, or CHARACTER_CONTRADICTION")
    text: str = Field(description="The opening hook text (<25 words)")
    score: float = Field(description="Quality score (0-100)")
    is_selected: bool = False


class ScriptEvaluationReport(BaseModel):
    word_count: int
    estimated_duration_sec: float
    hook_score: float
    beats_detected: List[str]
    retention_score: float
    repetition_flags: List[str]
    is_approved: bool
    summary: str


class ScriptStorytellingEngine:
    """Orchestrates retention-engineered script development and objective quality review."""

    def __init__(self):
        _load_env()
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing from environment.")
        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=120000))
        self.qf = QualityFramework()

    def generate_and_rank_hooks(
        self,
        movie_name: str,
        topic_title: str,
        core_thesis: str
    ) -> Tuple[HookCandidate, List[HookCandidate]]:
        """
        Generates 3 distinct hook candidates and selects the highest scoring variant (QG-07).
        """
        prompt = f"""You are a YouTube Retention Specialist for Cinema X-Ray.
Topic: {topic_title}
Movie: {movie_name}
Thesis: {core_thesis}

Write 3 distinct opening hooks (each strictly under 25 words).
Rules:
1. NEVER use generic greetings ('Hey guys', 'Welcome to', 'In this video').
2. Immediately spark intense curiosity, a paradox, or highlight a specific character detail.
3. Must sound natural when spoken aloud.

Return JSON matching:
{{
  "candidates": [
    {{"approach": "PARADOX_QUESTION", "text": "Hook text here..."}},
    {{"approach": "HIDDEN_CLUE", "text": "Hook text here..."}},
    {{"approach": "CHARACTER_CONTRADICTION", "text": "Hook text here..."}}
  ]
}}
"""
        candidates = []
        try:
            res = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.4)
            )
            raw = json.loads(res.text)
            for item in raw.get("candidates", []):
                hook_res = self.qf.evaluate_hook_quality(item["text"])
                candidates.append(HookCandidate(
                    approach=item.get("approach", "GENERAL"),
                    text=item["text"],
                    score=hook_res.score or 75.0
                ))
        except Exception as e:
            print(f"[Script Engine] Note on hook generation: {e}. Using deterministic candidate suite.")
            fallback_hooks = [
                ("PARADOX_QUESTION", f"Notice how in {movie_name}, {topic_title}?"),
                ("HIDDEN_CLUE", f"In {movie_name}, the real secret was hidden in plain sight."),
                ("CHARACTER_CONTRADICTION", f"Why did the filmmaker deliberately hide the truth in {movie_name}?")
            ]
            for app, txt in fallback_hooks:
                hook_res = self.qf.evaluate_hook_quality(txt)
                candidates.append(HookCandidate(
                    approach=app,
                    text=txt,
                    score=hook_res.score or 78.0
                ))

        # Rank candidates by score
        candidates.sort(key=lambda c: c.score, reverse=True)
        best = candidates[0]
        best.is_selected = True

        print(f"[Script Engine] Selected Best Hook ({best.score:.1f}/100 | {best.approach}): \"{best.text}\"")
        return best, candidates

    def evaluate_script(self, script_text: str, video_format: str = "SHORT_45_SEC") -> ScriptEvaluationReport:
        """
        Independent evaluation pass testing script structure, word count, repetition, and retention.
        """
        words = script_text.strip().split()
        wc = len(words)
        est_dur = wc / 2.3  # Average spoken rate: 2.3 words/sec

        # 1. Word count check
        wc_res = self.qf.check_word_count(script_text, video_format)

        # 2. Extract first sentence for hook evaluation
        first_sentence = re.split(r"[.!?]", script_text.strip())[0] + "."
        hook_res = self.qf.evaluate_hook_quality(first_sentence)

        # 3. Micro-story beat detection
        lower = script_text.lower()
        beats_found = []
        if "?" in first_sentence or any(w in first_sentence.lower() for w in ["why", "notice", "how", "what if"]):
            beats_found.append("HOOK_CURIOSITY")
        if any(w in lower for w in ["most people think", "a lot of people", "seems like", "first glance", "now,"]):
            beats_found.append("MISCONCEPTION_CONTEXT")
        if any(w in lower for w in ["because", "actually", "in reality", "the script", "the scene", "notice"]):
            beats_found.append("EVIDENCE_REVEAL")
        if any(w in lower for w in ["felt so", "mind", "psychology", "symbol", "reason", "identity", "choice"]):
            beats_found.append("DEEP_EXPLANATION")
        if any(w in lower for w in ["someone else", "survive", "freedom", "won", "never", "truth"]):
            beats_found.append("PAYOFF_CLIMAX")

        # 4. Repetition & filler check
        banned_fillers = [
            "in this video", "today we are looking at", "make sure to like and subscribe",
            "comment down below", "without further ado", "let's dive in", "as we know"
        ]
        flags = [f"Contains filler: '{b}'" for b in banned_fillers if b in lower]

        # Calculate retention score
        beat_ratio = len(beats_found) / 5.0
        retention_score = min(100.0, (beat_ratio * 50.0) + (hook_res.score * 0.4) + (10.0 if not flags else 0.0))

        approved = wc_res.passed and hook_res.passed and len(beats_found) >= 3 and len(flags) == 0

        report = ScriptEvaluationReport(
            word_count=wc,
            estimated_duration_sec=round(est_dur, 2),
            hook_score=hook_res.score or 0.0,
            beats_detected=beats_found,
            retention_score=round(retention_score, 1),
            repetition_flags=flags,
            is_approved=approved,
            summary="Script approved for production." if approved else f"Script failed gates: {len(flags)} fillers, beats: {len(beats_found)}/5."
        )

        status_sym = "✅" if approved else "❌"
        print(f"[{status_sym}] Script Evaluation: {wc} words (~{est_dur:.1f}s), Retention: {retention_score:.1f}/100, Beats: {len(beats_found)}/5")
        return report
