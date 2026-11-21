# MOVIE BREAKDOWN — SECTION 14 DELIVERABLES & FINAL QC REPORT

## 1. PROJECT IDENTIFICATION
- **Movie / Franchise:** Fight Club
- **Specific Topic:** The Real Reason the Narrator Never Has a Name
- **Project Slug:** `cinema-decoded-fight-club-narrator-no-name`
- **Production Engine:** Remotion + Studio Python Pipeline
- **Visual Identity:** 70% Active Cinematic Viewport with Ambient Blurred Background

---

## 2. PRODUCTION STATUS & DELIVERABLES
| Asset Type | Resolution | Format | Verified File Path |
| :--- | :--- | :--- | :--- |
| **1080p Master** | 1080x1920 | MP4 (H.264) | [`cinema_xray_fight-club-narrator-no-name_1080p.mp4`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/output/cinema_xray_fight-club-narrator-no-name_1080p.mp4) |
| **8K Super-Res** | 4320x7680 | MP4 (HEVC) | [`cinema_xray_fight-club-narrator-no-name_8k.mp4`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/output/cinema_xray_fight-club-narrator-no-name_8k.mp4) |
| **Master Voiceover**| 48kHz Mono | WAV (PCM 16-bit) | [`master_narration.wav`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/assets/narration/master_narration.wav) |
| **Subtitles (ASS)** | 1080x1920 | ASS (Arc Cyan) | [`subtitles.ass`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/subtitles.ass) |
| **Subtitles (JSON)**| Time-stamped | JSON (Cards) | [`subtitles.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/subtitles.json) |
| **High-CTR Cover**  | 1080x1920 | JPG (High-Q) | [`thumbnail_fight-club-narrator-no-name.jpg`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/output/thumbnail_fight-club-narrator-no-name.jpg) |
| **Scene Storyboard**| Beat-by-Beat | JSON | [`scene_plan.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/scene_plan.json) |
| **Remotion Source** | 9:16 React | TSX / Remotion | [`src`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/src) |
| **QC Report**       | Multi-point | JSON | [`qc_report.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/output/qc_report.json) |

---

## 3. TECHNICAL SPECIFICATIONS & QC AUDIT
- **Total Master Duration:** 46.97 seconds
- **Frame Rate:** 30.000 FPS (Constant)
- **Active Framing:** 1080x1344 (70% screen height @ Y=288)
- **Audio Peak:** -5.10 dBFS (Broadcast compliant, zero digital clipping)
- **Audio Mean:** -21.40 dBFS
- **Sound Design Restrictions:** 100% COMPLIANT (Zero whoosh, swoosh, swish, riser, sweep, or cymbal SFX)
- **Acoustic Cadence:** Single-shot continuous Liam narration (Zero artificial pause gaps)
- **Verification Keyframes:** 8 extracted keyframes verified in [`qc_frames/`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-fight-club-narrator-no-name/output/qc_frames)

---

## 4. STAGE TIMINGS & PERFORMANCE
- **STAGE_01_RESEARCH:** 0.00s (0.00 min)
- **STAGE_02_AUDIO:** 4.12s (0.07 min)
- **STAGE_03_SUBTITLES:** 5.91s (0.10 min)
- **STAGE_04_STORYBOARD:** 0.00s (0.00 min)
- **STAGE_05_ASSETS:** 0.02s (0.00 min)
- **STAGE_06_REMOTION:** 0.00s (0.00 min)
- **STAGE_07_RENDER_1080P:** 63.03s (1.05 min)
- **STAGE_08_UPSCALE_8K:** 119.49s (1.99 min)
- **STAGE_09_THUMBNAIL:** 0.25s (0.00 min)
- **STAGE_10_QC:** 2.43s (0.04 min)
- **STAGE_11_REGISTRATION:** 0.01s (0.00 min)
- **TOTAL PIPELINE RUNTIME:** 195.26s (3.25 min)

---

## 5. VERIFICATION STATEMENT
All deliverables conform to the 14 sections of `MOVIE_BREAKDOWN_MASTER.md`. The approved script was rendered verbatim with zero text rewrites. The active footage is framed at 70% with ambient blur and gold dividers. Master 1080p and 8K deliverables are finalized and ready for immediate broadcast.
