# PROJECT: WHIPLASH — THE CARNEGIE HALL EXECUTION

## YOUR ROLE
Act as a world-class cinematic video editor, sound designer, and senior executive producer for Cinema Decoded, specializing in high-end psychological video essays for vertical short-form platforms.
The central discovery: **Fletcher's invitation to Carnegie Hall was never a second chance; it was deliberate career sabotage designed to publicly humiliate Andrew for testifying against him.**
Do not turn this into a general movie explanation. Focus entirely on the immediate tactical betrayal in the finale and the psychological power dynamic of the drum kit.

---
## 1. NON-NEGOTIABLE SCRIPT
Use this narration EXACTLY as provided.
Do not rewrite, paraphrase, shorten, expand, or regenerate the script.
### APPROVED NARRATION
"You thought Fletcher’s Carnegie Hall invitation was redemption, but it was actually a meticulously planned public execution. Notice what happens the moment Andrew steps up to the kit. Fletcher calls a chart they’ve never practiced, ensuring complete professional collapse in front of the industry elite. He didn’t bring Andrew back to greatness. He brought him back to destroy him on stage. But Andrew doesn't break. He absorbs the trap, takes the tempo, and turns a public humiliation into an unstoppable hostile takeover. Which movie villain had the most psychological control over the protagonist? Tell me in the comments."

---
## 2. CREATIVE DIRECTION
### Visual identity
Deep blacks, controlled stage lighting, harsh spotlight isolation, high contrast, warm amber key lights, sharp subject separation, sweat and drumhead texture close-ups, subtle 35mm film grain.
### Visual principle
**Every narration line must have a visually meaningful counterpart.**

---
## 3. SENTENCE-LEVEL VISUAL STORYTELLING

### SHOT 1 — THE HOOK (0–5s)
- **Narration:** You thought Fletcher’s Carnegie Hall invitation was redemption, but it was actually a meticulously planned public execution.
- **Visual direction:** Slow push-in on Fletcher (J.K. Simmons) standing on the Carnegie Hall podium, holding his baton in silhouette against harsh stage lights. High contrast, desaturated background.
- **Typography / Graphic Callout:** A METICULOUSLY PLANNED EXECUTION.

### SHOT 2 — THE SETUP (5–12s)
- **Narration:** Notice what happens the moment Andrew steps up to the kit.
- **Visual direction:** Medium shot of Andrew (Miles Teller) sitting down at the Ludwig drum kit, tightening his sticks, looking up with fragile confidence. Shallow depth of field.
- **Typography / Graphic Callout:** THE TRAP IS SET.

### SHOT 3 — THE BETRAYAL (12–22s)
- **Narration:** Fletcher calls a chart they’ve never practiced, ensuring complete professional collapse in front of the industry elite.
- **Visual direction:** Close-up on Fletcher leaning in close to Andrew, whispering the false song title with a cold, malicious smile. Cut to wide shot of the grand auditorium filled with tuxedo-clad critics.
- **Typography / Graphic Callout:** THE WRONG CHART.

### SHOT 4 — THE INTENT (22–32s)
- **Narration:** He didn’t bring Andrew back to greatness. He brought him back to destroy him on stage.
- **Visual direction:** Rack focus from Fletcher's gloating eyes back to Andrew’s face, catching the sudden realization of betrayal. High-contrast side lighting highlighting jaw tension.
- **Typography / Graphic Callout:** NOT REDEMPTION. DESTRUCTION.

### SHOT 5 — THE TURN (32–42s)
- **Narration:** But Andrew doesn't break. He absorbs the trap, takes the tempo, and turns a public humiliation into an unstoppable hostile takeover.
- **Visual direction:** Rapid-fire matching close-ups: hands gripping drumsticks, foot hitting the bass pedal, sweat flying off cymbals. Aggressive, rhythm-synced cuts matching the building cadence.
- **Typography / Graphic Callout:** THE HOSTILE TAKEOVER.

### SHOT 6 — THE PAYOFF (42–47s)
- **Narration:** He didn’t just survive. He stole the room.
- **Visual direction:** Low-angle hero shot of Andrew locking eyes with Fletcher, initiating the rogue drum solo without Fletcher's cue. Fletcher's expression shifts from triumph to sheer shock.
- **Typography / Graphic Callout:** THE DRUMMER TAKES CONTROL.

