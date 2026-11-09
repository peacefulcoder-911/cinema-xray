# Missing Assets Report: A Beautiful Mind (2001)

## 1. Status Overview
- **Script**: Approved & Fact-Checked (`projects/cinema-decoded-beautiful-mind-perception/script.txt`, 143 words, Score 69/70)
- **Audio**: Generated & Mastered (`projects/cinema-decoded-beautiful-mind-perception/audio/beautiful_mind_achird_master.wav`, 49.37s, Gemini Achird voice, EBU R128 -14.0 LUFS)
- **Subtitles**: Generated & Aligned (`projects/cinema-decoded-beautiful-mind-perception/beautiful_mind_subtitles.ass`, 52 kinetic CenterBold cards with cinematic yellow keyword highlights, NO box text)
- **Video Sourcing Status**: Blocked by YouTube Automated Scraping Protection (`HTTP Error 429: Too Many Requests / Sign in to confirm you're not a bot`).

Per system security and tool integrity policies, the agent never attempts to solve or bypass CAPTCHAs, proof-of-work challenges, or bot detection.

---

## 2. Required Video Assets

| Beat ID | Scene Description | Target Path in `output/clip_cache/` |
| :--- | :--- | :--- |
| **Beat 1 (0.00s – 6.54s)** | John Nash arriving at Princeton campus, observing patterns and light | `output/clip_cache/beautiful_mind_princeton_arrival_1080p.mp4` |
| **Beat 2 (6.54s – 15.10s)** | Nash scribbling equations on the dorm window glass in natural light | `output/clip_cache/beautiful_mind_window_equations_1080p.mp4` |
| **Beat 3 (15.10s – 24.20s)** | Charles Herman entering dorm, sharing flask, physically interacting | `output/clip_cache/beautiful_mind_john_meets_charles_1080p.mp4` |
| **Beat 4 (24.20s – 33.60s)** | William Parcher (Ed Harris) meeting Nash in warehouse / codebreaking | `output/clip_cache/beautiful_mind_parcher_espionage_1080p.mp4` |
| **Beat 5 (33.60s – 40.50s)** | Dr. Rosen in psychiatric hospital / Alicia uncovering the shed letters | `output/clip_cache/beautiful_mind_shed_revelation_1080p.mp4` |
| **Beat 6 (40.50s – 49.37s)** | Older John Nash at Princeton seeing Charles & Marcee standing silently | `output/clip_cache/beautiful_mind_ending_courtyard_1080p.mp4` |

---

## 3. How to Supply the Assets

To complete the 8K composite and render, choose either option below:

### Option A: Export YouTube Cookies (Recommended for full automation)
1. In your Google Chrome browser where you are signed into YouTube, use a cookie export extension (such as *Get cookies.txt LOCALLY*).
2. Save the exported cookie file as `config/youtube_cookies.txt`.
3. The pipeline will automatically pick up `config/youtube_cookies.txt` with `yt-dlp --cookies config/youtube_cookies.txt` and download all 6 scenes.

### Option B: Direct File Placement
Download or place any 1080p MP4 clips of *A Beautiful Mind* into `output/clip_cache/` matching the filenames in the table above (or place a single clip like `output/clip_cache/beautiful_mind_1080p.mp4`). Then instruct the agent to trigger `build_beautiful_mind_decoded.py`.

