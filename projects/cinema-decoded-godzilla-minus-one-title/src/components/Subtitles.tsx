import React from "react";
import { useCurrentFrame } from "remotion";
import subtitleData from "../../subtitles.json";

interface SubtitleCard {
  start: number;
  end: number;
  text: string;
  highlight?: string;
}

export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const currentTime = frame / 30;

  const cards: SubtitleCard[] = subtitleData.cards || [];
  const currentCard = cards.find(
    (c) => currentTime >= c.start && currentTime < c.end
  );

  if (!currentCard) {
    return null;
  }

  const words = currentCard.text.split(" ");
  const highlightWord = (currentCard.highlight || "").toUpperCase();

  return (
    <div
      style={{
        position: "absolute",
        bottom: 340,
        left: 50,
        right: 50,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "10px 14px",
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      {words.map((word, idx) => {
        const cleanWord = word.replace(/[^\w-]/g, "").toUpperCase();
        const isHighlight = cleanWord === highlightWord || word.toUpperCase().includes(highlightWord);
        return (
          <span
            key={idx}
            style={{
              fontFamily: "Arial Bold, Impact, Futura, sans-serif",
              fontSize: 68,
              fontWeight: 900,
              textTransform: "uppercase",
              letterSpacing: "0.03em",
              color: isHighlight ? "#ffcc00" : "#ffffff",
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
