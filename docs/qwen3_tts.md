# Qwen3-TTS


## Resources:
- [Qwen3 Workflow Examples](../qwen3_tts/output/workflows)
- [ComfyUI]
- ComfyUI Plugins:
    - [ComfyUI Manager](https://github.com/Comfy-Org/ComfyUI-Manager)
    - ~~[wanaigc ComfyUI-Qwen3-TTS](https://github.com/wanaigc/ComfyUI-Qwen3-TTS)~~
    - [Flybirdxx ComfyUI-Qwen-TTS](https://github.com/flybirdxx/ComfyUI-Qwen-TTS)
    - [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper)


## Build with Qwen3-TTS w/ Docker:
```
docker compose -f qwen3-compose.yaml build --no-cache
```

## Run w/ Docker Compose:
```
docker compose -f qwen3-compose.yaml up
```

## Stop Docker Compose:
```
docker compose -f qwen3-compose.yaml down

```


## Intended Workflows & Endpoints:
- Add Audio File:
    - Description: Upload audio file for voice cloning / transcription
    - add a .wav or .mp3 audio file
    - Transcribe Audio using whisper
    - Save output to be reusable (.qvp file)
- Generate TTS As Voice Profile (include instructions)
    - Description: Identify a Voice Profile to use (.qvp), instructions (emotions may be separate from instructions), text 
    - save output as .wav file


app/
├── core/
│   ├── qwen3_engine.py       <-- Qwen3 model lifecycle
│   ├── speech_to_text.py     <-- Whisper abstraction
│   └── voice_profiles.py     <-- .qvp management later
│
├── commands/
│   ├── clone.py              <-- CLI orchestration
│   ├── transcribe.py
│   └── generate.py




| Current              | New                   | Purpose                                |
| -------------------- | --------------------- | -------------------------------------- |
| Voice Profile        | Character             | A reusable AI persona                  |
| Create Voice Profile | Create Character      | Build a character from reference audio |
| Generate TTS         | Roleplay              | Generate dialogue as a character       |
| Voice Clone          | Character Voice Clone | The underlying Qwen mechanism          |
| Voice Manager        | Character Manager     | Manages stored characters              |


app/
├── core/
│   ├── character_manager.py      <-- Character lifecycle
│   ├── qwen3_engine.py           <-- Qwen3 wrapper only
│   ├── speech_to_text.py         <-- Whisper wrapper only
│   ├── roleplay.py               <-- Generate speech as character
│   └── characters/
│       ├── models.py             <-- CharacterResult dataclasses
│       └── storage.py            <-- Optional filesystem handling