import React from "react";
import { Composition, Sequence, Audio, staticFile } from "remotion";
import { CinematicFrame } from "./components/CinematicFrame";
import { Subtitles } from "./components/Subtitles";
import scenePlan from "../scene_plan.json";

export const GodzillaMinusOneVideo: React.FC = () => {
  const fps = scenePlan.fps || 30;
  const scenes = scenePlan.scenes || [];

  return (
    <div style={{ flex: 1, backgroundColor: "#000000", width: 1080, height: 1920 }}>
      {/* Master Audio Track: Conversational Liam Narration (EBU R128 -14 LUFS) */}
      <Audio src={staticFile("narration/master_narration.wav")} />

      {/* 14 Word-Matched Storyboard Scenes with 70% Active Framing & Soft Ambient Blur */}
      {scenes.map((scene: any) => {
        const startFrame = Math.round(scene.start_sec * fps);
        const durationInFrames = Math.round(scene.duration_sec * fps);

        return (
          <Sequence
            key={scene.id}
            from={startFrame}
            durationInFrames={durationInFrames}
            name={`${scene.id}: ${scene.narration.substring(0, 30)}...`}
          >
            <CinematicFrame
              sourceFile={scene.source_file}
              sourceStart={scene.source_start}
              duration={scene.duration_sec}
              callout={scene.callout}
              calloutY={340}
              motion={scene.camera_movement}
            />
          </Sequence>
        );
      })}

      {/* Synchronized High-Contrast Mobile Captions */}
      <Subtitles />
    </div>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="GodzillaMinusOneTitleExplanation"
      component={GodzillaMinusOneVideo}
      durationInFrames={Math.round(scenePlan.total_duration * (scenePlan.fps || 30))}
      fps={scenePlan.fps || 30}
      width={1080}
      height={1920}
    />
  );
};
