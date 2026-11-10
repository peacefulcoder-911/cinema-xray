import React from "react";
import { Composition, Sequence, Audio, staticFile } from "remotion";
import { CinematicFrame } from "./components/CinematicFrame";
import { Subtitles } from "./components/Subtitles";
import scenePlan from "../scene_plan.json";

export const DoctorStrangeVideo: React.FC = () => {
  const fps = scenePlan.fps;
  const beats = scenePlan.beats;

  return (
    <div style={{ flex: 1, backgroundColor: "#000000", width: 1080, height: 1920 }}>
      {/* Master Audio Track: Liam Narration + Ambient Mystic Score (EBU R128 -14 LUFS) */}
      <Audio src={staticFile("narration/master_audio.wav")} />

      {/* 11 Cinematic Storyboard Beats with 70% Active Framing & Soft Ambient Blur */}
      {beats.map((beat, index) => {
        let startFrame = 0;
        for (let i = 0; i < index; i++) {
          startFrame += Math.round(beats[i].duration * fps);
        }
        const durationInFrames = Math.round(beat.duration * fps);

        return (
          <Sequence
            key={beat.beat_id}
            from={startFrame}
            durationInFrames={durationInFrames}
            name={beat.name}
          >
            <CinematicFrame
              sourceFile={beat.source_file}
              sourceStart={beat.source_start}
              duration={beat.duration}
              callout={beat.callout}
              calloutY={beat.callout_y}
              motion={beat.motion}
            />
          </Sequence>
        );
      })}

      {/* Arc Reactor Cyan HUD Lower-Third Subtitles */}
      <Subtitles />
    </div>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DoctorStrangeWatchBreakdown"
      component={DoctorStrangeVideo}
      durationInFrames={Math.round(scenePlan.total_duration * scenePlan.fps)}
      fps={scenePlan.fps}
      width={1080}
      height={1920}
    />
  );
};

