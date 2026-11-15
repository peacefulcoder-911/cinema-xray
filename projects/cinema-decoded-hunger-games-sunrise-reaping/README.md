# Cinema Decoded: Why Haymitch Had to Face 47 Other Tributes

A high-retention movie breakdown Short explaining the lethal rule change of the 50th Hunger Games (The Second Quarter Quell) in *The Hunger Games: Sunrise on the Reaping* (2026), where young Haymitch Abernathy is forced into an arena with 47 other tributes instead of 23.

---

## Key Deliverables & Artifacts

* **8K Ultra HD Master:** `output/sunrise-master-8k.mp4` (4320x7680 @ 85 Mbps HEVC)
* **1080p Delivery Short:** `output/sunrise-youtube-1080p.mp4` (1080x1920 @ 30 FPS)
* **High-CTR Vertical Thumbnail:** `output/thumbnail.jpg` (1080x1920)
* **8 QC Keyframes:** `output/qc_frames/`
* **Subtitles:** `subtitles.ass` (Arc Reactor Cyan HUD / Gold highlight, word-synchronized via `faster-whisper`)

---

## Research & Documentation

* [`script/approved-script.txt`](script/approved-script.txt): Locked 15-sentence narration script.
* [`script/narration-timing.json`](script/narration-timing.json): Millisecond-accurate timestamp breakdown for all 15 sentences and scenes.
* [`research/verified-facts.md`](research/verified-facts.md): Canonical lore analysis of the 50th Hunger Games, Second Quarter Quell, and Haymitch's victory.
* [`research/source-references.md`](research/source-references.md): Official Lionsgate promotional trailer timestamps and Scholastic literary references.
* [`research/word-to-visual-mapping.md`](research/word-to-visual-mapping.md): 15-scene word-level visual alignment table.
* [`research/footage-manifest.json`](research/footage-manifest.json): Exact source timestamps, motion treatments, and callout graphics.

---

## Production Pipeline

* **Narration Voice:** ElevenLabs Liam (`VCgLBmBjldJmfphyB8sZ`), conversational storyteller delivery, calibrated with `atempo=0.88` for clear numerical articulation.
* **Audio Mastering:** EBU R128 (-14.0 LUFS integrated loudness, -1.0 dBFS true peak broadcast safety).
* **Duration:** 65.95 seconds (strictly compliant with 65–75 second brief requirement).
* **Visual Staging:** 70% active cinematic viewport (`1080x1344`) centered on `1080x1920` with ambient Gaussian blur backdrop (`boxblur=35:5`), Panem Gold (`#ffb703`) matte dividers, and cyan/crimson/gold HUD callout badges.
* **Acoustic Subtitles:** Word-level forced acoustic alignment with instant pause clearance (>=0.18s) and bright cyan keyword highlights (`\c&H00FFFF00&`).
* **Super-Resolution:** Apple Silicon hardware-accelerated HEVC (`hevc_videotoolbox`) upscaling to 8K master (4320x7680).
