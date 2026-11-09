# Missing Assets Report: The Martian (2015)

## 1. Status Overview
- **Script**: Approved (`projects/cinema-decoded-the-martian-problem-solving/script.txt`, 139 words)
- **Audio**: Generated & Mastered (`projects/cinema-decoded-the-martian-problem-solving/audio/martian_achird_fast.wav`, 46.52s, EBU R128 -14.0 LUFS)
- **Subtitles**: Generated & Aligned (`projects/cinema-decoded-the-martian-problem-solving/martian_subtitles.ass`, 47 precision CenterBold cards)
- **Video Sourcing**: Blocked by YouTube Anti-Bot Verification (`HTTP Error 429: Too Many Requests / Sign in to confirm you're not a bot`).

---

## 2. Required Video Assets

| Beat ID | Scene Description | Target Path in `output/clip_cache/` |
| :--- | :--- | :--- |
| **Beat 1 (0.0s – 7.5s)** | Ares III Hab exterior / solitary Watney surveying Mars | `output/clip_cache/the_martian_alone_on_mars_1080p.mp4` |
| **Beat 2 (7.5s – 16.0s)** | Hab interior / calorie and ration calculation sequence | `output/clip_cache/the_martian_resource_planning_1080p.mp4` |
| **Beat 3 (16.0s – 23.5s)** | Hab farming sequence / potato planting and sprout growth | `output/clip_cache/the_martian_planting_potatoes_1080p.mp4` |
| **Beat 4 (23.5s – 31.0s)** | Hydrazine water creation experiment in Hab | `output/clip_cache/the_martian_making_water_1080p.mp4` |
| **Beat 5 (31.0s – 39.5s)** | Pathfinder probe recovery and hexadecimal comms | `output/clip_cache/the_martian_pathfinder_comms_1080p.mp4` |
| **Beat 6 (39.5s – 46.5s)** | Rover journey across Martian desert towards Ares IV | `output/clip_cache/the_martian_rover_journey_1080p.mp4` |

---

## 3. How to Supply the Assets

To complete the 8K composite and rendering, choose either option below:

### Option A: Export YouTube Cookies (Recommended for full automation)
1. In your Google Chrome browser where you are signed into YouTube, use a cookie export extension (e.g., *Get cookies.txt LOCALLY*).
2. Save the exported cookie file as `config/youtube_cookies.txt`.
3. The pipeline will automatically pick up `config/youtube_cookies.txt` with `yt-dlp --cookies config/youtube_cookies.txt` and download all 6 scenes.

### Option B: Direct File Placement
Download or place any 1080p MP4 clips of *The Martian* into `output/clip_cache/` (e.g. `output/clip_cache/the_martian_1080p.mp4`) and notify the agent to link the scene beats and trigger the 8K render.

