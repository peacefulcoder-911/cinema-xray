import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene02IncursionTitle: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/incursion_explanation_dr_strange.mp4"
    sourceStart={2.5}
    duration={duration}
    callout="AN INCURSION"
    motion="SLOW_PAN_LEFT"
  />
);
