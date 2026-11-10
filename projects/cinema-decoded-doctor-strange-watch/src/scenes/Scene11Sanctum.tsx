import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene11Sanctum: React.FC = () => {
  return (
    <CinematicFrame
      sourceFile="doctor_strange_watch/strange_ending_broken_watch.mp4"
      sourceStart={38.0}
      duration={7.00}
      callout="TIME CAN NEVER FIX THE PAST"
      calloutY={340}
      motion="SLOW_PUSH_IN"
    />
  );
};

