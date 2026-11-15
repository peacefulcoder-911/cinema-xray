import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene06Destruction: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/incursion_explanation_dr_strange.mp4"
    sourceStart={15.0}
    duration={duration}
    callout="ZERO SURVIVAL"
    motion="SLOW_PAN_LEFT"
  />
);
