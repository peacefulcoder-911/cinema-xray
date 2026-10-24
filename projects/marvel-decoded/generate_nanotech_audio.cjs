const { ElevenLabsClient } = require('@elevenlabs/elevenlabs-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

// Voice: Charlie (Deep, Confident, Energetic) - IKne3meq5aSn9XLyUdCD
const VOICE_ID = 'IKne3meq5aSn9XLyUdCD'; 

const client = new ElevenLabsClient();

const scriptText = 
  "Ever notice the terrifying detail in Tony Stark's nanotech suit in Infinity War? " +
  "When Tony taps his chest, billions of nanobots swarm his body in seconds. " +
  "It looks like pure comic book magic. " +
  "Except... it obeys one brutal law of physics: the Conservation of Mass. " +
  "Every single nanobot is stored inside that small arc reactor housing. " +
  "The suit cannot create new particles out of thin air. " +
  "So when Thanos blasts him with the Power Stone, watch Tony's legs. " +
  "The armor literally strips his lower body to reinforce his shield. " +
  "And in his final stand, when he forms a blade to strike Thanos, " +
  "his helmet dissolves to supply the metal... " +
  "leaving his head completely unprotected. " +
  "Tony Stark wasn't invincible. " +
  "With every hit, he was actively deciding which organ he was willing to sacrifice next.";

async function generate() {
  console.log("Generating ElevenLabs voiceover for Nanotech Decoded...");
  console.log("Voice ID:", VOICE_ID);

  const audioStream = await client.textToSpeech.convert(VOICE_ID, {
    text: scriptText,
    modelId: 'eleven_flash_v2_5',
    voiceSettings: {
      stability: 0.45,
      similarityBoost: 0.85,
      speed: 1.14
    }
  });

  const outDir = '/Users/vinaybt/Downloads/marvel-decoded/audio';
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const outMp3 = path.join(outDir, 'nanotech_voiceover.mp3');
  const fileStream = fs.createWriteStream(outMp3);

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

module.exports = { generate, scriptText };
