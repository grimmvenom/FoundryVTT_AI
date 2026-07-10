# Foundry AI Assistant

The goal of this project is to build a semi-air gapped AI to support my Foundry VTT D&D sessions.

## Approach:
- Using Docker:
    - [x] Build an Airgapped AI Service using [ollama](https://ollama.com/)
    - [x] Build an AI Dashboard using [open WebUI](https://github.com/open-webui/open-webui)
    - [x] ComfyUI for [qwen3](https://github.com/DarioFT/ComfyUI-Qwen3-TTS)
    - [ ] Build an audio TTS system for custom / unique voices for D&D Characters using [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)
- [x] Integrate AI Prompts & Responses into FoundryVTT
- [ ] Integrate TTS into OpenWeb UI and FoundryVTT


## Foundry VTT Modules of Interest:
- Integrate AI
- FX Master
- NPC Chatter
- Lootsheet NPC
- RPGX AI - Only supports base ollama connection and not to open WebUI preventing RAG / data lookups without premium

<br>

## Topology:
```mermaid
graph LR
    subgraph Docker_Container_Network ["Docker Environment"]
        direction TB
        OW["Open WebUI"]
        Ollama["Ollama / Llama 3"]
        TTS["Qwen3-TTS"]
        
        OW <--> Ollama
        OW <--> TTS
    end

    Foundry["Foundry VTT"]

    %% Connections
    Foundry -->|Prompt AI / Lore Data| OW
    OW -->|Synthesized Audio| Foundry

    %% Styling
    style Docker_Container_Network fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Foundry fill:#ff9900,stroke:#333,color:#fff
    style OW fill:#007bff,stroke:#fff,color:#fff
```

<br>

### Resources:
- Similar project / inspiration: [https://www.youtube.com/watch?v=yik3czBEL2Y](https://www.youtube.com/watch?v=yik3czBEL2Y)
