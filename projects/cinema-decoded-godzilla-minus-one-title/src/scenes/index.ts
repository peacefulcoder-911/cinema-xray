import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const HookScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={97.0}
    duration={duration}
    callout="WHY MINUS ONE?"
    motion="SLOW_PUSH_IN"
  />
);

export const PostWarScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={6.5}
    duration={duration}
    callout="AFTER WORLD WAR II"
    motion="SLOW_PUSH_IN"
  />
);

export const DestroyedCityScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={18.0}
    duration={duration}
    callout="CITIES DESTROYED"
    motion="FAST_ZOOM"
  />
);

export const RebuildingScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_netflix.mp4"
    sourceStart={13.5}
    duration={duration}
    callout="TRYING TO REBUILD"
    motion="SLOW_PUSH_IN"
  />
);

export const ZeroGraphic: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={21.0}
    duration={duration}
    callout="0"
    motion="SLOW_PAN_RIGHT"
  />
);

export const GodzillaReveal: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={34.5}
    duration={duration}
    callout="GODZILLA"
    motion="FAST_ZOOM"
  />
);

export const DestructionScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={43.0}
    duration={duration}
    callout={null}
    motion="SLOW_PUSH_IN"
  />
);

export const MinusOneGraphic: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={60.0}
    duration={duration}
    callout="0 → -1"
    motion="SLOW_PAN_LEFT"
  />
);

export const EndingScene: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/godzilla_minus_one_trailer_02.mp4"
    sourceStart={104.0}
    duration={duration}
    callout={null}
    motion="SLOW_PUSH_IN"
  />
);
