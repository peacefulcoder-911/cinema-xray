import React from "react";
import { useCurrentFrame } from "remotion";
import subtitleCards from "../subtitles.json";

interface SubtitleCard {
  start: number;
  end: number;
  text: string;
  highlight: string;
}

export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const currentTime = frame / 30;

  const activeCard: SubtitleCard | undefined = subtitleCards.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  if (!activeCard) {
    return null;
  }

  const { text, highlight } = activeCard;
  const parts = highlight ? text.split(new RegExp(`(${highlight})`, "gi")) : [text];

  return (
    <div
      style={{
        position: "absolute",
        bottom: 360,
        left: 60,
        right: 60,
        textAlign: "center",
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      <span
        style={{
          fontFamily: "Futura, 'Arial Bold', sans-serif",
          fontWeight: 900,
          fontSize: 74,
          lineHeight: 1.15,
          color: "#FFFFFF",
          textTransform: "uppercase",
          letterSpacing: 3,
          textShadow:
            "-4px -4px 0 #0A0A0A, 4px -4px 0 #0A0A0A, -4px 4px 0 #0A0A0A, 4px 4px 0 #0A0A0A, 0 6px 12px rgba(0,0,0,0.8)",
        }}
      >
        {parts.map((part, i) => {
          const isHighlight = highlight && part.toUpperCase() === highlight.toUpperCase();
          return (
            <span
              key={i}
              style={{
                color: isHighlight ? "#00FFFF" : "#FFFFFF",
              }}
            >
              {part}
            </span>
          );
        })}
      </span>
    </div>
  );
};

