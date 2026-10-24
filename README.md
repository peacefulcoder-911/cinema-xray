# 🎬 Cinema X-Ray

> **AI-Powered Movie Breakdowns, High-End Video Essays, & Scientific Cinematic Explainers.**

Cinema X-Ray is an automated production suite for generating cinematic video essays, scientific scene breakdowns, and pop culture deep-dives.

## 🌟 Capabilities & Projects
- **Cinema Decoded Engine (`automation/`)**:
  - Master script generation engine using structured prompts for high audience retention.
  - Topic discovery, hook formulation, and narrative progression.
- **Interstellar Explained (`projects/interstellar-decoded/`)**:
  - Full 5-chapter scientific documentary exploring gravitational time dilation, black hole accretion physics, wormhole geometry, 5D tesseract, and quantum gravity.
  - Multi-track audio assembly with Gemini Achird TTS and cinematic Hans Zimmer orchestral scores.
- **Marvel Decoded (`projects/marvel-decoded/`)**:
  - Scene-by-scene technology breakdown (e.g. Iron Man Nanotech Armor mechanics vs. Thanos).
  - Multi-voice narration using ElevenLabs & Gemini voice engines with styled ASS subtitles.

## 📁 Repository Structure
```
cinema-xray/
├── automation/                  # Master script generator & pipeline automation
│   ├── prompts/                 # Retention-focused script engineering prompts
│   ├── config/                  # Engine configurations
│   └── output/                  # Generated topics & transcripts
├── projects/
│   ├── interstellar-decoded/    # 5-Chapter scientific documentary pipeline
│   │   ├── build_interstellar_documentary.py
│   │   ├── script/              # Chapter scripts & director notes
│   │   └── audio/               # Voiceover generation scripts
│   └── marvel-decoded/          # Marvel tech and battle breakdown pipeline
│       ├── elevenlabs_client.js
│       ├── generate_nanotech_audio.cjs
│       └── script/
└── docs/                        # Master script engine frameworks & blueprints
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- FFmpeg 6.0+

### 2. Configure Credentials
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### 3. Run Interstellar Documentary Assembly
```bash
cd projects/interstellar-decoded
python3 audio/generate_all_achird_audio.py
python3 build_interstellar_documentary.py
```
