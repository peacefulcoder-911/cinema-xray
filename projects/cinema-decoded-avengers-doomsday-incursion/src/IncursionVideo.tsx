import React from "react";
import { Composition, Sequence, Audio, staticFile } from "remotion";
import { CinematicFrame } from "./components/CinematicFrame";
import { Subtitles } from "./components/Subtitles";
import scenePlan from "../scene_plan.json";

export const IncursionVideo: React.FC = () => {
  const fps = scenePlan.fps || 30;
  const scenes = scenePlan.scenes || [];

  return (
    <div style={{ flex: 1, backgroundColor: "#000000", width: 1080, height: 1920 }}>
      {/* Master Audio Track: ElevenLabs Liam Narration (EBU R128 -14 LUFS) */}
      <Audio src={staticFile("narration/master_narration.wav")} />

      {/* 13 Cinematic Storyboard Scenes with 70% Active Framing & Soft Ambient Blur */}
      {scenes.map((scene: any, index: number) => {
        const startFrame = Math.round(scene.start_sec * fps);
        const durationInFrames = Math.round(scene.duration_sec * fps);

        // Cycle through authentic footage clips
        const sourceFile =
          index % 2 === 0
            ? "assets/footage/incursion_explanation_dr_strange.mp4"
            : "assets/footage/multiverse_colliding_jump.mp4";

        return (
          <Sequence
            key={scene.id}
            from={startFrame}
            durationInFrames={durationInFrames}
            name={`${scene.id}: ${scene.text_overlay}`}
          >
            <CinematicFrame
              sourceFile={sourceFile}
              sourceStart={index * 2.5}
              duration={scene.duration_sec}
              callout={scene.text_overlay}
              calloutY={340}
              motion={scene.camera_movement}
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
      id="AvengersDoomsdayIncursionVideo"
      component={IncursionVideo}
      durationInFrames={Math.round(scenePlan.total_duration * (scenePlan.fps || 30))}
      fps={scenePlan.fps || 30}
      width={1080}
      height={1920}
    />
  );
};
