// Create a listener that accepts messages starting with ? as an AI prompt
// Create an actor name 'AI Narrator' and responses will post as that actor.

Hooks.off("chatMessage");

Hooks.on("chatMessage", (chatLog, message, chatData) => {
  const prefix = "?"; 
  const plainText = message.replace(/<\/?[^>]+(>|$)/g, "").trim();
  
  if (plainText.startsWith(prefix)) {
    const prompt = plainText.slice(prefix.length).trim();
    ui.notifications.info("AI is thinking...");

    IntegrateAI.processWithAI(prompt)
      .then(result => {
        let finalText = result?.choices?.[0]?.message?.content || result;
        
        if (finalText) {
          const gmUser = game.users.find(u => u.isGM && u.active) || game.users.find(u => u.isGM);
          
          // --- ICON CUSTOMIZATION ---
          // Option A: Use a specific Actor's portrait (Best way to get a custom icon)
          // Replace "AI Narrator" with the exact name of an Actor in your sidebar
          const aiActor = game.actors.getName("AI Narrator"); 
          
          const messageData = {
            author: gmUser ? gmUser.id : game.user.id,
            content: finalText,
            style: CONST.CHAT_MESSAGE_STYLES.IC,
            speaker: {
              alias: "Dungeon Master AI",
              actor: aiActor?.id || null, // If actor exists, uses its icon
              token: aiActor?.prototypeToken?.id || null
            }
          };

          // Option B: If you don't want to create an actor, 
          // we can manually inject a small CSS style into the content to show an icon
          if (!aiActor) {
            const iconUrl = "assets/images/dnd-logo.png"; // Path to any image in your Foundry data
            messageData.content = `
              <div style="display: flex; align-items: flex-start; gap: 8px;">
                <img src="${iconUrl}" width="32" height="32" style="border:none; border-radius: 4px;">
                <div>${finalText}</div>
              </div>`;
          }

          ChatMessage.create(messageData);
        }
      })
      .catch(err => {
        console.error("AI Listener Error:", err);
        ui.notifications.error("AI Script Error.");
      });

    return false;
  }
});