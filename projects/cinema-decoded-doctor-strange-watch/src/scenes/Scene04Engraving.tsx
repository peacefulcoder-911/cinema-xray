import React from "react";
import { CinematicFrame } from "../components/CinematicFrame";

export const Scene04Engraving: React.FC = () => {
  return (
    <CinematicFrame
      sourceFile="doctor_strange_watch/strange_watch_crash.mp4"
      sourceStart={25.5}
      duration={3.50}
      callout="THE HIDDEN INSCRIPTION"
      calloutY={340}
      motion="SLOW_PUSH_IN"
    />
  );
};

