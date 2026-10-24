const { ElevenLabsClient } = require('@elevenlabs/elevenlabs-js');
const fs = require('fs');
const path = require('path');

// Voice: Charlie (Deep, Confident, Energetic) - IKne3meq5aSn9XLyUdCD
// Alternative: Adam (Dominant, Firm) - pNInz6obpgDQGcFmaJgB
const VOICE_ID = 'IKne3meq5aSn9XLyUdCD'; 

const client = new ElevenLabsClient();

const scriptText = 
  "Doctor Strange viewed fourteen million six hundred and five futures... " +
  "and saw only ONE where they won. " +
  "Seconds later, he handed Thanos the most dangerous weapon in the universe. " +
  "Why surrender? " +
  "Game theorists call it Backward Induction. " +
  "Strange knew Thanos was mathematically unstoppable on Titan. " +
  "But more importantly, he knew Tony Stark was the only human mind capable of inventing time travel. " +
  "Surrendering the Time Stone wasn't defeat. " +
  "It was an investment. " +
  "Doctor Strange didn't lose the battle. " +
  "He initiated the endgame.";

async function generate() {
  console.log("Generating ElevenLabs voiceover for Doctor Strange Decoded...");
  console.log("Voice ID:", VOICE_ID);

  const audioStream = await client.textToSpeech.convert(VOICE_ID, {
    text: scriptText,
    modelId: 'eleven_flash_v2_5',
    voiceSettings: {
      stability: 0.45,
      similarityBoost: 0.85,
      speed: 1.12
    }
  });

  const outDir = path.join(__dirname, 'audio');
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const outMp3 = path.join(outDir, 'strange_voiceover.mp3');
  const fileStream = fs.createWriteStream(outMp3);

  // Convert web ReadableStream to Node stream
  const reader = audioStream.getReader ? audioStream.getReader() : null;
  if (reader) {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      fileStream.write(Buffer.from(value));
    }
    fileStream.end();
  } else if (audioStream.pipe) {
    audioStream.pipe(fileStream);
  } else {
    // If it's an async iterable
    for await (const chunk of audioStream) {
      fileStream.write(Buffer.from(chunk));
    }
    fileStream.end();
  }

  await new Promise((resolve, reject) => {
    fileStream.on('finish', resolve);
    fileStream.on('error', reject);
  });

  console.log("Audio written successfully to:", outMp3);
}

if (require.main === module) {
  generate().catch(err => {
    console.error("ElevenLabs Generation Error:", err);
    process.exit(1);
  });
}

module.exports = { generate };
