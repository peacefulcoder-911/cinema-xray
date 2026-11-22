# CINEMA X-RAY — PRODUCTION QUALITY STANDARDS & QUALITY GATES
**Document Version:** 1.0  
**Enforcement Level:** MANDATORY & MACHINE-ENFORCED  
**Architecture Reference:** `pipeline/quality_framework.py`

---

## 1. QUALITY PHILOSOPHY & CORE PRINCIPLES

Cinema X-Ray produces high-retention, high-revelation cinema analysis videos. Every production must pass strict, non-negotiable quality gates.

1. **Binary Critical Gates:** Critical quality gates are strictly binary. A numerical score cannot compensate for factual inaccuracy, audio clipping, subtitle desynchronization, corrupted rendering, or missing assets.
2. **Machine Enforcement:** Standards must be validated programmatically by Python and media inspection tools (`ffprobe`, AST/regex parsing, acoustic alignment, volume measurement), not merely prompt instructions.
3. **Fail-Fast Architecture:** Any critical gate failure immediately halts production, logs a structured error report, and triggers bounded recovery before downstream resources are consumed.
4. **Verbatim Narration Integrity:** Approved scripts are immutable. Zero unapproved sentences, filler words, or omitted words.
5. **Audience-Centric Engagement:** Content must provide genuine intellectual or psychological insight into filmmaking, avoiding generic summaries or artificial clickbait.

---

## 2. THE 23 PRODUCTION QUALITY GATES MATRIX

| Gate # | Quality Gate Name | Evaluation Target | Verification Mode | Critical / Binary? | Proceed on Failure? | Correction Protocol |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QG-01** | **Topic Selection** | Topic eligibility, uniqueness, curiosity, audience relevance | Automated + DB | **YES (Binary)** | **NO** | Select alternate unproduced topic from catalog |
| **QG-02** | **Duplicate Prevention** | Slug, title, thesis deduplication against historic & active jobs | Automated (SQLite/JSON) | **YES (Binary)** | **NO** | Abort or generate non-colliding slug & angle |
| **QG-03** | **Research Quality** | Breadth of analysis, director choices, scene references | Automated + AI | Non-Critical | Conditional | Expand dossier with additional research queries |
| **QG-04** | **Fact Verification** | Scene existence, character actions, quotes, timestamps | Automated + AI | **YES (Binary)** | **NO** | Strip unverified claim or reject topic |
| **QG-05** | **Originality & Thesis** | Central analytical insight beyond surface plot summary | Automated + AI | **YES (Binary)** | **NO** | Re-prompt analytical lens with contrarian angle |
| **QG-06** | **Script Structure** | Required beat sequence (Hook, Context, Evidence, Reveal, Payoff) | Automated (AST/Regex) | **YES (Binary)** | **NO** | Re-structure script into required beats |
| **QG-07** | **Hook Score** | Opening 3 seconds curiosity gap, intrigue, clarity (>80/100) | Automated Evaluator | **YES (Binary)** | **NO** | Generate 3 hook variants; select highest scoring |
| **QG-08** | **Viewer Retention** | Open loops, escalation, elimination of repetitive exposition | Automated Evaluator | **YES (Binary)** | **NO** | Tighten script, prune filler sentences |
| **QG-09** | **Word Count & Pacing** | Word count bounds (Shorts: 90-135 words; Long: 750-950 words) | Automated | **YES (Binary)** | **NO** | Re-compile script to exact word limit |
| **QG-10** | **Visual Storyboard** | Line-by-line visual purpose, camera motion, scene pacing | Automated Schema | **YES (Binary)** | **NO** | Regenerate scene plan with required beat durations |
| **QG-11** | **Asset Selection** | Asset-to-beat semantic relevance, zero generic filler | Automated + Schema | Non-Critical | Conditional | Fallback to verified movie promotional footage |
| **QG-12** | **Footage Integrity** | File existence, valid MP4/MKV, duration $>10\text{s}$, res $\ge 1080\text{p}$ | Automated (`ffprobe`) | **YES (Binary)** | **NO** | Trigger re-download or alternate clip search |
| **QG-13** | **Framing Compliance** | 70% active viewport (`1080x1344` @ Y=288), ambient blur | Automated (FFmpeg) | **YES (Binary)** | **NO** | Re-encode with verified filtergraph coordinates |
| **QG-14** | **Voice Synthesis** | Brian voice (`nPczCjzI2devNBz1zQrb`), no missing words, no cuts | Automated (`ffprobe`/hash) | **YES (Binary)** | **NO** | Re-synthesize via ElevenLabs with locked voice ID |
| **QG-15** | **Audio Mastering** | Broadcast EQ (75Hz/320Hz/9kHz), Peak $\le -1.0\text{ dBFS}$, zero clip | Automated (`volumedetect`)| **YES (Binary)** | **NO** | Re-normalize audio with linear gain & EBU R128 |
| **QG-16** | **Subtitle Accuracy** | Acoustic word alignment, zero negative timestamps, bounds | Automated (`faster-whisper`)| **YES (Binary)** | **NO** | Re-align with faster-whisper acoustic model |
| **QG-17** | **Subtitle Styling** | Arc Cyan (`#00FFFF`), dark box background, vertical Y=340 | Automated (ASS parser)| **YES (Binary)** | **NO** | Regenerate ASS headers from master template |
| **QG-18** | **Render Validation** | Video readable, duration matches audio $\pm 0.6\text{s}$, zero black frame | Automated (`ffprobe`/keyframe)| **YES (Binary)** | **NO** | Re-render composition with clean timeline |
| **QG-19** | **Super-Resolution 8K** | Resolution $4320\times 7680$, HEVC codec, bitrate $\ge 40\text{ Mbps}$ | Automated (`ffprobe`) | Non-Critical (Fallback)| Conditional | Fallback to CPU libx265 or deliver 1080p |
| **QG-20** | **Thumbnail Packaging**| $1080\times 1920$, size $<2\text{MB}$, high contrast text, focal point | Automated (PIL/file) | **YES (Binary)** | **NO** | Re-extract keyframe, re-render typography badge |
| **QG-21** | **Metadata Accuracy** | Title $<100$ chars, description $<5000$ chars, verified chapters | Automated Validator | **YES (Binary)** | **NO** | Re-generate metadata adhering to YouTube bounds |
| **QG-22** | **Upload Security** | Safe privacy status (`private`/`unlisted`), valid YouTube ID | Automated API | **YES (Binary)** | **NO** | Retry upload with exponential backoff |
| **QG-23** | **Final Delivery QC** | 8-frame visual audit, JSON production report, DB commitment | Automated Inspector | **YES (Binary)** | **NO** | Block release; mark production state `BLOCKED` |

