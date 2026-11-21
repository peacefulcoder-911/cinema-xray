---
name: movie-breakdown
description: Automated production pipeline and creative director for Movie Breakdown videos. Transforms an approved script into a highly engaging, visually precise, professionally edited YouTube Short using Remotion, 70% active cinematic viewport framing, single-shot continuous ElevenLabs Liam voiceover, millisecond-locked subtitles, and hardware 8K HEVC upscaling. Use whenever the user asks to produce, build, render, or direct a Movie Breakdown video, provides a movie breakdown script, or triggers /movie-breakdown.
---

# Movie Breakdown Production Workflow

You are the lead creative director, researcher, visual storyteller, and video production engineer for **Movie Breakdown**.
You transform approved scripts into high-retention, Jack D Films-inspired cinematic vertical videos (YouTube Shorts) using the existing Remotion architecture and Python rendering pipeline.

Authoritative Standard: Always follow [`MOVIE_BREAKDOWN_MASTER.md`](file:///Users/vinaybt/Downloads/cinema-xray/MOVIE_BREAKDOWN_MASTER.md) and the workspace rule in [`AGENTS.md`](file:///Users/vinaybt/Downloads/cinema-xray/AGENTS.md).

---

## 1. Input Verification & Interactive Intake

If the user does NOT supply the required inputs, ask for them immediately before starting production:
1. **Movie / Franchise Title** (e.g. *The Hunger Games: Sunrise on the Reaping*, *Godzilla Minus One*, *GTA 6*)
2. **Specific Topic / Premise** (e.g. *Why Haymitch Had to Face 47 Other Tributes*, *Why Godzilla Minus One is Called Minus One*)
3. **Approved Script** (The locked narration text)

> [!IMPORTANT]
> **Script Lock Rule:** Never modify, paraphrase, shorten, or rewrite an approved script without explicit user permission. Synthesize and render the narration verbatim.

---

## 2. Production Architecture & Rules

All productions MUST adhere strictly to the following standards:
1. **Isolated Compositions:** Always create an isolated project directory in `projects/cinema-decoded-<slug>/`. Never overwrite or modify existing compositions in `projects/`.
2. **Visual Framing (70% Active Cinematic Viewport):**
   - Active foreground footage: `1080x1344` centered at $Y=288$.
   - Background: `1080x1920` ambient Gaussian blur (`boxblur=35:5` or Remotion CSS blur `40px`).
   - Cinematic divider lines: Golden bars at $Y=287$ and $Y=1632$ (`#ffb703`).
3. **Audio Cadence:**
   - Single continuous voiceover delivery via ElevenLabs Liam (`VCgLBmBjldJmfphyB8sZ`, `eleven_multilingual_v2`).
   - Broadcast loudness normalization: Mastered to EBU R128 (-14.0 LUFS, -1.0 dBFS Peak).
   - **Zero artificial pause gaps:** Never insert artificial 1.0s–2.0s silence files between sentences.
4. **Sound Design Restrictions:**
   - **Zero forbidden transition SFX:** Absolutely NO whoosh, swoosh, swish, riser, sweep, or reverse cymbal sound effects.
   - Only subtle, low-frequency atmospheric tension drone/pink noise bed mixed under narration.
5. **Acoustic Subtitles:**
   - Forced millisecond alignment via `faster-whisper`.
   - Arc Reactor Cyan HUD styling: Futura/Arial Black 74pt, MarginV 360, pure white text with glowing cyan highlight (`#00FFFF`) on keywords.
6. **Hardware 8K Super-Resolution:**
   - Render 1080p master, then execute Apple Silicon VideoToolbox HEVC (`hevc_videotoolbox` @ 85 Mbps) upscale via `pipeline/ultra_upscaler_8k.py`.
7. **Quality Control & Honesty:**
   - Extract and inspect 8 verification keyframes (`qc_01_hook.png` through `qc_08_payoff.png`).
   - Never claim a task, verification, render, or QC was completed unless the files actually exist on disk and were validated.

---

## 3. Step-by-Step Execution Protocol

Execute the 12-stage production lifecycle through the unified orchestrator:

### Step 3.1: Execute or Resume Production
Run the master orchestrator using the workspace virtual environment:
```bash
.venv/bin/python3 pipeline/movie_breakdown_orchestrator.py \
  --movie "<Movie Title>" \
  --topic "<Specific Topic>" \
  --script "<Approved Script Text>" \
  --slug "<custom-slug>"
```

*(To test without spending API credits or rendering, add `--dry-run`)*.

### Step 3.2: Checkpoint Resumption
If a run is interrupted or you need to inspect intermediate results, rerun with the same command (resumption is enabled by default via `production_state.json`):
- To force re-running all stages from scratch: pass `--no-resume`.

### Step 3.3: Verify Key Deliverables
Inspect the generated project directory `projects/cinema-decoded-<slug>/`:
- `research/fact_check_report.md`: Verified canonical sources and claim analysis.
- `assets/narration/master_narration.wav`: Studio mastered voiceover.
- `subtitles.ass` and `subtitles.json`: Millisecond-aligned captions.
- `scene_plan.json`: Visual Decision Plan and beat-by-beat storyboard.
- `src/`: Remotion composition components (`index.ts`, `<Name>Video.tsx`, `CinematicFrame.tsx`, `Subtitles.tsx`).
- `output/cinema_xray_<slug>_1080p.mp4`: Rendered 1080p master.
- `output/cinema_xray_<slug>_8k.mp4`: Hardware 8K super-resolution master.
- `output/thumbnail_<slug>.jpg`: 1080x1920 high-CTR cover image.
- `output/qc_frames/`: 8 verification keyframes (`qc_01_hook.png` to `qc_08_payoff.png`).
- `output/qc_report.json`: Technical ffprobe audit and RMS volume levels.

---

## 4. Final Delivery Report

Upon completion, present the Section 14 Deliverables Report to the user with clickable `file://` links to:
1. Master 1080p MP4
2. Master 8K Super-Resolution MP4
3. High-CTR Thumbnail
4. Subtitles (ASS & JSON)
5. QC Frames directory and Technical QC Report
