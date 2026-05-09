/**
 * Foundry TTS Macro for Local Kokoro
 * Assign this to a hotbar slot. 
 */

// Quick voice switcher for a Foundry Macro
const voices = ["af_bella", "am_adam", "bm_george", "bf_emma"];
// Use this variable in your 'fetch' body


const speaker = token?.actor?.name || "Narrator";
const text = await new Promise(resolve => {
  new Dialog({
    title: `Speech for ${speaker}`,
    content: `<textarea id="speech-text" style="width:100%; height:100px;"></textarea>`,
    buttons: {
      speak: {
        label: "Speak",
        callback: (html) => resolve(html.find('#speech-text').val())
      }
    }
  }).render(true);
});

if (!text) return;

// Map Actor names to Voice IDs
const voiceMap = {
  "Eldrin": "am_adam",
  "Lira": "af_bella",
  "Barnaby": "bm_george"
};

const selectedVoice = voiceMap[speaker] || "af_sky"; // Fallback voice

fetch("http://192.168.7.XXX:8880/v1/audio/speech", { // Use your Server's LAN IP
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "kokoro",
    input: text,
    voice: selectedVoice
  })
})
.then(res => res.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  // Play for everyone (Foundry Audio Bus)
  AudioHelper.play({src: url, volume: 0.8}, true);
});