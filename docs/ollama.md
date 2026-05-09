# Ollama Notes

## Resources:
- [ollama](https://ollama.com/)
- models saved to `/usr/share/ollama/manifests/registry.ollama.ai/library`


## Examples:
- [ollama.sh](../code/ollama.sh)

## Create a new model based on .mf configuration
```
ollama create DungeonMaster -f chatbots/DungeonMaster.mf
```

## Run new model with prompt from terminal
```
ollama run DungeonMaster "Act as a drunk pirate and tell me where the treasure is."
```

# Default Location on Linux
When running as a service, Ollama uses its own system user. You can find the models here:
` /usr/share/ollama/.ollama/models`

Inside that folder, you’ll see:
* **/manifests:** Small text files that describe the model (metadata).
* **/blobs:** The actual "meat" of the model (the massive multi-gigabyte files). These have cryptic names like `sha256:abc123...` for deduplication.

---

### How to see them (Permission Tip)
Because that folder is owned by the `ollama` system user, you might get a "Permission Denied" if you try to browse it normally. Use `sudo` to peek inside:
```bash
sudo ls -lh /usr/share/ollama/.ollama/models
```

---

### Moving Models to a Different Drive
Since AI models are huge (Llama 3.1 8B is ~4.7GB), you might want to move them if your root partition is getting full.

1.  **Stop the service:** `sudo systemctl stop ollama`
2.  **Move the folder:** `sudo mv /usr/share/ollama/.ollama/models /path/to/your/big/drive/`
3.  **Update the "Jail" (Service Override):**
    Remember the `systemctl edit` command we used for privacy? Use it again:
    ```bash
    sudo systemctl edit ollama.service
    ```
4.  **Add the new path** under the `[Service]` section:
    ```ini
    Environment="OLLAMA_MODELS=/path/to/your/big/drive/models"
    ```
5.  **Restart:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    ```

### Is your storage getting tight?
If you're worried about disk space, you can always delete models you aren't using anymore with:
`ollama rm model_name` (e.g., `ollama rm llama3.1:8b`). This is cleaner than deleting files manually from the `/blobs` folder!


---

# Additional Information:

You can configure personalities in two ways: **permanently** (by creating a new "custom model") or **dynamically** (per character in Foundry).

Since you are using Foundry VTT, you will likely use both: a "custom model" for your general DMing style, and "per-actor" prompts for specific NPCs.

---

## 1. The Permanent Way: Creating a "Custom Model"

You can use a **Modelfile** to create a specialized version of Llama 3.1 that always acts like a Dungeon Master. This is the most efficient way to use it across different Foundry worlds.

1. **Create a file** in your home folder named `DMModel.mf`.
    
2. **Paste this configuration** into it:
    
    Dockerfile
    
    ```
    FROM llama3.1:8b
    
    # Lower temperature makes it more consistent with rules
    PARAMETER temperature 0.7
    
    # The 'Brain' of the model
    SYSTEM """
    You are an expert Tabletop RPG Game Master. Your goal is to help the user 
    manage a fantasy world. You are creative, but you stick to the logic 
    of the setting. When asked for dialogue, provide it in character. 
    When asked for stats, use a clean Markdown table.
    """
    ```
    
3. **Build your new model:** Open your terminal and run:
    
    Bash
    
    ```
    ollama create MyDM -f DMModel.mf
    ```
    
4. **Use it:** Now, in Foundry, instead of selecting `llama3.1:8b`, you select **`MyDM`**. It will now always "wake up" in DM mode.
    
---


## 2. The Dynamic Way: Per-NPC in Foundry

Most Foundry AI modules (like **RPGX AI Assistant** or **UnKenny**) allow you to set a **"System Prompt"** or **"Preamble"** for every single Actor.

- **Global Persona:** Set the main module settings to be your "DM Assistant."
    
- **Specific NPC Persona:** Open an NPC's character sheet. Most modules add a tab or a button called "AI Settings" or "Modify UnKennyness."
    
    - **Preamble/Prompt Example:** _"You are Kaelen, a nervous elven alchemist. You stutter when you lie and you are obsessed with rare mushrooms. You refuse to talk about the local Baron."_
        

---

## 3. Recommended "Dials and Knobs"

Whether you are editing a Modelfile or module settings, these two settings change the "feel" of the personality most:

- **Temperature:**
    
    - **0.3:** Very literal, great for rule checks and stat blocks.
        
    - **0.8:** The "Sweet Spot" for balanced roleplay.
        
    - **1.2+:** Wildly creative, but might start forgetting the rules or talking nonsense.
        
- **Top_P:**
    
    - **Lower (0.5):** More focused and "sensible."
        
    - **Higher (0.9):** More diverse vocabulary and "flair."
        


# Chat Agents

You are spot on—**OpenClaw** is a major part of the local AI conversation in 2026, but it is fundamentally different from a standard "chatbot."

### What is OpenClaw?
If **Ollama** is the "brain" (the model), **OpenClaw** is the "hands." 
* **It’s an Agent, not just a Chatbot:** While a chatbot just talks to you, an agent can *do* things. OpenClaw can browse your local files, execute shell commands, check your calendar, or send messages via Telegram/Discord.
* **Autonomous:** It can be programmed to perform background tasks (like monitoring a folder or a website) without you talking to it first.

---

### Is OpenClaw what you want for Foundry?
Probably not for your **NPCs**, but maybe for **you** as a GM.
* **For NPCs:** Stick to **Open WebUI**. It’s designed for human-to-AI conversation and roleplay. It has a clean, ChatGPT-like interface that stays in your browser.
* **For Your Workstation:** Use **OpenClaw** if you want a local assistant that can help you organize your campaign notes, automate prep tasks, or even run a Discord bot for your players while you aren't there.

---

### How to run a Chatbot right now (The "Safe" Way)
Since you are on Manjaro and want to keep things air-capped, I recommend **Open WebUI** over OpenClaw for your first "chatbot" experience. It is much more secure because it has built-in user authentication.

#### 1. Quick Start: The Terminal Chat
You already have everything needed to chat right now. Open your terminal and type:
```bash
ollama run llama3.1:8b
```
*This is the purest "local chatbot" experience. No browser, no internet, just you and the AI.*

#### 2. The Modern GUI: Open WebUI
If you want the full "Local ChatGPT" interface (including character profiles and history):
1.  **Install it** (e.g., via Docker or Python):
    ```bash
    pip install open-webui
    ```
2.  **Launch it:**
    ```bash
    open-webui serve
    ```
3.  **Access it:** Open your browser to `http://localhost:8080`.

---

### ⚠️ Warning about OpenClaw on Manjaro
Because OpenClaw can execute terminal commands (the "Hands" part), it is much more dangerous to leave unconfigured. 
* **The "Jail" Issue:** If you haven't locked down your permissions, a rogue prompt could technically tell OpenClaw to delete files on your Linux machine. 
* **Privacy:** OpenClaw is designed to connect to messaging apps (Telegram, WhatsApp). If your goal is to stay **air-capped**, OpenClaw’s best features will be disabled because it thrives on those external connections.

**Verdict:** * Use **Open WebUI** for your Foundry NPC roleplay and general chatting. 
* Use **OpenClaw** only if you want an AI "intern" to manage your Linux files and automate your life.

Would you like the specific command to launch OpenClaw via Ollama to see the difference, or would you prefer to stick to the more "roleplay-friendly" Web interfaces?