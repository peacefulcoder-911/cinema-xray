import React from "react";
import { OffthreadVideo, staticFile, interpolate, useCurrentFrame } from "remotion";

interface CinematicFrameProps {
  sourceFile: string;
  sourceStart: number;
  duration: number;
  callout?: string;
  calloutY?: number;
  motion?: string;
}

export const CinematicFrame: React.FC<CinematicFrameProps> = ({
  sourceFile,
  sourceStart,
  duration,
  callout,
  calloutY = 340,
  motion = "SLOW_PUSH_IN",
}) => {
  const frame = useCurrentFrame();
  const totalFrames = Math.round(duration * 30);

  // Compute zoom scale based on motion mode
  let scale = 1.0;
  if (motion === "SLOW_PUSH_IN") {
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.04], { extrapolateRight: "clamp" });
  } else if (motion === "FAST_ZOOM") {
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.10], { extrapolateRight: "clamp" });
  } else if (motion === "SLOW_PAN_LEFT" || motion === "SLOW_PAN_RIGHT") {
    scale = interpolate(frame, [0, totalFrames], [1.02, 1.05], { extrapolateRight: "clamp" });
  }

  // Strip leading path prefix for staticFile
  const normalizedFile = sourceFile.replace(/^assets\//, "");

  return (
    <div style={{ position: "relative", width: 1080, height: 1920, overflow: "hidden" }}>
      {/* Background: Soft Ambient Gaussian Blur (boxblur 35:5 equivalent) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          filter: "blur(40px) brightness(0.65) saturate(1.2)",
          transform: "scale(1.15)",
        }}
      >
        <OffthreadVideo
          src={staticFile(normalizedFile)}
          startFrom={Math.round(sourceStart * 30)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Foreground: 70% Active Cinematic Framing (1080x1344) placed between Y=288 and Y=1632 */}
      <div
        style={{
          position: "absolute",
          top: 288,
          left: 0,
          width: 1080,
          height: 1344,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            transform: `scale(${scale})`,
            transformOrigin: "center center",
          }}
        >
          <OffthreadVideo
            src={staticFile(normalizedFile)}
            startFrom={Math.round(sourceStart * 30)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      </div>

      {/* Clean Matte Line Dividers */}
      <div style={{ position: "absolute", top: 287, left: 0, width: 1080, height: 2, backgroundColor: "rgba(0,0,0,0.8)" }} />
      <div style={{ position: "absolute", top: 1632, left: 0, width: 1080, height: 2, backgroundColor: "rgba(0,0,0,0.8)" }} />

      {/* Cinematic Callout Badge */}
      {callout && (
        <div
          style={{
            position: "absolute",
            top: calloutY,
            width: "100%",
            textAlign: "center",
            fontFamily: "Arial, sans-serif",
            fontWeight: "bold",
            fontSize: 30,
            color: "#FFFFFF",
            letterSpacing: 2,
            textShadow: "2px 2px 4px rgba(0,0,0,0.9)",
          }}
        >
          {callout.toUpperCase()}
        </div>
      )}
    </div>
  );
};

