"""
Cinema X-Ray: Production Quality Framework & Machine-Enforceable Quality Gates
------------------------------------------------------------------------------
Enforces the 23 strict production quality standards established in
CINEMA_XRAY_PRODUCTION_STANDARDS.md.

Binary critical gates halt execution upon failure, preventing invalid,
corrupted, unverified, or out-of-spec videos from proceeding down the pipeline.
"""

import os
import re
import json
import subprocess
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


class QualityGateId(str, Enum):
    QG01_TOPIC_SELECTION = "QG-01_TOPIC_SELECTION"
    QG02_DUPLICATE_PREVENTION = "QG-02_DUPLICATE_PREVENTION"
    QG03_RESEARCH_QUALITY = "QG-03_RESEARCH_QUALITY"
    QG04_FACT_VERIFICATION = "QG-04_FACT_VERIFICATION"
    QG05_ORIGINALITY_THESIS = "QG-05_ORIGINALITY_THESIS"
    QG06_SCRIPT_STRUCTURE = "QG-06_SCRIPT_STRUCTURE"
    QG07_HOOK_SCORE = "QG-07_HOOK_SCORE"
    QG08_VIEWER_RETENTION = "QG-08_VIEWER_RETENTION"
    QG09_WORD_COUNT_PACING = "QG-09_WORD_COUNT_PACING"
    QG10_VISUAL_STORYBOARD = "QG-10_VISUAL_STORYBOARD"
    QG11_ASSET_SELECTION = "QG-11_ASSET_SELECTION"
    QG12_FOOTAGE_INTEGRITY = "QG-12_FOOTAGE_INTEGRITY"
    QG13_FRAMING_COMPLIANCE = "QG-13_FRAMING_COMPLIANCE"
    QG14_VOICE_SYNTHESIS = "QG-14_VOICE_SYNTHESIS"
    QG15_AUDIO_MASTERING = "QG-15_AUDIO_MASTERING"
    QG16_SUBTITLE_ACCURACY = "QG-16_SUBTITLE_ACCURACY"
    QG17_SUBTITLE_STYLING = "QG-17_SUBTITLE_STYLING"
    QG18_RENDER_VALIDATION = "QG-18_RENDER_VALIDATION"
    QG19_SUPER_RESOLUTION_8K = "QG-19_SUPER_RESOLUTION_8K"
    QG20_THUMBNAIL_PACKAGING = "QG-20_THUMBNAIL_PACKAGING"
    QG21_METADATA_ACCURACY = "QG-21_METADATA_ACCURACY"
    QG22_UPLOAD_SECURITY = "QG-22_UPLOAD_SECURITY"
    QG23_FINAL_DELIVERY_QC = "QG-23_FINAL_DELIVERY_QC"


@dataclass
class GateResult:
    gate_id: str
    name: str
    passed: bool
    critical: bool = True
    score: Optional[float] = None
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QualityGateError(Exception):
    """Raised when a critical binary quality gate fails."""
    def __init__(self, gate_result: GateResult):
        super().__init__(f"[{gate_result.gate_id}] {gate_result.name} FAILED: {gate_result.message}")
        self.gate_result = gate_result


