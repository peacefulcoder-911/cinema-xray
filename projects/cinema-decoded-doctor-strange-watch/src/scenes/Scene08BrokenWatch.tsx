import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene08BrokenWatch: React.FC = () => {
  return (
    <CinematicFrame
      sourceFile="doctor_strange_watch/strange_ending_broken_watch.mp4"
      sourceStart={17.0}
      duration={4.18}
      callout="HE CANNOT LET IT GO"
      calloutY={340}
      motion="SLOW_PUSH_IN"
    />
  );
};

