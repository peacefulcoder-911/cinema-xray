import React from "react";
import { useCurrentFrame } from "remotion";
import subtitleData from "../../subtitles.json";

interface SubtitleCard {
  start_sec: number;
  end_sec: number;
  highlight_index: number;
  words: string[];
}

export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const currentTime = frame / 30;

  const cards: SubtitleCard[] = subtitleData.cards || [];
  const currentCard = cards.find(
    (c) => currentTime >= c.start_sec && currentTime < c.end_sec
  );

  if (!currentCard) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: 340,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "10px 14px",
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      {currentCard.words.map((word, idx) => {
        const isHighlight = idx === currentCard.highlight_index;
        return (
          <span
            key={idx}
            style={{
              fontFamily: "Arial Bold, Futura, sans-serif",
              fontSize: 66,
              fontWeight: 900,
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              color: isHighlight ? "#00ffff" : "#ffffff",
              textShadow:
                "-3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 3px 3px 0 #000, 0 4px 18px rgba(0,0,0,0.95)",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