### SHOT 7 — COMMENT PROMPT (47–50s)
- **Narration:** Which movie villain had the most psychological control over the protagonist? Tell me in the comments.
- **Visual direction:** Slow pull-back on Andrew mid-solo under blinding white spotlights, fading to deep Cinema Decoded black slate.
- **Typography / Graphic Callout:** TELL ME IN THE COMMENTS.

---
## 4. FOOTAGE RESEARCH AND ACQUISITION
- **Scene 1:** Carnegie Hall Finale (Act 3 climax, approximately 01:38:00 to 01:44:00).
- **Required Assets:** 
  - `WHIPLASH_FINALE_FLETCHER_WHISPER.mp4`
  - `WHIPLASH_ANDREW_KIT_SIT_DOWN.mp4`
  - `WHIPLASH_CROWD_AUDITORIUM_WIDE.mp4`
  - `WHIPLASH_DRUM_SOLO_MACRO_SHOTS.mp4`
- **Directory Path:** `/assets/master_footage/whiplash/carnegie_hall_climax/`

---
## 5. MOTION AND EDITING
- **Pacing:** Strict adherence to spoken rhythm. Cuts land precisely on the beat during the drum sequence.
- **Camera Moves:** Controlled, heavy push-ins during psychological realizations. Snap zooms locked to Fletcher's dialogue beats.
- **Transitions:** Pure hard cuts. No optical wipes or digital distortion.

---
## 6. AUDIO GENERATION — STRICT RESTRICTIONS
- **Voice Profile:** Confident documentary voice, measured cadence, authoritative tone (Match Achird profile).
- **Sound Design:** 
  - Clean isolated snare drum hits and cymbal crashes boosted slightly beneath the narration during the turn.
  - Room tone of Carnegie Hall layered low under dialogue.
- **ABSOLUTELY PROHIBITED SOUND EFFECTS:** ZERO whooshes, swooshes, risers, sweeps, or transition impacts. Clean acoustic space only.
- **Master Audio:** Silence floor <= -65 dB. Dialogue normalized to -14 LUFS.

---
## 7. CAPTIONS AND GRAPHICS
- **Style:** CenterBold high-contrast synchronized subtitles.
- **Color Palette:** Pure white text with gold (#D4AF37) highlights for key thematic words (*EXECUTION*, *BETRAYAL*, *TAKEOVER*).
- **Placement:** Exact vertical center-safe zone for 9:16 aspect ratio, avoiding TikTok/Reels UI obstruction zones.

---
## 8. TECHNICAL IMPLEMENTATION
Workflow sequence: 
`APPROVED NARRATION` -> `SENTENCE PARSER` -> `SCENE JSON` -> `TIMING ENGINE` -> `FOOTAGE MAPPING` -> `CLEAN AUDIO GENERATION` -> `CAPTION GENERATION` -> `REMOTION / FFMPEG 8K RENDERING` -> `QUALITY CONTROL`.

---
## 9. RENDER REQUIREMENTS
- **Primary Master:** 8K Vertical Master (4320x7680) @ 30 FPS, Apple ProRes 422 HQ.
- **Delivery Copy:** 1080p Web Deliverable (1080x1920) @ 30 FPS, H.265 / MP4, 20 Mbps CBR.

---
## 10. FINAL QUALITY CONTROL
- [ ] Story check: Does the script debunk the surface-level redemption narrative immediately?
- [ ] Visual check: Do all 7 shots map cleanly to the sentence-level breakdown?
- [ ] Audio check: Are there zero prohibited whooshes or risers? Is the silence floor below -65 dB?
- [ ] Technical check: Is resolution verified at true 8K master output?

---
## 11. FINAL DELIVERABLES
1. `whiplash_carnegie_8k_master.mov`
2. `whiplash_carnegie_1080p_vertical.mp4`
3. `whiplash_isolated_voiceover.wav`
4. `whiplash_stems_dialogue_sfx.zip`
5. `whiplash_srt_captions.srt`
6. `whiplash_json_timeline_data.json`
7. `whiplash_thumbnail_concept_01.png`
8. `whiplash_thumbnail_concept_02.png`
9. `qc_audio_spectrum_report.txt`
10. `execution_manifest.md`

## FINAL CREATIVE STANDARD
High contrast. Immersive visuals. Precise storytelling. True 8K output verification. No whoosh sounds.