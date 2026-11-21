import React from "react";
import { Composition, Sequence, Audio, staticFile } from "remotion";
import { CinematicFrame } from "./components/CinematicFrame";
import { Subtitles, SubtitleCard } from "./components/Subtitles";
import scenePlan from "../scene_plan.json";
import subtitleData from "../subtitles.json";

export const TrumanwifetvcommercialVideo: React.FC = () => {
  const cards: SubtitleCard[] = subtitleData.cards || [];
  let accumulatedFrames = 0;

  return (
    <div style={{ position: "relative", width: 1080, height: 1920, backgroundColor: "#000" }}>
      {/* Visual Scenes Sequence */}
      {scenePlan.scenes.map((scene, idx) => {
        const durationFrames = Math.round(scene.duration_sec * 30);
        const fromFrame = accumulatedFrames;
        accumulatedFrames += durationFrames;

        return (
          <Sequence key={scene.id || idx} from={fromFrame} durationInFrames={durationFrames}>
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

      {/* Synchronized Subtitles */}
      <Subtitles cards={cards} />

      {/* Studio Mastered Narration Audio */}
      <Audio src={staticFile("assets/narration/master_narration.wav")} />
    </div>
  );
};

export const RemotionRoot: React.FC = () => {
  const totalFrames = Math.round(scenePlan.total_duration * 30);

  return (
    <Composition
      id="Trumanwifetvcommercial"
      component={TrumanwifetvcommercialVideo}
      durationInFrames={totalFrames}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
