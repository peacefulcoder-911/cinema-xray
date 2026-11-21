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
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.06], { extrapolateRight: "clamp" });
  } else if (motion === "FAST_ZOOM") {
    scale = interpolate(frame, [0, totalFrames], [1.0, 1.14], { extrapolateRight: "clamp" });
  } else if (motion === "SLOW_PAN_LEFT" || motion === "SLOW_PAN_RIGHT") {
    scale = interpolate(frame, [0, totalFrames], [1.02, 1.07], { extrapolateRight: "clamp" });
  } else if (motion === "SLOW_ZOOM_OUT") {
    scale = interpolate(frame, [0, totalFrames], [1.06, 1.00], { extrapolateRight: "clamp" });
  }

  const normalizedFile = sourceFile.replace(/^assets\//, "");

  return (
    <div style={{ position: "relative", width: 1080, height: 1920, overflow: "hidden", backgroundColor: "#000000" }}>
      {/* Background: Soft Ambient Gaussian Blur */}
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

      {/* Foreground: 70% Active Cinematic Framing (1080x1344) placed Y=288 */}
      <div
        style={{
          position: "absolute",
          top: 288,
          left: 0,
          width: 1080,
          height: 1344,
          overflow: "hidden",
          boxShadow: "0 0 60px rgba(0,0,0,0.9)",
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
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      </div>

      {/* Cinematic Gold Divider Bars */}
      <div
        style={{
          position: "absolute",
          top: 287,
          left: 0,
          width: 1080,
          height: 2,
          backgroundColor: "rgba(255, 183, 3, 0.85)",
          boxShadow: "0 0 16px rgba(255, 183, 3, 0.95)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 1632,
          left: 0,
          width: 1080,
          height: 2,
          backgroundColor: "rgba(255, 183, 3, 0.85)",
          boxShadow: "0 0 16px rgba(255, 183, 3, 0.95)",
        }}
      />

      {/* Callout Badge */}
      {callout && (
        <div
          style={{
            position: "absolute",
            top: calloutY,
            left: 0,
            width: 1080,
            display: "flex",
            justifyContent: "center",
            zIndex: 40,
          }}
        >
          <div
            style={{
              backgroundColor: "rgba(12, 12, 16, 0.94)",
              border: "2px solid rgba(255, 183, 3, 0.90)",
              borderRadius: 8,
              padding: "10px 24px",
              boxShadow: "0 8px 32px rgba(0,0,0,0.9), 0 0 16px rgba(255, 183, 3, 0.4)",
            }}
          >
            <span
              style={{
                fontFamily: "Arial Bold, Futura, sans-serif",
                fontSize: callout.length > 20 ? 30 : 40,
                fontWeight: 900,
                color: "#ffdd44",
                letterSpacing: 2,
                textTransform: "uppercase",
              }}
            >
              {callout}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
