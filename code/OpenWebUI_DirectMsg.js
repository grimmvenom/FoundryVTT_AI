/*
Summary: JavaScript script for Foundry VTT to chat / query Open WebUI service running on the same local network.
API key is saved in a journal document with limited access.
*/

const JOURNAL_NAME = "AI Config";
const API_URL = "http://192.168.7.7:9000/api/chat/completions";
const MODEL_ID = "dungeonmaster"; 
const DEBUG_MODE = false; 

// Add as many Collection IDs as you need to this list
const COLLECTION_IDS = [
    "Characters"
];

const configJournal = game.journal.getName(JOURNAL_NAME);
if (!configJournal) {
    ui.notifications.error(`Journal "${JOURNAL_NAME}" not found.`);
} else {
    const rawContent = configJournal.pages.contents[0].text.content;
    const apiKey = rawContent.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, '').trim();

    new Dialog({
      title: `DM Archive (${DEBUG_MODE ? 'DEBUG ACTIVE' : 'Ready'})`,
      content: `<textarea id="ai-prompt" style="width:100%; height:100px; font-family: 'Signika', sans-serif;" placeholder="Ask a question..."></textarea>`,
      buttons: {
        generate: {
          icon: '<i class="fas fa-book-sparkles"></i>',
          label: "Query Archives",
          callback: async (html) => {
            const userPrompt = html.find('#ai-prompt').val();
            if (!userPrompt) return;

            ui.notifications.info(`Searching ${COLLECTION_IDS.length} collections...`);

            // Format the collections for the Open WebUI API
            const filePayload = COLLECTION_IDS.map(id => ({
                type: "collection",
                id: id
            }));

            try {
              const payload = {
                model: MODEL_ID,
                messages: [
                    { 
                        role: "system", 
                        content: "If the user provides a roleplay prompt, prioritize the persona requested. Only use archive data if the specific character name is mentioned." 
                    },
                    { 
                        role: "user", 
                        content: userPrompt 
                    }
                ],
                stream: false,
                citations: true,
                files: filePayload,
                rag: {
                    k: 10, // Pulling more chunks since we have multiple collections
                    r: 0.5,
                    template: "Documents:\n{{context}}\n\nQuestion: {{query}}"
                }
              };

              if (DEBUG_MODE) console.log("API Request Payload:", payload);

              const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${apiKey}`
                },
                body: JSON.stringify(payload)
              });

              const data = await response.json();
              
              if (DEBUG_MODE) console.log("API Raw Response:", data);

              if (!response.ok) {
                  throw new Error(data.detail || "API Error");
              }

              const aiReply = data.choices[0].message.content;

              // Main Chat Output
              ChatMessage.create({
                speaker: { alias: "DM Assistant" },
                content: `
                <div style="background: #fdf6e3; border: 2px solid #c9ad6a; padding: 10px; border-radius: 3px; font-family: serif;">
                    <h3 style="margin-top:0; border-bottom: 1px solid #c9ad6a; font-variant: small-caps;">Result</h3>
                    ${aiReply.replace(/\n/g, '<br>')}
                </div>`
              });

              // Debug Whisper to GM
              if (DEBUG_MODE) {
                  const sourceCount = data.sources?.length || 0;
                  const sourceNames = data.sources?.map(s => s.document?.metadata?.name || "Unknown File").join(", ");
                  
                  ChatMessage.create({
                    speaker: { alias: "Debug Monitor" },
                    whisper: ChatMessage.getWhisperRecipients("GM"),
                    content: `
                        <div style="font-size: 0.8em; line-height: 1.2em; color: #555;">
                            <b>Debug Info:</b><br>
                            Sources Found: ${sourceCount}<br>
                            Files hit: ${sourceNames || "None"}<br>
                            <i>Check F12 console for full metadata.</i>
                        </div>`
                  });
              }

            } catch (err) {
              ui.notifications.error(`Error: ${err.message}`);
              console.error("Macro Error:", err);
            }
          }
        }
      }
    }).render(true);
}