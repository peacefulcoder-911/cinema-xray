import React from "react";
import { useCurrentFrame } from "remotion";

export interface SubtitleCard {
  start: number;
  end: number;
  text: string;
  highlight?: string;
}

interface SubtitlesProps {
  cards: SubtitleCard[];
}

export const Subtitles: React.FC<SubtitlesProps> = ({ cards }) => {
  const frame = useCurrentFrame();
  const currentTime = frame / 30;

  const currentCard = cards.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  if (!currentCard) {
    return null;
  }

  const words = currentCard.text.split(" ");
  const cleanHighlight = (currentCard.highlight || "").toUpperCase().replace(/[^A-Z0-9]/g, "");

  return (
    <div
      style={{
        position: "absolute",
        bottom: 340,
        left: 0,
        width: 1080,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 50,
        padding: "0 60px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          fontFamily: "Futura, Arial Black, sans-serif",
          fontSize: 70,
          fontWeight: 900,
          color: "#ffffff",
          textAlign: "center",
          textTransform: "uppercase",
          letterSpacing: 2,
          lineHeight: 1.15,
          textShadow:
            "0 4px 16px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.9), 2px 2px 4px #000000",
        }}
      >
        {words.map((w, idx) => {
          const cleanWord = w.toUpperCase().replace(/[^A-Z0-9]/g, "");
          const isHighlighted = cleanWord === cleanHighlight || (cleanHighlight && cleanWord.includes(cleanHighlight));
          return (
            <span
              key={idx}
              style={{
                color: isHighlighted ? "#ff4499" : "#ffffff",
                textShadow: isHighlighted
                  ? "0 0 24px rgba(255, 68, 153, 0.9), 0 0 8px rgba(255, 255, 255, 0.8)"
                  : undefined,
                margin: "0 8px",
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </div>
  );
};
