# Qwen3-TTS


# TODO:
- [x] Add instructions for roleplay command
- [x]List Characters
- []Setup FAST API
- [] Integrate as TTS

## Resources:
- [Qwen3 Workflow Examples](../qwen3_tts/output/workflows)
- [ComfyUI]
- ComfyUI Plugins:
    - [ComfyUI Manager](https://github.com/Comfy-Org/ComfyUI-Manager)
    - ~~[wanaigc ComfyUI-Qwen3-TTS](https://github.com/wanaigc/ComfyUI-Qwen3-TTS)~~
    - [Flybirdxx ComfyUI-Qwen-TTS](https://github.com/flybirdxx/ComfyUI-Qwen-TTS)
    - [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper)


## Project Structure:
```
config/
├── default.ini
├── mac.ini

app/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI entrypoint
│   ├── routes/
│   │   ├── characters.py    # character endpoints
│   │   ├── tts.py           # speech generation
│   │   └── health.py
│   └── schemas.py           # Pydantic models
│
├── core/
│   ├── characters/
|   |    ├── manager.py
|   |    ├── models.py
|   |    ├── storage.py
│   ├── qwen3_engine.py
│   ├── speech_to_text.py
│   ├── transcribe.py
│   └── ...
│
└── cli.py
```


## Running With Docker:

### Build with Qwen3-TTS w/ Docker:
```
docker compose -f qwen3-compose.yaml build --no-cache
```

### Run w/ Docker Compose:
```
docker compose -f qwen3-compose.yaml up
```

### Stop Docker Compose:
```
docker compose -f qwen3-compose.yaml down

```

### Interactive Shell Into Docker Container:
"""
docker compose run --rm --entrypoint bash mimic-tts
root@c6c10ae6b5b7:/app#
"""



## Commandline Commands:

### create_character → builds and stores a reusable voice clone prompt (voice_prompt.pt)
- Add Audio File:
    - Description: Upload audio file for voice cloning / transcription
    - add a .wav or .mp3 audio file
    - Transcribe Audio using whisper
    - Save output to be reusable (.qvp file)
- Generate TTS As Voice Profile (include instructions)
    - Description: Identify a Voice Profile to use (.pt), instructions (emotions may be separate from instructions), text 
    - save output as .wav file
- Fields:
    - instructions → how the voice should perform ("speak quickly", "whisper", "excited", "serious")
    - personality → behavioral traits ("sarcastic", "kind", "mischievous")
    - description → lore/context/background ("traveling bard from the northern kingdoms")

"""
python -m app.cli create-character \
  --name test \
  --audio tts_data/input/louise_voice_actor.wav \
  --instructions "Energetic child voice with playful delivery"
"""


## Transcribe An Audio File -> Text
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


### Character

#### Create a Reusable Character Profile / Voice Clone Using an Audio Clip
- to Overwrite an existing character use the `--overwrite` flag.
Input:
- reference audio clip
- transcript (Whisper)
- optional personality/instructions

Creates:
/app/tts_data/characters/<name>/
├── voice.pt
├── transcript.txt
└── metadata.json

"""
root@74b4bffe85ee:/app# python -m app.cli characters create \
    --name louise \
    --audio tts_data/input/louise_voice_actor.wav \
    --instructions "Energetic, sarcastic, curious child genius with a playful tone"
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
Mode: clone
Qwen3-TTS loaded successfully

============================================================
Creating Voice Clone Prompt
============================================================
Voice clone prompt created

============================================================
Character Created
============================================================

Name: louise
Voice Profile: /app/tts_data/characters/louise/voice.pt
Transcript: /app/tts_data/characters/louise/transcript.txt
Metadata: /app/tts_data/characters/louise/metadata.json
"""

### roleplay
- Loads character
- Uses Base model
- Builds:
    - voice clone prompt from reference audio
    - instruction prompt from personality/emotion/style
- Generates:
    - same voice
    - different delivery



                                 Character Creation
                       |
                       v
          reference audio + transcript
                       |
                       v
              create_voice_clone_prompt()
                       |
                       v
              Save reusable voice profile
                       |
                       |
                       v
              Roleplay Generation
                       |
                       |
          +------------+-------------+
          |                          |
          v                          v
   Voice Clone Base             CustomVoice
          |                          |
          |                          |
   cloned identity             style control
          |                          |
          +------------+-------------+
                       |
                       v
             instructions/emotion
                       |
                       v
                  output.wav