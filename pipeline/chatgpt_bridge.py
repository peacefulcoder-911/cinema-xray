"""
Cinema Decoded: ChatGPT Conversation Bridge & Universal Prompt Parser
=====================================================================
Connects to ChatGPT shared conversations (chatgpt.com/share/<id>) and OpenAI API,
extracts conversation history, parses director briefs, locked narration scripts,
and formats them for AutonomousProductionEngine.
"""

import os
import re
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

REPO_ROOT = Path(__file__).resolve().parent.parent

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
}


class ChatGPTBridge:
    """Bridges ChatGPT shared links & OpenAI API into the Cinema Decoded pipeline."""

    def __init__(self, share_url: Optional[str] = None):
        self.share_url = share_url

    @staticmethod
    def extract_share_id(url_or_id: str) -> str:
        """Extracts the UUID share ID from a ChatGPT share URL or returns it directly."""
        m = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", url_or_id)
        if m:
            return m.group(1)
        return url_or_id.strip()

    def fetch_shared_conversation(self, url_or_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches the complete conversation tree and linear messages from chatgpt.com backend API.
        """
        target = url_or_id or self.share_url
        if not target:
            raise ValueError("No ChatGPT share URL or share ID provided.")

        share_id = self.extract_share_id(target)
        api_url = f"https://chatgpt.com/backend-api/share/{share_id}"

        resp = requests.get(api_url, headers=HEADERS, timeout=25)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch ChatGPT share (HTTP {resp.status_code}): {resp.text[:200]}")

        return resp.json()

    def get_linear_messages(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts clean ordered messages (role + text) from the API payload."""
        messages = []
        linear = data.get("linear_conversation", [])

        for idx, item in enumerate(linear):
            msg = item.get("message")
            if not msg:
                continue
            role = msg.get("author", {}).get("role", "unknown")
            content = msg.get("content", {})
            parts = content.get("parts", [])
            text_parts = [p for p in parts if isinstance(p, str)]
            full_text = "\n".join(text_parts).strip()
            if full_text:
                messages.append({
                    "index": idx,
                    "id": msg.get("id"),
                    "role": role,
                    "text": full_text,
                    "create_time": msg.get("create_time")
                })

        return messages

    def find_latest_script_or_prompt(self, url_or_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Scans backwards through the conversation to find the latest assistant response
        containing either a full director prompt, an approved script block, or a movie breakdown.
        """
        data = self.fetch_shared_conversation(url_or_id)
        messages = self.get_linear_messages(data)
        
        # Walk backwards through assistant messages
        for idx in range(len(messages) - 1, -1, -1):
            msg = messages[idx]
            if msg["role"] != "assistant":
                continue
            text = msg["text"]
            
            # Also check if previous assistant message in the same turn provides context (like Movie name)
            prev_context = ""
            if idx > 0 and messages[idx-1]["role"] == "assistant":
                prev_context = messages[idx-1]["text"] + "\n\n"
            
            parsed = self.parse_prompt_or_script(prev_context + text)
            if parsed and parsed.get("script_text"):
                parsed["source_message_id"] = msg.get("id")
                parsed["conversation_title"] = data.get("title")
                parsed["share_id"] = self.extract_share_id(url_or_id or self.share_url)
                return parsed

        raise ValueError("Could not find any viable production script or director prompt in the conversation.")

    def parse_prompt_or_script(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Universal parser capable of extracting:
        1. Full 14-section or 11-section Antigravity Director Prompts
        2. WritingBlock / XML document scripts
        3. Hook / Evidence / Revelation / Payoff formats
        4. Standard Markdown movie breakdown posts
        """
        # 1. Clean up ChatGPT artifact formatting wrappers (e.g. :::writing{...}, <WritingBlock...>, <badge...>)
        clean_text = re.sub(r":::writing\{[^}]*\}", "", text)
        clean_text = re.sub(r":::", "", clean_text)
        
        # Check for <WritingBlock id="...">...</WritingBlock>
        wb_match = re.search(r"<WritingBlock[^>]*>(.*?)</WritingBlock>", clean_text, re.DOTALL)
        script_candidate = None
        if wb_match:
            script_candidate = wb_match.group(1).strip()

        # Check for ### APPROVED SCRIPT or ## 2. APPROVED NARRATION or ## 2. EXACT NARRATION
        if not script_candidate:
            m_app = re.search(r"### APPROVED SCRIPT\s*\n+[\"']?(.*?)[\"']?(?=\n+#|\n+##|\n+Preserve|\Z)", clean_text, re.DOTALL)
            if m_app:
                script_candidate = m_app.group(1).strip()

        if not script_candidate:
            m_exact = re.search(r"## 2\.\s+EXACT NARRATION.*?\n+[\"']?(.*?)[\"']?(?=\n+#|\n+##|\n+Generate|\Z)", clean_text, re.DOTALL)
            if m_exact:
                script_candidate = m_exact.group(1).strip()

        if not script_candidate:
            m_sec2 = re.search(r"## 2\.\s+APPROVED NARRATION — LOCKED.*?\n+(.*?)(?=\n+#|\n+##|\n+Preserve|\Z)", clean_text, re.DOTALL)
            if m_sec2:
                # Could be sub-sections HOOK, EVIDENCE, REVELATION, PAYOFF
                sub_blocks = re.findall(r"###\s+[A-Z\s]+\n+[\"']?(.*?)[\"']?(?=\n+###|\Z)", m_sec2.group(1), re.DOTALL)
                if sub_blocks:
                    script_candidate = "\n\n".join([b.strip().strip('"').strip("'") for b in sub_blocks if b.strip()])
                else:
                    script_candidate = m_sec2.group(1).strip()

        # Extract Movie Title
        movie = "Cinema Decoded"
        m_movie = re.search(r"\*\*Movie:\*\*\s*(.*?)(?:\n|\r|\*|$)", clean_text)
        if m_movie:
            movie = m_movie.group(1).strip()
        else:
            m_trend = re.search(r"##\s*Trending topic:\s*([A-Za-z0-9\s:’'-]+?)(?:\s*—|\s*\(|\s*\n|$)", clean_text)
            if m_trend:
                movie = m_trend.group(1).strip()
            else:
                m_proj = re.search(r"^#\s*(?:PROJECT:\s*)?(.*?)\s*—\s*(.*?)$", clean_text, re.MULTILINE)
                if m_proj:
                    movie = m_proj.group(1).strip()
                else:
                    m_film = re.search(r"##\s*([A-Za-z0-9\s:’'-]+?)(?:\s*—|\s*\(|\s*\n)", clean_text)
                    if m_film:
                        movie = m_film.group(1).strip()

        # Clean movie name if it has markdown formatting or prefixes
        movie = re.sub(r"^[#\s*]+", "", movie)
        movie = re.sub(r"Trending topic:\s*", "", movie, flags=re.IGNORECASE).strip()

        # Extract Video Title / Headline
        headline = "Movie Breakdown"
        m_title = re.search(r"\*\*Video Title:\*\*\s*(.*?)(?:\n|\r|\*|$)", clean_text)
        if m_title:
            headline = m_title.group(1).strip()
        else:
            m_t2 = re.search(r"\*\*Title:\s*(.*?)\*\*", clean_text)
            if m_t2:
                headline = m_t2.group(1).strip()
            elif m_proj:
                headline = m_proj.group(2).strip()

        # Extract Concept / Central Discovery
        disc = headline
        m_disc = re.search(r"\*\*Short concept:\*\*\s*(.*?)(?:\n|\r|$)", clean_text)
        if m_disc:
            disc = m_disc.group(1).strip()
        else:
            m_disc2 = re.search(r"\*\*Concept:\*\*\s*(.*?)(?:\n|\r|$)", clean_text)
            if m_disc2:
                disc = m_disc2.group(1).strip()

        if not script_candidate:
            return None

        # Clean quotes and unwanted lines from script
        clean_script = script_candidate.replace('"', "").strip()
        # Remove markdown bold/italics
        clean_script = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean_script)
        clean_script = re.sub(r"\*([^*]+)\*", r"\1", clean_script)

        # Generate topic slug
        slug_raw = f"{movie}_{headline}".lower()
        slug = re.sub(r"[^a-z0-9]+", "_", slug_raw).strip("_")[:50]

        return {
            "movie": movie,
            "headline": headline,
            "central_discovery": disc,
            "topic_slug": slug,
            "script_text": clean_script,
            "raw_text": text
        }


if __name__ == "__main__":
    url = "https://chatgpt.com/share/6af91b43-5120-83e8-846e-2888ec4e2a77"
    bridge = ChatGPTBridge(url)
    print("Testing ChatGPT bridge fetch from shared conversation...")
    res = bridge.find_latest_script_or_prompt()
    print("\n✅ Successfully extracted script!")
    print(f"🎬 Movie:    {res['movie']}")
    print(f"📌 Headline: {res['headline']}")
    print(f"💡 Slug:     {res['topic_slug']}")
    print(f"📝 Script ({len(res['script_text'].split())} words):\n{res['script_text']}")
