import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene09HumanConsequences: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/multiverse_colliding_jump.mp4"
    sourceStart={22.0}
    duration={duration}
    callout="BILLIONS AT STAKE"
    motion="SLOW_PUSH_IN"
  />
);
