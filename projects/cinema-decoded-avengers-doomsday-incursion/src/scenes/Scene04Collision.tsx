import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene04Collision: React.FC<{ duration: number }> = ({ duration }) => (
  <CinematicFrame
    sourceFile="assets/footage/multiverse_colliding_jump.mp4"
    sourceStart={10.0}
    duration={duration}
    callout="TWO UNIVERSES"
    motion="SLOW_PAN_RIGHT"
  />
);
