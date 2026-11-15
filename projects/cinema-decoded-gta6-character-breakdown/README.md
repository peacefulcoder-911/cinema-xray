# Cinema Decoded: Why GTA 6 Has Two Main Characters

A high-retention gaming documentary Short explaining why Grand Theft Auto VI (Rockstar Games) follows dual protagonists: **Jason Duval** and **Lucia Caminos**.

---

## Deliverables & Assets

* **YouTube URL (Unlisted Master):** [https://youtu.be/GmUd8k2G5Y0](https://youtu.be/GmUd8k2G5Y0)
* **YouTube Video ID:** `GmUd8k2G5Y0`
* **8K Ultra HD Master:** `output/gta6-master-8k.mp4` (4320x7680 @ 85 Mbps HEVC)
* **1080p Delivery Short:** `output/gta6-youtube-1080p.mp4` (1080x1920 @ 30 FPS)
* **High-CTR Thumbnail:** `output/thumbnail.jpg` (1080x1920)
* **8 QC Keyframes:** `output/qc_frames/`

---

## Research & Documentation
* [`research/character-facts.md`](research/character-facts.md): Canonical character profiles for Jason Duval and Lucia Caminos, verified against official Rockstar Games sources.
* [`research/source-references.md`](research/source-references.md): Rockstar Games official portal, Trailer 1 timestamps, and Take-Two Interactive press materials.
* [`research/word-to-visual-mapping.md`](research/word-to-visual-mapping.md): 14-scene word-level visual alignment table.
* [`research/footage-manifest.json`](research/footage-manifest.json): Exact source timestamps, motion treatments, and callout graphics.

---

## Production Pipeline
* **Voiceover:** ElevenLabs Liam (`VCgLBmBjldJmfphyB8sZ`), conversational documentary pacing, mastered to EBU R128 (-14.0 LUFS, -1.0 dBFS True Peak).
* **Duration:** 61.13 seconds (strictly complying with the 60–70s brief target).
* **Framing:** 70% active cinematic canvas (`1080x1344`) centered on `1080x1920` with soft ambient Gaussian blur backdrop (`boxblur=35:5`) and neon pink (`#ff4499`) & cyan (`#00e5ff`) matte dividers.
* **Subtitles:** Arc Reactor Cyan HUD / Jack D Films typography with neon pink keyword highlights, ASS millisecond word-synchronized via `faster-whisper`.
* **Super-Resolution:** Apple Silicon hardware-accelerated HEVC (`hevc_videotoolbox`) upscaling to 8K.
