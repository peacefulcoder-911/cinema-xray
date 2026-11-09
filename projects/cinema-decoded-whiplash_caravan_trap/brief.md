# PROJECT: WHIPLASH — THE FINAL TRAP OF CARNEGIE HALL

## YOUR ROLE
Act as a world-class cinematic video editor, sound designer, and senior executive producer for Cinema Decoded. 
The central discovery: **Fletcher's invitation to Carnegie Hall was never a redemption arc; it was a premeditated public execution designed to destroy Andrew's career for good.**
Do not turn this into a general movie explanation. Focus strictly on the psychological warfare and professional assassination attempt during the Carnegie Hall performance.

---
## 1. NON-NEGOTIABLE SCRIPT
Use this narration EXACTLY as provided.
Do not rewrite, paraphrase, shorten, expand, or regenerate the script.
### APPROVED NARRATION
"Look closely at the deceptive, knowing smile Fletcher gives the drummer right before the downbeat of "Whiplash." Andrew thinks he is finally earning his mentor’s respect on the Carnegie Hall stage. But notice what happens when the band starts. Fletcher calls "Whiplash," but hands Andrew the charts for "Upswingin'." It is not an innocent mistake. It is calculated career sabotage. Fletcher knows Andrew doesn't know the charts, designed to publicly humiliate the kid who testified against him. The trap is set. But Andrew doesn't walk off. He takes the sticks back, sets his own tempo, and traps Fletcher instead. Which film villain hides their malice behind mentorship best? Tell me in the comments."
Preserve the narration order and wording.

---
## 2. CREATIVE DIRECTION
### Visual identity
Harsh stage lighting, high-contrast shadows, cold blues contrasting with suffocating golden spotlights, sharp subject separation, sweat on skin under intense magnification, subtle 35mm film grain.
### Visual principle
**Every narration line must have a visually meaningful counterpart.**

---
## 3. SENTENCE-LEVEL VISUAL STORYTELLING

### SHOT 1 — THE HOOK
- **Narration:** Look closely at the deceptive, knowing smile Fletcher gives the drummer right before the downbeat of "Whiplash."
- **Visual direction:** Extreme close-up on J.K. Simmons’ face (Fletcher). Cold stage lights catch the corner of his mouth curving into a razor-thin, malicious grin. Slow push-in, high contrast.
- **Typography / Graphic Callout:** 
  ```
  THE REAL TRAP
  ```

### SHOT 2
- **Narration:** Andrew thinks he is finally earning his mentor’s respect on the Carnegie Hall stage.
- **Visual direction:** Medium-wide shot of Andrew at the drum kit under a towering overhead spotlight, looking up at Fletcher with misplaced validation and hope.
- **Typography / Graphic Callout:** 
  ```
  THE ILLUSION OF REDEMPTION
  ```

### SHOT 3
- **Narration:** But notice what happens when the band starts. Fletcher calls "Whiplash," but hands Andrew the charts for "Upswingin'."
- **Visual direction:** Quick-cut close-up of sheet music resting on the stand. Rack focus to Fletcher's hand dropping the wrong folder onto Andrew's stand with deliberate carelessness.
- **Typography / Graphic Callout:** 
  ```
  NOT A MISTAKE. SABOTAGE.
  ```

### SHOT 4
- **Narration:** It is not an innocent mistake. It is calculated career sabotage.
- **Visual direction:** Tight focus on Andrew's eyes widening in sudden, paralyzing realization as he scans the incorrect musical arrangement. Deep shadows swallow the background orchestra.
- **Typography / Graphic Callout:** 
  ```
  PUBLIC EXECUTION
  ```

### SHOT 5
- **Narration:** Fletcher knows Andrew doesn't know the charts, designed to publicly humiliate the kid who testified against him.
- **Visual direction:** Cut back to Fletcher raising his baton, eyes locked directly onto Andrew with cold, unapologetic hostility. The power dynamic is absolute.
- **Typography / Graphic Callout:** 
  ```
  PAYBACK FOR THE TESTIMONY
  ```

### SHOT 6 — THE PAYOFF
- **Narration:** The trap is set. But Andrew doesn't walk off. He takes the sticks back, sets his own tempo, and traps Fletcher instead.
- **Visual direction:** Dynamic, rapid montage: Andrew walking back off-stage, picking up his drumsticks, locking eyes with Fletcher, and aggressively launching into "Caravan" without permission. Fletcher's smile drops instantly.
- **Typography / Graphic Callout:** 
  ```
  TURNING THE TABLES
  ```

