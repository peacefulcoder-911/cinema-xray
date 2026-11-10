# PROJECT: WHIPLASH — THE CARNEGIE HALL TRAP

## YOUR ROLE
Act as a world-class cinematic video editor and lead storyteller for Cinema Decoded. Your mission is to transform the provided psychological thesis into a 50-second, high-impact vertical video essay (9:16) for intelligent film fans. 
The central discovery: **Fletcher’s invitation to Carnegie Hall was never redemption; it was career sabotage and public execution until Andrew turned the trap into his own weapon.**
Do not turn this into a general movie explanation. Focus strictly on the psychological warfare between Fletcher and Andrew during the final performance.

---
## 1. NON-NEGOTIABLE SCRIPT
Use this narration EXACTLY as provided.
Do not rewrite, paraphrase, shorten, expand, or regenerate the script.
### APPROVED NARRATION
"You think Fletcher’s invitation to Carnegie Hall was redemption, but it was actually a calculated execution. Look closely at Fletcher’s face when Andrew walks onto that stage. There is no pride in those eyes—only cold, vindictive payback for the lawsuit that ruined his career. He hands Andrew the wrong chart on purpose, setting him up for total public humiliation in front of the entire jazz elite. The trap was set. But Fletcher miscalculated. Andrew doesn't leave the stage in shame. He steals the tempo, steps into the spotlight, and forces Fletcher to follow his lead. Which film villain has the most satisfying downfall? Tell me in the comments."
Preserve the narration order and wording.

---
## 2. CREATIVE DIRECTION
### Visual identity
Deep blacks, controlled shadows, high-contrast warm stage lighting, stark amber spotlighting on brass instruments, sharp subject separation, subtle 35mm film grain.
### Visual principle
**Every narration line must have a visually meaningful counterpart.**

---
## 3. SENTENCE-LEVEL VISUAL STORYTELLING

### SHOT 1 — THE HOOK (0–5s)
- **Narration:** You think Fletcher’s invitation to Carnegie Hall was redemption, but it was actually a calculated execution.
- **Visual direction:** Slow push-in on Andrew walking onto the darkened Carnegie Hall stage. Desaturated color grade shifting into harsh warm overhead spotlight.
- **Typography/Graphic:** CALCULATED EXECUTION (Cyan HUD overlay, center-screen, 0.8s fade out).

### SHOT 2 (5–12s)
- **Narration:** Look closely at Fletcher’s face when Andrew walks onto that stage.
- **Visual direction:** Extreme tight macro rack-focus on J.K. Simmons' (Fletcher) eyes, narrowing from behind the music stand.
- **Typography/Graphic:** NO REDEMPTION (Bottom third, Stark Cyan).

### SHOT 3 (12–20s)
- **Narration:** There is no pride in those eyes—only cold, vindictive payback for the lawsuit that ruined his career.
- **Visual direction:** Quick match-cut to archival courtroom deposition flash-frame (desaturated cyan tint), cutting instantly back to Fletcher's tight, unblinking glare.
- **Typography/Graphic:** COLD PAYBACK (Stark cyan highlighted phrase).

### SHOT 4 (20–30s)
- **Narration:** He hands Andrew the wrong chart on purpose, setting him up for total public humiliation in front of the entire jazz elite.
- **Visual direction:** Low-angle tracking shot of Fletcher sliding the folder across the music stand, lips curled in a slight, silent smirk.
- **Typography/Graphic:** THE WRONG CHART (Bold HUD overlay).

### SHOT 5 (30–38s)
- **Narration:** The trap was set. But Fletcher miscalculated.
- **Visual direction:** Rapid rhythmic montage: sweat dripping onto a snare drum, Andrew’s wide, hyper-focused eyes locked onto Fletcher.
- **Typography/Graphic:** THE TRAP (Pulsing cyan display).

### SHOT 6 — THE PAYOFF (38–46s)
- **Narration:** Andrew doesn't leave the stage in shame. He steals the tempo, steps into the spotlight, and forces Fletcher to follow his lead.
- **Visual direction:** Explosive dynamic camera movement—orbiting Andrew as sticks blur against drum heads, cutting to Fletcher’s stunned, wide-eyed realization.
- **Typography/Graphic:** SEIZING THE TEMPO (High-contrast center title).

