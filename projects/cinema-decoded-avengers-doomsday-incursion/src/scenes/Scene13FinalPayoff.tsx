import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene13FinalPayoff: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/multiverse_colliding_jump.mp4"
    sourceStart={35.0}
    duration={duration}
    callout="THE MULTIVERSE IS THE BATTLEFIELD."
    motion="SLOW_PUSH_IN"
  />
);
