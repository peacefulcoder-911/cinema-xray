import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene01Hook: React.FC = () => {
  return (
    <CinematicFrame
      sourceFile="doctor_strange_watch/strange_watch_crash.mp4"
      sourceStart={19.0}
      duration={4.50}
      callout="DOCTOR STRANGE (2016)"
      calloutY={340}
      motion="SLOW_PUSH_IN"
    />
  );
};

