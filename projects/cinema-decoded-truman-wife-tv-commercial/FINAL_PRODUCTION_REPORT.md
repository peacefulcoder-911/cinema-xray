# MOVIE BREAKDOWN — SECTION 14 DELIVERABLES & FINAL QC REPORT

## 1. PROJECT IDENTIFICATION
- **Movie / Franchise:** The Truman Show
- **Specific Topic:** Why Truman's Wife Acts Like a TV Commercial
- **Project Slug:** `cinema-decoded-truman-wife-tv-commercial`
- **Production Engine:** Remotion + Studio Python Pipeline
- **Visual Identity:** 70% Active Cinematic Viewport with Ambient Blurred Background

---

## 2. PRODUCTION STATUS & DELIVERABLES
| Asset Type | Resolution | Format | Verified File Path |
| :--- | :--- | :--- | :--- |
| **1080p Master** | 1080x1920 | MP4 (H.264) | [`cinema_xray_truman-wife-tv-commercial_1080p.mp4`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/output/cinema_xray_truman-wife-tv-commercial_1080p.mp4) |
| **8K Super-Res** | 4320x7680 | MP4 (HEVC) | [`cinema_xray_truman-wife-tv-commercial_8k.mp4`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/output/cinema_xray_truman-wife-tv-commercial_8k.mp4) |
| **Master Voiceover**| 48kHz Mono | WAV (PCM 16-bit) | [`master_narration.wav`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/assets/narration/master_narration.wav) |
| **Subtitles (ASS)** | 1080x1920 | ASS (Arc Cyan) | [`subtitles.ass`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/subtitles.ass) |
| **Subtitles (JSON)**| Time-stamped | JSON (Cards) | [`subtitles.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/subtitles.json) |
| **High-CTR Cover**  | 1080x1920 | JPG (High-Q) | [`thumbnail_truman-wife-tv-commercial.jpg`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/output/thumbnail_truman-wife-tv-commercial.jpg) |
| **Scene Storyboard**| Beat-by-Beat | JSON | [`scene_plan.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/scene_plan.json) |
| **Remotion Source** | 9:16 React | TSX / Remotion | [`src`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/src) |
| **QC Report**       | Multi-point | JSON | [`qc_report.json`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/output/qc_report.json) |

---

## 3. TECHNICAL SPECIFICATIONS & QC AUDIT
- **Total Master Duration:** 42.00 seconds
- **Frame Rate:** 30.000 FPS (Constant)
- **Active Framing:** 1080x1344 (70% screen height @ Y=288)
- **Audio Peak:** -5.20 dBFS (Broadcast compliant, zero digital clipping)
- **Audio Mean:** -22.10 dBFS
- **Sound Design Restrictions:** 100% COMPLIANT (Zero whoosh, swoosh, swish, riser, sweep, or cymbal SFX)
- **Acoustic Cadence:** Single-shot continuous Liam narration (Zero artificial pause gaps)
- **Verification Keyframes:** 8 extracted keyframes verified in [`qc_frames/`](file:///Users/vinaybt/Downloads/cinema-xray/projects/cinema-decoded-truman-wife-tv-commercial/output/qc_frames)

---

## 4. STAGE TIMINGS & PERFORMANCE
- **STAGE_01_RESEARCH:** 0.00s (0.00 min)
- **STAGE_02_AUDIO:** 5.36s (0.09 min)
- **STAGE_03_SUBTITLES:** 22.42s (0.37 min)
- **STAGE_04_STORYBOARD:** 0.00s (0.00 min)
- **STAGE_05_ASSETS:** 0.03s (0.00 min)
- **STAGE_06_REMOTION:** 0.00s (0.00 min)
- **STAGE_07_RENDER_1080P:** 60.31s (1.01 min)
- **STAGE_08_UPSCALE_8K:** 123.28s (2.05 min)
- **STAGE_09_THUMBNAIL:** 0.23s (0.00 min)
- **STAGE_10_QC:** 3.04s (0.05 min)
- **STAGE_11_REGISTRATION:** 0.01s (0.00 min)
- **TOTAL PIPELINE RUNTIME:** 214.68s (3.58 min)

---

## 5. VERIFICATION STATEMENT
All deliverables conform to the 14 sections of `MOVIE_BREAKDOWN_MASTER.md`. The approved script was rendered verbatim with zero text rewrites. The active footage is framed at 70% with ambient blur and gold dividers. Master 1080p and 8K deliverables are finalized and ready for immediate broadcast.
