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



## Interactive Shell Into Docker Container:
"""
docker compose run --rm --entrypoint bash mimic-tts
root@c6c10ae6b5b7:/app#
"""

## Create a Reusable Character Profile / Voice Clone Using an Audio Clip
"""
root@c6c10ae6b5b7:/app# python -m app.cli create-character \
    --audio tts_data/input/louise_voice_actor.wav \
    --name test \
    --instructions "Energetic child voice with playful delivery."

 
Loaded configuration: /app/config/default.ini

============================================================
Creating Character
============================================================
============================================================
Loading Whisper
============================================================
Model:        large-v3
Device:       cuda
Compute type: float16
Whisper loaded successfully
Transcribing: tts_data/input/louise_voice_actor.wav

============================================================
Loading Qwen3-TTS
============================================================
/opt/conda/lib/python3.11/site-packages/torch/cuda/__init__.py:716: UserWarning: Can't initialize NVML
  warnings.warn("Can't initialize NVML")
Qwen3-TTS loaded successfully

Character profile created:
/app/tts_data/characters/test/voice.qvp

============================================================
Character Created
============================================================

Name: test
Voice Profile: /app/tts_data/characters/test/voice.qvp
Transcript: /app/tts_data/characters/test/transcript.txt
Metadata: /app/tts_data/characters/test/metadata.json

"""


# Transcribe An Audio File -> Text
"""
root@c6c10ae6b5b7:/app# python -m app.cli transcribe --audio tts_data/input/louise_voice_actor.wav --output tts_data/output/transcribe_test.txt

********
Warning: flash-attn is not installed. Will only run the manual PyTorch version. Please install flash-attn for faster inference.
********
 
Loaded configuration: /app/config/default.ini
============================================================
Loading Whisper
============================================================
Model:        large-v3
Device:       cuda
Compute type: float16
Whisper loaded successfully
Transcribing: tts_data/input/louise_voice_actor.wav

Transcript:

Yes, you can keep chewing on my sweater. He likes his apple pie warm and his a la mode cold. Good luck. I just made this tuna casserole, and I noticed it had your name on it and jalapeno peppers. Physical fitness is very important to Shannon, as you can tell, right? I just wanted to be like you. Mom told me stories about when you did crimes. I'm an ape. One of Chester V's most brilliant innovations. Well, here's a thought from the old idea factory. What if we go down the mountain on our crevasses together? Who cares what he wanted? He doesn't, because he's dead. And we all know he hated your guts. We're either in a cafe in Paris or a coffee shop in New Jersey. I'm pretty sure I just came back from the doctor with life-changing news. Check it out, Dipper. I successfully bazazzled my face. Blink. Ow. I was disrespectful. I was out of line. And oh my god, did you move that picture? Ah! Ah!

Saved transcript -> tts_data/output/transcribe_test.txt

"""


# TODO:
- Add instructions for roleplay command
- Setup FAST API
- Integrate as TTS