---

## 3. DETAILED GATE SPECIFICATIONS

### QG-01 & QG-02: Topic Selection & Duplicate Prevention
- **Evaluated:** Topic uniqueness, film catalog freshness, title/slug collision.
- **Passing Standard:**
  1. `topic_slug` does not exist in `completed_topics.db` or `completed_topics.json`.
  2. `movie_name` has not been featured in the past 3 consecutive production days.
  3. `topic_status` is not currently in `RESERVED` state by another worker process.
- **Action on Failure:** Worker releases lock and queries next eligible candidate.

### QG-07: Hook Quality & Scoring
- **Evaluated:** The first 3 to 5 seconds of spoken narration.
- **Scoring Rubric (100 Points Total):**
  - *Curiosity Gap (30 pts):* Creates an unanswered psychological or narrative question.
  - *Specificity (25 pts):* Mentions specific characters, scenes, or cinematic elements (no vague generalities).
  - *Immediate Relevance (20 pts):* No greetings ("Hey guys"), no channel introductions ("Welcome to Cinema X-Ray").
  - *Viewer Promise (15 pts):* Promises a concrete revelation or discovery.
  - *Clarity & Brevity (10 pts):* Spoken under 7 seconds ($\le 20$ words).
- **Passing Standard:** $\ge 80/100$.

### QG-14 & QG-15: Voice & Audio Standards
- **Narrator Profile:** Brian (`nPczCjzI2devNBz1zQrb`).
- **Broadcast Sweetening EQ:**
  - $75\text{ Hz}$ High-Pass Filter ($18\text{ dB/oct}$) to eliminate low rumble.
  - $320\text{ Hz}$ Parametric Notch ($Q=1.2$, $-2.5\text{ dB}$) to remove nasal mud and boxiness.
  - $9.0\text{ kHz}$ High-Shelf ($+2.0\text{ dB}$) for airy broadcast presence.
- **Mastering Loudness:**
  - Integrated Loudness: $-14.0\text{ LUFS} \pm 1.0\text{ LUFS}$.
  - True Peak: $\le -1.0\text{ dBFS}$ (Zero digital clipping).
  - Forbidden Sound Design: Zero whoosh, swoosh, swish, riser, sweep, or reverse cymbal SFX.
  - Zero synthetic drone or pink noise bed in final vocal mix.

### QG-16 & QG-17: Subtitle Synchronization & Styling
- **Acoustic Alignment Engine:** `faster-whisper` forced acoustic word-level timestamps.
- **Styling Architecture (ASS Format):**
  - Font: Futura / Arial Bold, Size: 70pt.
  - Placement: Centered horizontally, bottom margin $Y=340\text{px}$ (above Shorts UI controls).
  - Colors: Active Word `#00FFFF` (Arc Cyan glow), Inactive Words `#FFFFFF` (Pure White).
  - Shadow: Hard black double drop-shadow (`0 4px 16px rgba(0,0,0,0.95)`).
- **Passing Standard:** No overlapping events, no subtitle duration $> 4.0\text{s}$, no line wrapping exceeding 32 characters per line.

### QG-18: Render Validation & Media Integrity
- **Dimensions:** $1080\times 1920$ (9:16 vertical).
- **Viewport Framing:** $1080\times 1344$ active viewport placed at $Y=288\text{px}$, framed with 2px golden divider lines (`#ffb703`) at $Y=287$ and $Y=1632$.
- **Background:** Gaussian blur ($r=35$) with $-8\%$ brightness and $+15\%$ contrast.
- **Audio-Video Sync:** Video duration matches audio duration within $\pm 0.6\text{s}$. Zero truncated audio.

---

## 4. PERSISTENT VALIDATION IMPLEMENTATION
All 23 gates are executed programmatically via `QualityFramework` in `pipeline/quality_framework.py`. Results are serialized into `qc_report.json` for every production.
