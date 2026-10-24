# Subtitle writer for Elevator Decoded
content = """[Script Info]
Title: Marvel Decoded - Elevator Fight (Fast Edition)
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,64,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.25,0:00:03.20,Default,,0,0,0,,STEVE STEPS INTO AN ELEVATOR\\NWITH {\\c&H0000E5FF&}TEN ARMED AGENTS{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:03.55,0:00:06.10,Default,,0,0,0,,BEFORE A PUNCH IS THROWN,\\NHE LOOKS AROUND AND ASKS:
Dialogue: 0,0:00:06.35,0:00:08.85,Default,,0,0,0,,{\\c&H0000E5FF&}"DOES ANYONE WANT TO GET OUT?"{\\c&H00FFFFFF&}
Dialogue: 0,0:00:09.10,0:00:11.00,Default,,0,0,0,,WHY OFFER AN EXIT\\NTO AN {\\c&H0000E5FF&}AMBUSH{\\c&H00FFFFFF&}?
Dialogue: 0,0:00:11.15,0:00:13.70,Default,,0,0,0,,STRATEGISTS CALL IT\\NRESETTING THE {\\c&H0000E5FF&}OODA LOOP{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:13.95,0:00:17.40,Default,,0,0,0,,STEVE NOTICED {\\c&H0000E5FF&}SWEATING NECKS{\\c&H00FFFFFF&},\\NAND UNCLIPPED BATONS.
Dialogue: 0,0:00:17.60,0:00:18.85,Default,,0,0,0,,HE KNEW THE ATTACK WAS COMING.
Dialogue: 0,0:00:19.10,0:00:20.80,Default,,0,0,0,,ASKING THEM TO LEAVE\\NWASN'T COURTESY.
Dialogue: 0,0:00:20.95,0:00:22.90,Default,,0,0,0,,IT FORCED TEN BRAINS\\NTO {\\c&H0000E5FF&}SUDDENLY HESITATE{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:23.15,0:00:26.05,Default,,0,0,0,,THAT PAUSE DESTROYED THEIR\\N{\\c&H0000E5FF&}SYNCHRONIZED TIMING{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:26.30,0:00:29.10,Default,,0,0,0,,CAP DIDN'T JUST BEAT THEM\\NWITH {\\c&H0000E5FF&}SUPER STRENGTH{\\c&H00FFFFFF&}.
Dialogue: 0,0:00:29.35,0:00:30.80,Default,,0,0,0,,HE BEAT THEM WITH\\N{\\c&H0000E5FF&}REACTION TIME{\\c&H00FFFFFF&}.
"""
with open("/Users/vinaybt/Downloads/marvel-decoded/script/elevator_fast.ass", "w") as f:
    f.write(content.strip() + "\n")
print("Subtitle written successfully!")
