# Foundry AI Assistant

The goal of this project is to build a semi-air gapped AI to support my Foundry VTT D&D sessions.

## Approach:
- Using Docker:
    - [x] Build an Airgapped AI Service using [ollama](https://ollama.com/)
    - [x] Build an AI Dashboard using [open WebUI](https://github.com/open-webui/open-webui)
    - [x] ComfyUI for [qwen3](https://github.com/DarioFT/ComfyUI-Qwen3-TTS)
    - [x] Build an audio TTS system for custom / unique voices for D&D Characters using [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)
    - [x] Integrate AI Prompts & Responses into FoundryVTT
    - [x] Integrate TTS into OpenWeb UI
    - [x] Integrate TTS with FoundryVTT (via script / macro)

<br>

## Topology:
```mermaid
graph LR
    subgraph Docker_Container_Network ["Docker Environment"]
        direction TB
        Mimic["Mimic-TTS"]
        OW["Open WebUI"]
        Ollama["Ollama / Llama 3"]
        qwen["Qwen3"]
        
        OW <--> Ollama
        OW <--> Mimic
        Mimic <--> qwen
    end

    Foundry["Foundry VTT"]
    Mimic <--> Foundry
    %% Connections
    Foundry -->|Prompt AI / Lore Data| OW
    OW -->|Synthesized Audio| Foundry

    %% Styling
    style Docker_Container_Network fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Foundry fill:#ff9900,stroke:#333,color:#fff
    style OW fill:#007bff,stroke:#fff,color:#fff
```

<br>

## Docs:
- Setup Instructions: [Docker Notes](docs/docker.md)
- Service: [Mimic TTS](docs/mimic_tts.md)
- Application: [Mimic Voice](docs/mimic_voice.md)
- Notes:
    - [Open-WebUI](docs/openWebUI.md)
    - [Ollama LLM](docs/ollama.md)

<br>

### Resources:
- Similar project / inspiration: [https://www.youtube.com/watch?v=yik3czBEL2Y](https://www.youtube.com/watch?v=yik3czBEL2Y)
