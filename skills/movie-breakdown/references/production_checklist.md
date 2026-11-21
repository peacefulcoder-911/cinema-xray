# Movie Breakdown: 14-Section Production Checklist

Use this checklist to verify compliance with [`MOVIE_BREAKDOWN_MASTER.md`](file:///Users/vinaybt/Downloads/cinema-xray/MOVIE_BREAKDOWN_MASTER.md) on every video production run.

| Section | Quality Gate | Verification Criteria | Status |
| :--- | :--- | :--- | :--- |
| **01** | **Creative Brief** | Clear premise, curiosity-inducing hook within 2 seconds, satisfying payoff. | [ ] Verified |
| **02** | **Script Lock** | Approved script text matches verbatim. Zero unauthorized rewrites or line deletions. | [ ] Verified |
| **03** | **Canon Research** | Claims verified against authoritative lore/franchise sources in `research/fact_check_report.md`. | [ ] Verified |
| **04** | **Narration Cadence** | Single-shot continuous ElevenLabs Liam synthesis. Zero artificial pause gaps between sentences. | [ ] Verified |
| **05** | **Audio Mastering** | Broadcast loudness mastered to EBU R128 (-14.0 LUFS, -1.0 dBFS Peak). Zero clipping. | [ ] Verified |
| **06** | **Subtitles HUD** | Arc Reactor Cyan HUD (Futura 74pt, MarginV 360). High-impact keywords highlighted in `#00FFFF`. | [ ] Verified |
| **07** | **Visual Plan** | Visual Decision Plan in `scene_plan.json`. Beats timed between 2.5s and 4.0s for rapid pacing. | [ ] Verified |
| **08** | **70% Viewport** | 70% Active Cinematic Framing (1080x1344 @ Y=288) with ambient Gaussian blur and gold divider bars. | [ ] Verified |
| **09** | **Sound Design** | Zero forbidden transition SFX (no whoosh, swoosh, swish, riser, sweep, reverse cymbal). Subtle ambient bed only. | [ ] Verified |
| **10** | **Remotion Scaffolding** | Isolated React composition in `projects/cinema-decoded-<slug>/src/` without overwriting prior projects. | [ ] Verified |
| **11** | **1080p Master** | 1080x1920 30 FPS MP4 rendered with burned subtitles and mastered audio track. | [ ] Verified |
| **12** | **8K Super-Res** | Apple Silicon VideoToolbox HEVC (`hevc_videotoolbox` @ 85 Mbps) upscale via `ultra_upscaler_8k.py`. | [ ] Verified |
| **13** | **High-CTR Cover** | 1080x1920 high-contrast thumbnail generated in `output/thumbnail_<slug>.jpg`. | [ ] Verified |
| **14** | **QC Audit** | 8 verification frames extracted in `output/qc_frames/`. ffprobe validation report in `output/qc_report.json`. | [ ] Verified |
