# 🎬 Cinema X-Ray

> **Autonomous AI-Powered Movie Breakdowns, High-Retention Video Essays, & 4K Cinematic Shorts.**

Cinema X-Ray is an end-to-end autonomous video production pipeline designed to generate viral movie explainers, psychological breakdowns, and cinematic deep-dives with zero manual editing.

---

## ⚡ Strategic Autonomous Pipeline (`pipeline/`)

The pipeline runs completely on its own via `python3 run_cinema_xray.py`:

```
┌────────────────────────────────────────────────────────┐
│ 1. Autonomous Script Engine (pipeline/script_generator) │
│    - Viral 4-part cinema essay structure               │
│    - Visual anomaly hook -> Lorentz paradox -> payoff  │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Studio TTS Synthesis (pipeline/audio_generator)     │
│    - Gemini 3.1 Flash Achird voice                     │
│    - Calm, authoritative, charismatic film analyst      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Center Bold Stroke Engine (pipeline/subtitle_engine)│
│    - Gemini speech-to-phrase forced alignment          │
│    - 2-4 word cards, Arial Black, Outline=10, 76pt     │
│    - Glowing gold highlighted keywords (\c&H0000E5FF&) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. 70% Screen Framing Compositor (video_compositor)   │
│    - Auto-detects & removes Cinemascope letterbox bars │
│    - Movie footage fills 70% of screen height (1344px) │
│    - Top (15%) & Bottom (15%) blurred ambient backdrop │
│    - Generates & mixes sub-bass tension drone & noise  │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 5. Master Render & 4K Upscale                          │
│    - 1080x1920 60fps Short (YouTube / TikTok / Reels)  │
│    - 2160x3840 4K UHD Master (Lanczos + VideoToolbox)  │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 One-Click Execution

To build a brand new video autonomously:

```bash
cd /Users/vinaybt/Downloads/cinema-xray
python3 run_cinema_xray.py
```

### Outputs Generated:
- **1080p Master**: `output/final_video/cinema_xray_cap_mjolnir_worthy.mp4`
- **4K UHD Master**: `output/final_video/cinema_xray_cap_mjolnir_worthy_4k.mp4`
- **Voiceover**: `output/audio/mjolnir_worthiness_voiceover.wav`
- **Timed Subtitles**: `output/script/subtitles.json` & `output/temp/subtitles_center_bold.ass`

---

## 📁 Repository Structure
```
cinema-xray/
├── pipeline/                    # Autonomous production modules
│   ├── script_generator.py      # LLM viral movie script generator
│   ├── audio_generator.py       # Gemini Achird voiceover synthesizer
│   ├── subtitle_engine.py       # Center Bold Stroke ASS subtitle aligner
│   └── video_compositor.py      # 70% framing, letterbox strip & 4K upscaler
├── run_cinema_xray.py           # Master autonomous orchestrator
├── projects/
│   ├── interstellar-decoded/    # 5-Chapter scientific documentary pipeline
│   └── marvel-decoded/          # Marvel raw video assets & tech scripts
├── output/                      # Generated scripts, audio, clips & 4K video
└── docs/                        # Retention blueprints & audio profiles
```
