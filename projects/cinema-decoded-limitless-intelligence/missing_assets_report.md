# Missing Assets Report: Limitless (2011)

## 1. Status Overview
- **Script**: Approved & Fact-Checked (`projects/cinema-decoded-limitless-intelligence/script.txt`, 157 words, Score 70/70)
- **Audio**: Generated & Mastered (`projects/cinema-decoded-limitless-intelligence/audio/limitless_achird_master.wav`, 51.27s, Gemini Achird voice, EBU R128 -14.0 LUFS)
- **Subtitles**: Generated & Aligned (`projects/cinema-decoded-limitless-intelligence/limitless_subtitles.ass`, 56 kinetic CenterBold cards with cinematic yellow keyword highlights: `INTELLIGENCE`, `AMBITION`, `CONTROL`, `DEPENDENCY`, `JUDGMENT`, `WISDOM`, NO box text)
- **Video Sourcing Status**: Blocked by YouTube Automated Scraping Protection (`HTTP Error 429: Too Many Requests / Sign in to confirm you're not a bot`).

Per system security and tool integrity policies, the agent never attempts to solve or bypass CAPTCHAs, proof-of-work challenges, or bot detection.

---

## 2. Required Video Assets

| Beat ID | Scene Description | Target Path in `output/clip_cache/` |
| :--- | :--- | :--- |
| **Beat 1 (0.00s – 3.14s)** | Eddie Morra on edge of luxury penthouse ledge; high-contrast opening | `output/clip_cache/limitless_penthouse_opening_1080p.mp4` |
| **Beat 2 (3.14s – 11.92s)** | Messy Chinatown apartment, unkempt Eddie staring blankly, Vern handing pill | `output/clip_cache/limitless_messy_apartment_1080p.mp4` |
| **Beat 3 (11.92s – 21.30s)** | Golden infinite zoom rush through Manhattan, stock day-trading, rapid typing | `output/clip_cache/limitless_infinite_zoom_trading_1080p.mp4` |
| **Beat 4 (21.30s – 31.70s)** | Carl Van Loon (Robert De Niro) confronting Eddie in executive boardroom | `output/clip_cache/limitless_van_loon_confrontation_1080p.mp4` |
| **Beat 5 (31.70s – 42.00s)** | Gennady loan shark threatening Eddie in rain; withdrawal sickness & tremor | `output/clip_cache/limitless_gennady_withdrawal_1080p.mp4` |
| **Beat 6 (42.00s – 51.27s)** | Impeccably tailored Eddie walking through campaign crowd, calm reflection | `output/clip_cache/limitless_ending_senate_1080p.mp4` |

---

## 3. How to Supply the Assets

To complete the 8K composite and render, choose either option below:

### Option A: Export YouTube Cookies (Recommended for full automation)
1. In your Google Chrome browser where you are signed into YouTube, use a cookie export extension (such as *Get cookies.txt LOCALLY*).
2. Save the exported cookie file as `config/youtube_cookies.txt`.
3. The pipeline will automatically pick up `config/youtube_cookies.txt` with `yt-dlp --cookies config/youtube_cookies.txt` and download all 6 scenes.

### Option B: Direct File Placement
Download or place any 1080p MP4 clips of *Limitless* into `output/clip_cache/` matching the filenames in the table above (or place a single clip like `output/clip_cache/limitless_1080p.mp4`). Then instruct the agent to trigger `build_limitless_decoded.py`.

