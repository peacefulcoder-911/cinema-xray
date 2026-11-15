import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene12ImpossibleChoice: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/incursion_explanation_dr_strange.mp4"
    sourceStart={30.0}
    duration={duration}
    callout="NO EASY VICTORY"
    motion="FAST_ZOOM"
  />
);
