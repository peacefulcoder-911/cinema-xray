import os
import json

SCRIPT_DIR = "/Users/vinaybt/Downloads/interstellar-decoded/script"
os.makedirs(SCRIPT_DIR, exist_ok=True)

# Subtitle styles for 16:9 1920x1080 cinematic video essay
HEADER = """[Script Info]
Title: Interstellar Decoded - Video Essay
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Trebuchet MS,44,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,80,80,80,1
Style: TitleCard,Arial Black,52,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,5,3,5,60,60,60,1
Style: SubTitleCard,Trebuchet MS,32,&H00E0E0E0,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,3,2,5,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Chapter 0: Prologue (38.76s)
c0_events = """
Dialogue: 1,0:00:01.00,0:00:05.50,TitleCard,,0,0,0,,{\\fad(600,600)}THE PHYSICS OF INTERSTELLAR
Dialogue: 1,0:00:01.00,0:00:05.50,SubTitleCard,,0,0,0,,{\\fad(600,600)}When Science Fiction Meets Gravitational Physics
Dialogue: 0,0:00:00.20,0:00:04.80,Default,,0,0,0,,Most science fiction treats the laws of physics as mere suggestions.
Dialogue: 0,0:00:05.20,0:00:10.50,Default,,0,0,0,,But when Christopher Nolan made {\\c&H0000E5FF&}Interstellar{\\c&H00FFFFFF&}, he partnered with Nobel laureate {\\c&H0000E5FF&}Kip Thorne{\\c&H00FFFFFF&}...
Dialogue: 0,0:00:10.90,0:00:15.50,Default,,0,0,0,,To do something unprecedented: they didn't just imagine the cosmos—{\\c&H0000E5FF&}they calculated it{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:16.00,0:00:22.50,Default,,0,0,0,,The visual effects in this film were driven by {\\c&H004EF1F2&}actual gravitational equations{\\c&H00FFFFFF&},
Dialogue: 0,0:00:22.80,0:00:29.80,Default,,0,0,0,,Resulting in simulations so precise they generated {\\c&H0000E5FF&}new peer-reviewed scientific discoveries{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:30.40,0:00:38.20,Default,,0,0,0,,Today, we decode every scientific concept in Interstellar—\\NFrom {\\c&H004EF1F2&}warped spacetime{\\c&H00FFFFFF&} to the {\\c&H0000E5FF&}fifth dimension{\\c&H00FFFFFF&}.
"""

# Chapter 1: Wormhole (50.40s)
c1_events = """
Dialogue: 1,0:00:00.80,0:00:05.20,TitleCard,,0,0,0,,{\\fad(600,600)}CHAPTER 1: THE SPHERICAL WORMHOLE
Dialogue: 1,0:00:00.80,0:00:05.20,SubTitleCard,,0,0,0,,{\\fad(600,600)}Einstein-Rosen Bridges & Spacetime Curvature
Dialogue: 0,0:00:00.20,0:00:05.80,Default,,0,0,0,,Our journey begins near Saturn with an anomaly: a {\\c&H0000E5FF&}wormhole{\\c&H00FFFFFF&},
Dialogue: 0,0:00:06.10,0:00:11.80,Default,,0,0,0,,Formally known in theoretical physics as an {\\c&H004EF1F2&}Einstein-Rosen bridge{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:12.20,0:00:16.50,Default,,0,0,0,,In popular culture, wormholes are portrayed as flat swirling circles.
Dialogue: 0,0:00:16.80,0:00:21.00,Default,,0,0,0,,But in three-dimensional space, {\\c&H0000E5FF&}that is physically impossible{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:21.50,0:00:27.20,Default,,0,0,0,,As physicist Romilly demonstrates with a piece of paper,
Dialogue: 0,0:00:27.50,0:00:32.80,Default,,0,0,0,,If you punch a hole in a 2D sheet, the hole is a {\\c&H0000E5FF&}two-dimensional circle{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:33.20,0:00:39.00,Default,,0,0,0,,Add another spatial dimension, and that circle becomes a {\\c&H004EF1F2&}three-dimensional sphere{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:39.50,0:00:44.20,Default,,0,0,0,,A wormhole in our universe isn't a tunnel you slide down—
Dialogue: 0,0:00:44.50,0:00:50.00,Default,,0,0,0,,It is a {\\c&H0000E5FF&}spherical gateway{\\c&H00FFFFFF&}, reflecting the warped light of a distant galaxy millions of light-years away.
"""

# Chapter 2: Miller's Planet (66.52s)
c2_events = """
Dialogue: 1,0:00:00.80,0:00:05.50,TitleCard,,0,0,0,,{\\fad(600,600)}CHAPTER 2: GRAVITATIONAL TIME DILATION
Dialogue: 1,0:00:00.80,0:00:05.50,SubTitleCard,,0,0,0,,{\\fad(600,600)}Miller's Planet — Where 1 Hour Equals 7 Years
Dialogue: 0,0:00:00.20,0:00:06.00,Default,,0,0,0,,Once through the bridge, the crew lands on {\\c&H0000E5FF&}Miller's planet{\\c&H00FFFFFF&},
Dialogue: 0,0:00:06.30,0:00:11.80,Default,,0,0,0,,Where {\\c&H0000E5FF&}one hour on the surface equals seven Earth years{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:12.20,0:00:17.80,Default,,0,0,0,,This isn't fantasy—it is Einstein's {\\c&H004EF1F2&}General Relativity{\\c&H00FFFFFF&} in its most extreme manifestation.
Dialogue: 0,0:00:18.20,0:00:23.50,Default,,0,0,0,,Gravity is not simply a force; it is the {\\c&H0000E5FF&}physical warping of spacetime{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:23.90,0:00:30.00,Default,,0,0,0,,The deeper you descend into a gravitational well, the slower your clock ticks relative to the outside.
Dialogue: 0,0:00:30.50,0:00:36.50,Default,,0,0,0,,Because Miller's planet skims just outside the event horizon of a supermassive black hole,
Dialogue: 0,0:00:36.80,0:00:42.20,Default,,0,0,0,,{\\c&H004EF1F2&}Time itself is stretched to the breaking point{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:42.80,0:00:48.50,Default,,0,0,0,,And those towering {\\c&H0000E5FF&}four-thousand-foot waves{\\c&H00FFFFFF&}?
Dialogue: 0,0:00:48.80,0:00:53.20,Default,,0,0,0,,They are not tsunamis from earthquakes.
Dialogue: 0,0:00:53.60,0:01:00.00,Default,,0,0,0,,They are {\\c&H004EF1F2&}permanent tidal bulges{\\c&H00FFFFFF&}—colossal gravitational tugs exerted by Gargantua,
Dialogue: 0,0:01:00.40,0:01:06.00,Default,,0,0,0,,Holding walls of water frozen in time.
"""

# Chapter 3: Gargantua (55.08s)
c3_events = """
Dialogue: 1,0:00:00.80,0:00:05.20,TitleCard,,0,0,0,,{\\fad(600,600)}CHAPTER 3: GARGANTUA & GRAVITATIONAL LENSING
Dialogue: 1,0:00:00.80,0:00:05.20,SubTitleCard,,0,0,0,,{\\fad(600,600)}The Anatomy of a Rotating Kerr Black Hole
Dialogue: 0,0:00:00.20,0:00:05.50,Default,,0,0,0,,At the heart of the system looms {\\c&H0000E5FF&}Gargantua{\\c&H00FFFFFF&}:
Dialogue: 0,0:00:05.80,0:00:11.80,Default,,0,0,0,,A supermassive {\\c&H004EF1F2&}Kerr black hole{\\c&H00FFFFFF&} with the mass of 100 million suns,
Dialogue: 0,0:00:12.10,0:00:17.50,Default,,0,0,0,,Spinning at {\\c&H0000E5FF&}99.8 percent the speed of light{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:18.00,0:00:24.00,Default,,0,0,0,,To depict Gargantua, Thorne provided thirty pages of differential equations to the VFX team.
Dialogue: 0,0:00:24.50,0:00:29.80,Default,,0,0,0,,The simulation revealed {\\c&H0000E5FF&}gravitational lensing{\\c&H00FFFFFF&}:
Dialogue: 0,0:00:30.10,0:00:35.20,Default,,0,0,0,,Gravity so extreme it bends the physical path of light rays.
Dialogue: 0,0:00:35.60,0:00:41.50,Default,,0,0,0,,Light emitted behind the black hole is bent {\\c&H004EF1F2&}over the top and under the bottom{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:42.00,0:00:48.50,Default,,0,0,0,,What appears to be a vertical halo is actually the {\\c&H0000E5FF&}backside of the accretion disk{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:49.00,0:00:54.60,Default,,0,0,0,,Interstellar didn't just animate a black hole; {\\c&H0000E5FF&}it computed reality{\\c&H00FFFFFF&}.
"""

# Chapter 4: Tesseract (39.44s)
c4_events = """
Dialogue: 1,0:00:00.80,0:00:05.20,TitleCard,,0,0,0,,{\\fad(600,600)}CHAPTER 4: THE 5TH DIMENSION & THE TESSERACT
Dialogue: 1,0:00:00.80,0:00:05.20,SubTitleCard,,0,0,0,,{\\fad(600,600)}Bulk Hyperspace & Gravity Transcending Time
Dialogue: 0,0:00:00.20,0:00:05.80,Default,,0,0,0,,When Cooper falls through the event horizon, he enters the {\\c&H0000E5FF&}Tesseract{\\c&H00FFFFFF&}—
Dialogue: 0,0:00:06.10,0:00:11.50,Default,,0,0,0,,An interface constructed by {\\c&H004EF1F2&}fifth-dimensional beings{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:11.90,0:00:17.80,Default,,0,0,0,,In modern physics, our four-dimensional universe is embedded within a higher hyperspace called {\\c&H0000E5FF&}'the bulk'{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:18.20,0:00:23.20,Default,,0,0,0,,To a five-dimensional observer, {\\c&H004EF1F2&}time is a physical spatial dimension{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:23.60,0:00:29.00,Default,,0,0,0,,Just as you can walk left or right across a room,
Dialogue: 0,0:00:29.30,0:00:34.50,Default,,0,0,0,,A bulk entity can walk physically between {\\c&H0000E5FF&}yesterday, today, and tomorrow{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:35.00,0:00:39.00,Default,,0,0,0,,The Tesseract allows Cooper to interact across all moments of time.
"""

# Chapter 5: Quantum Gravity (51.44s)
c5_events = """
Dialogue: 1,0:00:00.80,0:00:05.20,TitleCard,,0,0,0,,{\\fad(600,600)}CHAPTER 5: SOLVING QUANTUM GRAVITY
Dialogue: 1,0:00:00.80,0:00:05.20,SubTitleCard,,0,0,0,,{\\fad(600,600)}Unifying Relativity with the Quantum Realm
Dialogue: 0,0:00:00.20,0:00:05.50,Default,,0,0,0,,The grandest unsolved mystery in physics is the rift between {\\c&H004EF1F2&}General Relativity{\\c&H00FFFFFF&},
Dialogue: 0,0:00:05.80,0:00:11.50,Default,,0,0,0,,Which explains the cosmic macro-universe, and {\\c&H004EF1F2&}Quantum Mechanics{\\c&H00FFFFFF&}, which governs atoms.
Dialogue: 0,0:00:12.00,0:00:17.80,Default,,0,0,0,,To solve gravity, Professor Brand needed data from inside a {\\c&H0000E5FF&}gravitational singularity{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:18.20,0:00:24.20,Default,,0,0,0,,By relaying that data through the tick of an old wristwatch,
Dialogue: 0,0:00:24.60,0:00:30.50,Default,,0,0,0,,Cooper bridged {\\c&H0000E5FF&}the infinite and the infinitesimal{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:31.00,0:00:36.80,Default,,0,0,0,,Interstellar proves that science and emotion are not opposites.
Dialogue: 0,0:00:37.20,0:00:43.50,Default,,0,0,0,,Gravity is the only force capable of traversing higher dimensions.
Dialogue: 0,0:00:44.00,0:00:51.00,Default,,0,0,0,,And through gravity, {\\c&H0000E5FF&}our connection to each other transcends both space and time{\\c&H00FFFFFF&}.
"""

chapters = [
    ("chapter_00.ass", c0_events),
    ("chapter_01.ass", c1_events),
    ("chapter_02.ass", c2_events),
    ("chapter_03.ass", c3_events),
    ("chapter_04.ass", c4_events),
    ("chapter_05.ass", c5_events)
]

for fname, events in chapters:
    path = os.path.join(SCRIPT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER + events.strip() + "\n")
    print(f"Written: {path}")

print("All chapter ASS subtitles successfully generated!")