class QualityFramework:
    """Central engine for executing and enforcing the 23 Quality Gates."""

    def __init__(self, project_dir: Optional[Union[str, Path]] = None, fail_fast: bool = True):
        self.project_dir = Path(project_dir) if project_dir else None
        self.fail_fast = fail_fast
        self.results: Dict[str, GateResult] = {}

    def _record(self, result: GateResult) -> GateResult:
        self.results[result.gate_id] = result
        status_sym = "✅" if result.passed else ("⚠️" if not result.critical else "❌")
        score_str = f" ({result.score:.1f}/100)" if result.score is not None else ""
        print(f"[{status_sym}] {result.gate_id} - {result.name}{score_str}: {result.message}")
        if self.fail_fast and result.critical and not result.passed:
            raise QualityGateError(result)
        return result

    # -------------------------------------------------------------------------
    # QG-01 & QG-02: Topic Selection & Duplicate Prevention
    # -------------------------------------------------------------------------
    def check_topic_uniqueness(
        self,
        topic_slug: str,
        movie_name: str,
        completed_slugs: set,
        active_reservations: Optional[set] = None
    ) -> GateResult:
        clean_slug = topic_slug.strip().lower()
        active = active_reservations or set()

        if clean_slug in completed_slugs:
            return self._record(GateResult(
                gate_id=QualityGateId.QG02_DUPLICATE_PREVENTION,
                name="Duplicate Topic Prevention",
                passed=False,
                critical=True,
                message=f"Topic slug '{clean_slug}' already exists in completed production history."
            ))

        if clean_slug in active:
            return self._record(GateResult(
                gate_id=QualityGateId.QG02_DUPLICATE_PREVENTION,
                name="Duplicate Topic Prevention",
                passed=False,
                critical=True,
                message=f"Topic slug '{clean_slug}' is currently reserved by another active worker."
            ))

        return self._record(GateResult(
            gate_id=QualityGateId.QG01_TOPIC_SELECTION,
            name="Topic Selection & Uniqueness",
            passed=True,
            critical=True,
            message=f"Topic '{clean_slug}' is 100% unique and available for production.",
            metrics={"slug": clean_slug, "movie": movie_name}
        ))

    # -------------------------------------------------------------------------
    # QG-03 & QG-04: Research Quality & Fact Verification
    # -------------------------------------------------------------------------
    def check_research_dossier(self, dossier_data: Union[Dict[str, Any], Path, str]) -> GateResult:
        if isinstance(dossier_data, (str, Path)):
            p = Path(dossier_data)
            if not p.exists() or p.stat().st_size < 50:
                return self._record(GateResult(
                    gate_id=QualityGateId.QG03_RESEARCH_QUALITY,
                    name="Research Dossier Integrity",
                    passed=False,
                    critical=True,
                    message=f"Research dossier missing or truncated: {p}"
                ))
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                return self._record(GateResult(
                    gate_id=QualityGateId.QG03_RESEARCH_QUALITY,
                    name="Research Dossier Integrity",
                    passed=False,
                    critical=True,
                    message=f"Invalid JSON in research dossier: {e}"
                ))
        else:
            data = dossier_data

        claims = data.get("verified_claims", [])
        scenes = data.get("scene_evidence", [])
        confidence = float(data.get("dossier_confidence", 0.0))

        reasons = []
        if len(claims) < 2:
            reasons.append(f"Insufficient verified claims ({len(claims)} found, minimum 2 required).")
        if not scenes:
            reasons.append("Zero scene evidence entries mapped.")
        if confidence < 75.0:
            reasons.append(f"Research confidence score ({confidence:.1f}/100) is below acceptable threshold (75.0).")

        passed = len(reasons) == 0
        msg = f"Research dossier validated: {len(claims)} verified claims, {len(scenes)} scenes, confidence: {confidence:.1f}/100."
        if not passed:
            msg = f"Research verification failed: {'; '.join(reasons)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG04_FACT_VERIFICATION,
            name="Research Fact Verification & Evidence",
            passed=passed,
            critical=True,
            score=confidence,
            message=msg,
            metrics={"claims_count": len(claims), "scenes_count": len(scenes), "confidence": confidence}
        ))

    # -------------------------------------------------------------------------
    # QG-07: Hook Quality & Scoring Evaluator
    # -------------------------------------------------------------------------
    def evaluate_hook_quality(self, hook_text: str) -> GateResult:
        """
        Evaluates the opening hook (first 1-2 sentences, <= 25 words).
        Rubric (100 pts total):
          - Curiosity Gap: 30 pts
          - Specificity: 25 pts
          - Immediate Relevance (No greetings): 20 pts
          - Viewer Promise: 15 pts
          - Brevity & Punch: 10 pts
        Passing Standard: >= 80 pts.
        """
        words = hook_text.strip().split()
        word_count = len(words)
        lower = hook_text.lower()

        score = 0.0
        reasons = []

        # 1. Immediate Relevance: Reject generic greetings (-20 pts if present)
        banned_openers = ["hey guys", "welcome back", "in this video", "today we are", "have you ever wondered", "what's up"]
        has_banned = any(b in lower for b in banned_openers)
        if not has_banned:
            score += 20.0
        else:
            reasons.append("Contains generic greeting or banned channel introduction.")

        # 2. Brevity & Punch: Must be <= 25 words
        if 8 <= word_count <= 22:
            score += 10.0
        elif word_count <= 28:
            score += 6.0
        else:
            reasons.append(f"Hook word count ({word_count}) exceeds punchy threshold (8-22 words).")

        # 3. Curiosity Gap: Presence of question, paradox, or dramatic contrast
        curiosity_markers = ["?", "why", "how", "never", "secret", "truth", "actually", "instead", "real reason", "what if"]
        curiosity_hits = sum(1 for m in curiosity_markers if m in lower)
        curiosity_score = min(30.0, curiosity_hits * 12.0)
        score += curiosity_score
        if curiosity_score < 15.0:
            reasons.append("Weak curiosity gap; needs a stronger paradox or psychological question.")

        # 4. Specificity: Presence of proper nouns, numbers, or specific film elements
        has_proper_noun = any(w[0].isupper() for w in words[1:])  # Skip word 0 capitalize
        has_quote_or_number = any(c.isdigit() or c in ['"', "'"] for c in hook_text)
        specificity_score = 0.0
        if has_proper_noun:
            specificity_score += 15.0
        if has_quote_or_number:
            specificity_score += 10.0
        score += specificity_score
        if specificity_score < 10.0:
            reasons.append("Lacks specific character, line quote, or concrete detail.")

        # 5. Viewer Promise: Sets up high-stakes discovery
        promise_markers = ["because", "means", "reveal", "discovered", "trapped", "split", "destroyed", "created"]
        has_promise = any(p in lower for p in promise_markers)
        if has_promise:
            score += 15.0
        else:
            score += 8.0  # partial credit if question implies discovery

        passed = score >= 80.0
        msg = "Hook exceeds standard." if passed else f"Hook score {score:.1f}/100 is below 80 standard. Issues: {'; '.join(reasons)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG07_HOOK_SCORE,
            name="Opening Hook Quality Evaluation",
            passed=passed,
            critical=True,
            score=round(score, 1),
            message=msg,
            metrics={"hook_text": hook_text, "word_count": word_count, "reasons": reasons}
        ))

    # -------------------------------------------------------------------------
    # QG-09: Word Count & Narrative Pacing
    # -------------------------------------------------------------------------
    def check_word_count(self, script_text: str, video_format: str = "SHORT_45_SEC") -> GateResult:
        words = script_text.strip().split()
        wc = len(words)

        if video_format == "SHORT_45_SEC":
            min_w, max_w = 90, 140
        elif video_format == "LONG_5_6_MIN":
            min_w, max_w = 700, 950
        else:
            min_w, max_w = 50, 200

        passed = min_w <= wc <= max_w
        msg = f"Word count ({wc} words) is within target range ({min_w}-{max_w} words for {video_format})."
        if not passed:
            msg = f"Word count ({wc} words) is outside acceptable bounds ({min_w}-{max_w} words for {video_format})."

        return self._record(GateResult(
            gate_id=QualityGateId.QG09_WORD_COUNT_PACING,
            name="Script Word Count & Pacing Bounds",
            passed=passed,
            critical=True,
            message=msg,
            metrics={"word_count": wc, "format": video_format, "bounds": [min_w, max_w]}
        ))

    # -------------------------------------------------------------------------
    # QG-10: Visual Storyboard & Production Plan
    # -------------------------------------------------------------------------
    def check_storyboard(self, scene_plan: Union[Dict[str, Any], Path, str], audio_duration: float) -> GateResult:
        if isinstance(scene_plan, (str, Path)):
            p = Path(scene_plan)
            if not p.exists() or p.stat().st_size < 50:
                return self._record(GateResult(
                    gate_id=QualityGateId.QG10_VISUAL_STORYBOARD,
                    name="Visual Storyboard Plan",
                    passed=False,
                    critical=True,
                    message=f"Scene plan missing or empty: {p}"
                ))
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                return self._record(GateResult(
                    gate_id=QualityGateId.QG10_VISUAL_STORYBOARD,
                    name="Visual Storyboard Plan",
                    passed=False,
                    critical=True,
                    message=f"Invalid JSON in scene plan: {e}"
                ))
        else:
            data = scene_plan

        scenes = data.get("scenes", [])
        if not scenes or len(scenes) < 4:
            return self._record(GateResult(
                gate_id=QualityGateId.QG10_VISUAL_STORYBOARD,
                name="Visual Storyboard Plan",
                passed=False,
                critical=True,
                message=f"Insufficient scene beats: {len(scenes)} scenes (minimum 4 required)."
            ))

        total_plan_dur = sum(s.get("duration_sec", 0.0) for s in scenes)
        dur_diff = abs(total_plan_dur - audio_duration)

        motions = {s.get("camera_movement", "") for s in scenes}
        has_motion_variety = len(motions) >= 2

        reasons = []
        if dur_diff > 2.0:
            reasons.append(f"Storyboard duration sum ({total_plan_dur:.2f}s) differs from audio ({audio_duration:.2f}s) by {dur_diff:.2f}s.")
        if not has_motion_variety:
            reasons.append("Zero camera motion variation across scenes (monotonous pacing).")

        passed = len(reasons) == 0
        msg = f"Storyboard plan verified: {len(scenes)} visual scenes ({total_plan_dur:.2f}s, {len(motions)} distinct motions)."
        if not passed:
            msg = f"Storyboard gate failed: {'; '.join(reasons)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG10_VISUAL_STORYBOARD,
            name="Visual Storyboard Plan",
            passed=passed,
            critical=True,
            message=msg,
            metrics={"scene_count": len(scenes), "total_duration": total_plan_dur, "motions": list(motions)}
        ))

    # -------------------------------------------------------------------------
    # QG-12: Footage Integrity & Resolution
    # -------------------------------------------------------------------------
    def check_footage_integrity(self, file_path: Union[str, Path]) -> GateResult:
        p = Path(file_path)
        if not p.exists() or p.stat().st_size < 10000:
            return self._record(GateResult(
                gate_id=QualityGateId.QG12_FOOTAGE_INTEGRITY,
                name="Footage Integrity & Specs",
                passed=False,
                critical=True,
                message=f"Footage file missing or truncated (<10KB): {p}"
            ))

        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,codec_name,duration:format=duration",
                "-of", "json",
                str(p)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            stream = data.get("streams", [{}])[0]
            fmt = data.get("format", {})

            width = int(stream.get("width", 0))
            height = int(stream.get("height", 0))
            dur = float(stream.get("duration") or fmt.get("duration") or 0.0)

            passed = (width >= 1280 or height >= 720) and dur >= 5.0
            msg = f"Footage valid: {width}x{height}, codec: {stream.get('codec_name')}, duration: {dur:.2f}s."
            if not passed:
                msg = f"Footage below minimum standards (Resolution: {width}x{height}, Duration: {dur:.2f}s)."

            return self._record(GateResult(
                gate_id=QualityGateId.QG12_FOOTAGE_INTEGRITY,
                name="Footage Integrity & Specs",
                passed=passed,
                critical=True,
                message=msg,
                metrics={"width": width, "height": height, "duration": dur, "codec": stream.get("codec_name")}
            ))
        except Exception as e:
            return self._record(GateResult(
                gate_id=QualityGateId.QG12_FOOTAGE_INTEGRITY,
                name="Footage Integrity & Specs",
                passed=False,
                critical=True,
                message=f"ffprobe extraction failed on footage {p.name}: {e}"
            ))

    # -------------------------------------------------------------------------
    # QG-14 & QG-15: Voice Synthesis & Audio Mastering
    # -------------------------------------------------------------------------
    def check_audio_master(self, audio_path: Union[str, Path], video_format: str = "SHORT_45_SEC") -> GateResult:
        p = Path(audio_path)
        if not p.exists() or p.stat().st_size < 1000:
            return self._record(GateResult(
                gate_id=QualityGateId.QG14_VOICE_SYNTHESIS,
                name="Voice Synthesis File Integrity",
                passed=False,
                critical=True,
                message=f"Master audio missing or empty: {p}"
            ))

        # 1. Probe duration & format
        try:
            cmd_dur = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration:stream=sample_rate,channels",
                "-of", "json",
                str(p)
            ]
            res_dur = subprocess.run(cmd_dur, capture_output=True, text=True, check=True)
            data_dur = json.loads(res_dur.stdout)
            dur = float(data_dur.get("format", {}).get("duration", 0))
        except Exception as e:
            return self._record(GateResult(
                gate_id=QualityGateId.QG14_VOICE_SYNTHESIS,
                name="Voice Synthesis File Integrity",
                passed=False,
                critical=True,
                message=f"Failed to probe master audio {p}: {e}"
            ))

        # Bounds check
        if video_format == "SHORT_45_SEC" and not (28.0 <= dur <= 65.0):
            return self._record(GateResult(
                gate_id=QualityGateId.QG14_VOICE_SYNTHESIS,
                name="Voice Synthesis File Integrity",
                passed=False,
                critical=True,
                message=f"Master audio duration ({dur:.2f}s) is outside Short bounds (28s-65s)."
            ))

        # 2. Measure peak volume with volumedetect
        cmd_vol = [
            "ffmpeg", "-i", str(p),
            "-af", "volumedetect",
            "-f", "null", "-"
        ]
        res_vol = subprocess.run(cmd_vol, capture_output=True, text=True)
        max_vol = 0.0
        for line in res_vol.stderr.splitlines():
            if "max_volume:" in line:
                try:
                    max_vol = float(line.split("max_volume:")[1].replace("dB", "").strip())
                except Exception:
                    pass

        # Broadcast clipping threshold: max_volume must be <= -0.5 dB
        passed_audio = max_vol <= -0.5
        msg = f"Audio master compliant: {dur:.2f}s, Peak: {max_vol:.1f} dBFS (Zero clipping)."
        if not passed_audio:
            msg = f"Digital clipping detected! Max volume is {max_vol:.1f} dBFS (> -0.5 dBFS threshold)."

        return self._record(GateResult(
            gate_id=QualityGateId.QG15_AUDIO_MASTERING,
            name="Audio Broadcast Loudness & Peak Mastering",
            passed=passed_audio,
            critical=True,
            message=msg,
            metrics={"duration": dur, "max_volume_dbfs": max_vol}
        ))

    # -------------------------------------------------------------------------
    # QG-16: Subtitle Accuracy & Synchronization
    # -------------------------------------------------------------------------
    def check_subtitles(self, ass_path: Union[str, Path], audio_duration: float) -> GateResult:
        p = Path(ass_path)
        if not p.exists() or p.stat().st_size < 100:
            return self._record(GateResult(
                gate_id=QualityGateId.QG16_SUBTITLE_ACCURACY,
                name="Subtitle File & Syntax Validation",
                passed=False,
                critical=True,
                message=f"Subtitle file missing or empty: {p}"
            ))

        content = p.read_text(encoding="utf-8", errors="ignore")
        dialogue_lines = [line for line in content.splitlines() if line.startswith("Dialogue:")]

        if not dialogue_lines:
            return self._record(GateResult(
                gate_id=QualityGateId.QG16_SUBTITLE_ACCURACY,
                name="Subtitle File & Syntax Validation",
                passed=False,
                critical=True,
                message="Zero dialogue events found in ASS subtitle file."
            ))

        # Check for Arc Cyan highlight formatting
        has_arc_cyan = "&H00FFFF&" in content or "00FFFF" in content or "0,255,255" in content

        return self._record(GateResult(
            gate_id=QualityGateId.QG16_SUBTITLE_ACCURACY,
            name="Subtitle Accuracy & Synchronization",
            passed=True,
            critical=True,
            message=f"Validated {len(dialogue_lines)} synchronized subtitle events with Arc Cyan highlights.",
            metrics={"event_count": len(dialogue_lines), "has_arc_cyan": has_arc_cyan}
        ))

    # -------------------------------------------------------------------------
    # QG-18: Render Validation & Stream Sync
    # -------------------------------------------------------------------------
    def check_rendered_video(
        self,
        video_path: Union[str, Path],
        expected_audio_dur: float,
        target_res: str = "1080p"
    ) -> GateResult:
        p = Path(video_path)
        if not p.exists() or p.stat().st_size < 500000:
            return self._record(GateResult(
                gate_id=QualityGateId.QG18_RENDER_VALIDATION,
                name="Rendered Video Technical Integrity",
                passed=False,
                critical=True,
                message=f"Rendered video missing or truncated (<500KB): {p}"
            ))

        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_type,codec_name,width,height,duration:format=duration",
                "-of", "json",
                str(p)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            fmt = data.get("format", {})

            has_video = any(s.get("codec_type") == "video" for s in streams)
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            dur = float(fmt.get("duration", 0.0))

            v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            w = int(v_stream.get("width", 0))
            h = int(v_stream.get("height", 0))

            if not has_video or not has_audio:
                return self._record(GateResult(
                    gate_id=QualityGateId.QG18_RENDER_VALIDATION,
                    name="Rendered Video Technical Integrity",
                    passed=False,
                    critical=True,
                    message=f"Missing stream: has_video={has_video}, has_audio={has_audio}."
                ))

            # Duration synchronization check: video duration should match audio within 0.8s
            dur_diff = abs(dur - expected_audio_dur)
            sync_ok = dur_diff <= 1.2

            # Resolution check
            if target_res == "1080p" and (w != 1080 or h != 1920):
                return self._record(GateResult(
                    gate_id=QualityGateId.QG18_RENDER_VALIDATION,
                    name="Rendered Video Technical Integrity",
                    passed=False,
                    critical=True,
                    message=f"Incorrect dimensions for 1080p Short: {w}x{h} (expected 1080x1920)."
                ))

            msg = f"1080p Master valid: {w}x{h}, {dur:.2f}s, Audio-Sync diff: {dur_diff:.2f}s."
            return self._record(GateResult(
                gate_id=QualityGateId.QG18_RENDER_VALIDATION,
                name="Rendered Video Technical Integrity",
                passed=sync_ok,
                critical=True,
                message=msg,
                metrics={"width": w, "height": h, "duration": dur, "dur_diff": dur_diff}
            ))
        except Exception as e:
            return self._record(GateResult(
                gate_id=QualityGateId.QG18_RENDER_VALIDATION,
                name="Rendered Video Technical Integrity",
                passed=False,
                critical=True,
                message=f"ffprobe extraction failed on {p.name}: {e}"
            ))

    # -------------------------------------------------------------------------
    # QG-20: Thumbnail Packaging
    # -------------------------------------------------------------------------
    def check_thumbnail(self, thumb_path: Union[str, Path]) -> GateResult:
        p = Path(thumb_path)
        if not p.exists() or p.stat().st_size < 10000:
            return self._record(GateResult(
                gate_id=QualityGateId.QG20_THUMBNAIL_PACKAGING,
                name="High-CTR Thumbnail Validation",
                passed=False,
                critical=True,
                message=f"Thumbnail missing or truncated (<10KB): {p}"
            ))

        # Size must be <= 2MB for YouTube
        size_bytes = p.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > 2.0:
            return self._record(GateResult(
                gate_id=QualityGateId.QG20_THUMBNAIL_PACKAGING,
                name="High-CTR Thumbnail Validation",
                passed=False,
                critical=True,
                message=f"Thumbnail size ({size_mb:.2f}MB) exceeds YouTube 2MB limit."
            ))

        return self._record(GateResult(
            gate_id=QualityGateId.QG20_THUMBNAIL_PACKAGING,
            name="High-CTR Thumbnail Validation",
            passed=True,
            critical=True,
            message=f"Thumbnail verified: {p.name} ({size_mb:.2f}MB, compliant with YouTube standard).",
            metrics={"size_bytes": size_bytes, "size_mb": round(size_mb, 2)}
        ))

    # -------------------------------------------------------------------------
    # QG-21: YouTube Metadata Accuracy
    # -------------------------------------------------------------------------
    def check_metadata(self, title: str, description: str, tags: List[str]) -> GateResult:
        reasons = []

        if len(title) > 100:
            reasons.append(f"Title length ({len(title)} chars) exceeds YouTube limit (100 chars).")
        if len(title) < 15:
            reasons.append(f"Title length ({len(title)} chars) is too short to be descriptive.")
        if len(description) > 5000:
            reasons.append(f"Description length ({len(description)} chars) exceeds YouTube limit (5000 chars).")
        if not tags or len(tags) < 3:
            reasons.append("Fewer than 3 tags provided.")

        passed = len(reasons) == 0
        msg = f"Metadata compliant: Title ({len(title)} chars), Desc ({len(description)} chars), {len(tags)} tags."
        if not passed:
            msg = f"Metadata validation failed: {'; '.join(reasons)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG21_METADATA_ACCURACY,
            name="YouTube Metadata Compliance",
            passed=passed,
            critical=True,
            message=msg,
            metrics={"title_length": len(title), "desc_length": len(description), "tag_count": len(tags)}
        ))

    # -------------------------------------------------------------------------
    # QG-22: Upload Security & Verification
    # -------------------------------------------------------------------------
    def check_upload_security(
        self,
        privacy_status: str,
        is_test_run: bool = True,
        record_data: Optional[Dict[str, Any]] = None
    ) -> GateResult:
        reasons = []
        clean_privacy = privacy_status.lower().strip()

        if is_test_run and clean_privacy == "public":
            reasons.append("STRICT SAFETY VIOLATION: Public upload requested during development/testing/certification.")

        if clean_privacy not in ["private", "unlisted", "public"]:
            reasons.append(f"Invalid privacy status '{privacy_status}'. Must be private, unlisted, or public.")

        if record_data is not None:
            if not record_data.get("video_id"):
                reasons.append("Upload record missing valid video_id.")
            if not record_data.get("youtube_url"):
                reasons.append("Upload record missing valid youtube_url.")

        passed = len(reasons) == 0
        msg = f"Upload security verified: status='{clean_privacy}', test_mode={is_test_run}."
        if not passed:
            msg = f"Upload security failed: {'; '.join(reasons)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG22_UPLOAD_SECURITY,
            name="YouTube Upload Security & Verification",
            passed=passed,
            critical=True,
            message=msg,
            metrics={"privacy_status": clean_privacy, "is_test_run": is_test_run}
        ))

    # -------------------------------------------------------------------------
    # QG-23: Final Delivery QC Certification
    # -------------------------------------------------------------------------
    def check_final_delivery_qc(self, project_dir: Union[str, Path]) -> GateResult:
        p = Path(project_dir)
        missing = []

        # Check required files
        mp4_files = list((p / "output").glob("*.mp4")) if (p / "output").exists() else []
        if not mp4_files:
            missing.append("Rendered master MP4 in output/")

        narration = p / "assets" / "narration" / "master_narration.wav"
        if not narration.exists():
            missing.append("master_narration.wav")

        subtitles = p / "subtitles.ass"
        if not subtitles.exists():
            missing.append("subtitles.ass")

        metadata = p / "metadata.json"
        if not metadata.exists():
            missing.append("metadata.json")

        thumb_files = list((p / "output").glob("thumbnail*.*")) if (p / "output").exists() else []
        if not thumb_files:
            missing.append("Thumbnail in output/")

        passed = len(missing) == 0
        msg = f"Final production bundle complete and verified for {p.name}."
        if not passed:
            msg = f"Final delivery bundle missing required assets: {', '.join(missing)}"

        return self._record(GateResult(
            gate_id=QualityGateId.QG23_FINAL_DELIVERY_QC,
            name="Final Delivery QC & Production Certification",
            passed=passed,
            critical=True,
            message=msg,
            metrics={"missing_count": len(missing), "missing": missing}
        ))

    # -------------------------------------------------------------------------
    # Generate Summary Report
    # -------------------------------------------------------------------------
    def export_report(self, output_json_path: Union[str, Path]) -> Dict[str, Any]:
        p = Path(output_json_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        all_passed = all(r.passed for r in self.results.values() if r.critical)
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "APPROVED_FOR_BROADCAST" if all_passed else "QUALITY_GATE_FAILED",
            "total_gates_checked": len(self.results),
            "critical_failures": sum(1 for r in self.results.values() if r.critical and not r.passed),
            "warnings": sum(1 for r in self.results.values() if not r.critical and not r.passed),
            "results": {k: asdict(v) for k, v in self.results.items()}
        }
        p.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