### SHOT 7 — COMMENT PROMPT
- **Narration:** Which film villain hides their malice behind mentorship best? Tell me in the comments.
- **Visual direction:** Slow push-in on Fletcher's stunned, furious face realizing he has lost control of the music and the room. Fade down lighting sharply to 10% on the final beat.
- **Typography / Graphic Callout:** 
  ```
  WHICH VILLAIN HIDES BEHIND MENTORSHIP?
  ```

---
## 4. FOOTAGE RESEARCH AND ACQUISITION
- **Primary Source:** *Whiplash* (2014), directed by Damien Chazelle.
- **Key Sequences:** 
  - Carnegie Hall finale sequence (Timestamps: 01:36:00 - 01:44:00).
  - Fletcher's close-ups during the deceptive sheet music handoff.
  - Andrew's realization and defiance on the drum kit.
- **Asset Directory:** `/footage/movies/whiplash_2014/carnegie_hall_master.mkv`

---
## 5. MOTION AND EDITING
- **Camera Movement:** Controlled, heavy push-ins during psychological beats; sudden, sharp match-cuts on musical cues.
- **Pacing:** Starts slow and analytical during the hook, accelerates rapidly during the chart reveal, holds steady and intense through Andrew's rebellion.
- **Framing:** 9:16 vertical crop centered precisely on facial expressions and key props (sheet music, drumsticks).

---
## 6. AUDIO GENERATION — STRICT RESTRICTIONS
- **Voice Profile:** Confident documentary voice, Achird (measured, authoritative, calm delivery).
- **Absolute Prohibited Sound Effects:** ZERO whooshes, swooshes, risers, sweeps, transition impacts, or cinematic drops. 
- **Audio Cleanliness:** Silence floor <= -65 dB. Natural room tone and isolated score elements from the film must duck cleanly under the vocal track.

---
## 7. CAPTIONS AND GRAPHICS
- **Style:** CenterBold high-contrast synchronized subtitles.
- **Highlighting:** Key psychological words highlighted in warm gold (`#FFD700`).
- **Placement:** Lower-third vertical center, perfectly aligned to avoid platform UI overlays.

---
## 8. TECHNICAL IMPLEMENTATION
```
APPROVED NARRATION -> SENTENCE PARSER -> SCENE JSON -> TIMING ENGINE -> FOOTAGE MAPPING -> CLEAN AUDIO GENERATION -> CAPTION GENERATION -> REMOTION / FFMPEG 8K RENDERING -> QUALITY CONTROL
```

---
## 9. RENDER REQUIREMENTS
- **Primary Master:** 8K Vertical Master (4320 x 7680 @ 30 FPS, ProRes 422 HQ).
- **Delivery Copy:** 1080p Vertical Copy (1080 x 1920 @ 30 FPS, H.265 / MP4, High Bitrate).

---
## 10. FINAL QUALITY CONTROL
- **Story:** Does the script expose the hidden trap without wasting time on basic plot recap? Yes.
- **Visuals:** Does every single line of narration have a precise, purposeful visual counterpart? Yes.
- **Audio:** Are all prohibited sound effects (whooshes, risers) entirely absent? Confirmed. Is the silence floor below -65 dB? Yes.
- **Technical:** Are render resolutions locked at 8K master and 1080p delivery? Yes.

---
## 11. FINAL DELIVERABLES
1. Approved 95-115 word voiceover track (Achird profile).
2. Sentence-parsed JSON timing file.
3. 8K Vertical Master video file (4320x7680 @ 30 FPS).
4. 1080p Delivery copy video file (1080x1920 @ 30 FPS).
5. Synchronized CenterBold caption file (.srt / .json).
6. Isolated dialogue and score audio stems (ducked to -65 dB silence floor).
7. Color-graded vertical crops of the Carnegie Hall sequence.
8. Typography and graphic overlay asset layers.
9. Quality control diagnostic report verifying zero prohibited sound effects.
10. Final package archive for Cinema Decoded publishing pipeline.

## FINAL CREATIVE STANDARD
High contrast. Immersive visuals. Precise storytelling. True 8K output verification. No whoosh sounds.