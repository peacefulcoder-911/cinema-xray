import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene01Hook: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/multiverse_colliding_jump.mp4"
    sourceStart={0.0}
    duration={duration}
    callout="SAVE ONE. DESTROY ANOTHER."
    motion="SLOW_PUSH_IN"
  />
);
