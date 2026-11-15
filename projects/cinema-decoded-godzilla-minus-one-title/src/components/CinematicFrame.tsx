import React from "react";
import { OffthreadVideo, staticFile, interpolate, useCurrentFrame } from "remotion";

interface CinematicFrameProps {
  sourceFile: string;
  sourceStart: number;
  duration: number;
  callout?: string | null;
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
  const totalFrames = Math.max(1, Math.round(duration * 30));

  let scale = 1.0;
  if (motion === "SLOW_PUSH_IN") {
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.05], { extrapolateRight: "clamp" });
  } else if (motion === "FAST_ZOOM") {
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.12], { extrapolateRight: "clamp" });
  } else if (motion === "SLOW_PAN_LEFT" || motion === "SLOW_PAN_RIGHT") {
    scale = interpolate(frame, [0, totalFrames], [1.02, 1.06], { extrapolateRight: "clamp" });
  }

  const normalizedFile = sourceFile.replace(/^assets\//, "");

  return (
    <div style={{ position: "relative", width: 1080, height: 1920, overflow: "hidden", backgroundColor: "#000000" }}>
      {/* Background: Soft Ambient Gaussian Blur (boxblur 35:5 equivalent) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          filter: "blur(40px) brightness(0.60) saturate(1.2)",
          transform: "scale(1.15)",
        }}
      >
        <OffthreadVideo
          src={staticFile(normalizedFile)}
          startFrom={Math.round(sourceStart * 30)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>

      {/* Foreground: 70% Active Cinematic Framing (1080x1344) placed Y=288 to Y=1632 */}
      <div
        style={{
          position: "absolute",
          top: 288,
          left: 0,
          width: 1080,
          height: 1344,
          overflow: "hidden",
          borderTop: "2px solid rgba(255, 60, 40, 0.4)",
          borderBottom: "2px solid rgba(255, 60, 40, 0.4)",
          boxShadow: "0 0 50px rgba(0, 0, 0, 0.95)",
        }}
      >
        <div style={{ width: "100%", height: "100%", transform: `scale(${scale})` }}>
          <OffthreadVideo
            src={staticFile(normalizedFile)}
            startFrom={Math.round(sourceStart * 30)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      </div>

      {/* Callout Graphic (High-impact Jack D Films typography) */}
      {callout && (
        <div
          style={{
            position: "absolute",
            top: calloutY,
            left: 60,
            right: 60,
            textAlign: "center",
            padding: callout === "0 → -1" ? "16px 36px" : "12px 28px",
            backgroundColor: "rgba(10, 10, 15, 0.92)",
            border: callout === "0 → -1" ? "2px solid #ff3333" : "1px solid rgba(255, 200, 0, 0.8)",
            borderRadius: 8,
            boxShadow: "0 8px 30px rgba(0, 0, 0, 0.9)",
          }}
        >
          <span
            style={{
              fontFamily: "Arial Bold, Impact, sans-serif",
              fontSize: callout === "0 → -1" ? 54 : 32,
              fontWeight: 900,
              letterSpacing: "0.1em",
              color: callout === "0 → -1" ? "#ff3333" : "#ffcc00",
              textTransform: "uppercase",
              textShadow: "0 2px 10px rgba(0,0,0,0.8)",
            }}
          >
            {callout}
          </span>
        </div>
      )}
    </div>
  );
};