### SHOT 7 — COMMENT PROMPT (46–50s)
- **Narration:** Which film villain has the most satisfying downfall? Tell me in the comments.
- **Visual direction:** Final lingering close-up on Andrew's triumphant nod, cutting to a clean, dark-graded end-card plate.
- **Typography/Graphic:** TELL ME IN THE COMMENTS (Futura bold, lower third).

---
## 4. FOOTAGE RESEARCH AND ACQUISITION
- **Primary Source:** *Whiplash* (2014), directed by Damien Chazelle.
- **Key Scenes:** 
  - Carnegie Hall arrival sequence (Timestamp: 01:35:10 - 01:36:40).
  - The wrong chart confrontation (Timestamp: 01:38:00 - 01:39:30).
  - The final "Caravan" drum solo climax (Timestamp: 01:41:00 - 01:45:05).
- **Asset Path:** `/volumes/vault/cinema_decoded/footage/whiplash_carnegie_master_prores.mov`

---
## 5. MOTION AND EDITING
- Controlled push-ins on dialogue beats.
- Sharp match cuts synchronized precisely to the snare drum hits in the final sequence.
- Vertical 9:16 reframing centered strictly on actors' eyes and instrument interactions using motion-tracked bounding boxes.

---
## 6. AUDIO GENERATION — STRICT RESTRICTIONS
- **Voice Profile:** Confident documentary voice, Achird profile. Measured, rhythmic, authoritative cadence.
- **Music:** Sparse, tense ambient sub-bass drone building into crisp, isolated theatrical drum transients.
- **ABSOLUTELY PROHIBITED SOUND EFFECTS:** ZERO whooshes, zero swooshes, zero risers, zero sweeps, zero transition impacts. 
- **Audio Cleanliness:** Silence floor <= -65 dB. Dialogue mixed cleanly at -3 dB over balanced cinematic room tone.

---
## 7. CAPTIONS AND GRAPHICS
- **Style:** Arc Reactor Cyan HUD high-contrast synchronized subtitles.
- **Font:** Futura 74pt lower-third.
- **Highlighting:** Key psychological and investigative words highlighted in vivid Stark cyan.
- **Placement:** Lower-middle third, strict margin boundaries to avoid platform UI overlaps.

---
## 8. TECHNICAL IMPLEMENTATION
Workflow: 
APPROVED NARRATION -> SENTENCE PARSER -> SCENE JSON -> TIMING ENGINE -> FOOTAGE MAPPING -> CLEAN AUDIO GENERATION -> CAPTION GENERATION -> REMOTION / FFMPEG 8K RENDERING -> QUALITY CONTROL.

---
## 9. RENDER REQUIREMENTS
- 8K Vertical Master: 4320x7680 @ 30 FPS (ProRes 422 HQ).
- 1080p Delivery Copy: 1080x1920 @ 30 FPS (H.265, high bitrate MP4).

---
## 10. FINAL QUALITY CONTROL
- **Story:** Does the hook instantly reframe the Carnegie Hall scene? Yes.
- **Visuals:** Are there zero generic B-roll shots? Yes. Every shot maps precisely to the narration line.
- **Audio:** Is the silence floor maintained below -65 dB? Are all prohibited swooshes/whooshes eliminated? Yes.
- **Technical:** Are dimensions strictly 9:16 vertical 8K/1080p masters? Yes.

---
## 11. FINAL DELIVERABLES
1. 8K Master ProRes 4320x7680 file.
2. 1080p Web-Ready MP4 file.
3. Isolated Voiceover Audio Track (WAV, 24-bit/48kHz).
4. Isolated Cinematic Score & Sound Effects Track.
5. Exact Timed SRT Subtitle File with Cyan Formatting Tags.
6. Scene-by-Scene JSON Timing Manifest.
7. Color Grade Look-Up Table (.cube) profile for Whiplash Dark Stage aesthetic.
8. Thumbnail Graphic (9:16 vertical plate featuring Fletcher’s glaring eyes).
9. QA Compliance Audit Sheet confirming zero prohibited sound effects.
10. Final Executive Producer Sign-Off Log.

## FINAL CREATIVE STANDARD
High contrast. Immersive visuals. Precise storytelling. True 8K output verification. No whoosh sounds.