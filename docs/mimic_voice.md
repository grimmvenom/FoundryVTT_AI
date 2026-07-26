# Mimic Voice

Mimic Voice supports commandline & API and is a local GPU-accelerated text-to-speech service built around **Qwen3-TTS**, whisper, and other tools to allow you to clone voices from audio files. This allows you to build reusable voice profiles (characters) that can be used to roleplay characters via a text to speech (TTS) service.


It provides:
- Reusable character voice cloning
- Whisper-based audio transcription
- Cached Qwen voice clone prompts
- Character metadata and persistence
- CLI workflows for character management
- OpenAI-compatible TTS API
- Open WebUI integration
- Foundry VTT integration
- Roleplay-oriented voice generation
- Dynamic character / voice selection

The service is designed so that character creation and audio preparation can be handled manually through the CLI, while runtime speech generation is exposed through the API.


# Project Structure

```text
config/
├── default.ini
├── mac.ini
└── voices.json

app/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI application
│
├── core/
│   ├── characters/
│   │   ├── manager.py       # Character workflow coordination
│   │   ├── models.py        # Character data models
│   │   └── storage.py       # Character filesystem persistence
│   │
│   ├── qwen3_engine.py      # Qwen3-TTS engine
│   ├── speech_to_text.py    # Whisper integration
│   ├── transcribe.py
│   └── ...
│
└── cli.py                    # Command-line interface
```

---

# Character Storage

Characters are stored under:

```text
tts_data/characters/
```

Each character has its own directory:

```text
tts_data/characters/<character_name>/
├── metadata.json
├── transcript.txt
├── voice.pt
└── voice_prompt.pt
```

## Files

### `metadata.json`

Contains persistent character information:

- Character name
- CustomVoice speaker, if applicable
- Source audio path
- Default instructions
- Personality
- Description
- Voice filename
- Metadata schema version

Example:

```json
{
    "schema_version": 1,
    "name": "jester",
    "speaker": "jester",
    "source_audio": "/app/tts_data/input/jester.wav",
    "instructions": "excited, heavy accent",
    "personality": "quirky, hyper, funny",
    "description": "A young female traveling entertainer who entertains villages with jokes",
    "voice_filename": "voice.pt"
}
```

### `transcript.txt`

Contains the Whisper-generated transcript of the reference audio.

### `voice.pt`

Stores legacy / source voice profile information.

### `voice_prompt.pt`

Stores the reusable Qwen VoiceClonePrompt data.

This avoids rebuilding the voice clone prompt every time the character speaks.

---


# Command Line Interface

The CLI is primarily intended for manual character management and audio preparation.

Runtime TTS should generally use the API.

Available character commands include:

```text
characters create
characters list
```

---

# List Characters

List all stored characters:

```bash
python -m app.cli characters list
```

Example:

```text
============================================================
Characters
============================================================

jester
louise
molly
```

The list is sorted alphabetically.

---

# Create a Character

Create a reusable character voice clone:

```bash
python -m app.cli characters create \
  --name louise \
  --audio tts_data/input/louise_voice_actor.wav \
  --instructions "Energetic, sarcastic, curious child genius with a playful tone"
```

The process:

1. Validate reference audio
2. Load Whisper
3. Transcribe reference audio
4. Validate transcript
5. Create character directory
6. Load Qwen3-TTS
7. Create voice clone prompt
8. Save `voice_prompt.pt`
9. Save `transcript.txt`
10. Save `metadata.json`

Example output:

```text
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
```

---

# Overwrite an Existing Character

Use:

```bash
--overwrite
```

Example:

```bash
python -m app.cli characters create \
  --name louise \
  --audio tts_data/input/louise_voice_actor.wav \
  --instructions "Energetic, sarcastic, curious child genius with a playful tone" \
  --overwrite
```

This removes the existing character directory and recreates it.

---

# Character Creation Data

Character creation currently accepts:

### Name

The stored character name.

Example:

```text
louise
```

### Reference Audio

The audio used for voice cloning and transcription.

Supported formats:

```text
.wav
.mp3
.m4a
.flac
.ogg
```

### Instructions

Describes how the character should speak.

Examples:

```text
Speak quickly
```

```text
Energetic, playful, and sarcastic
```

```text
Whisper softly and cautiously
```

### Personality

Describes behavioral traits.

Examples:

```text
Sarcastic, kind, mischievous
```

### Description

Describes lore, context, or background.

Example:

```text
A traveling bard from the northern kingdoms.
```

Character metadata supports:

```text
instructions
personality
description
```

These fields are persisted in `metadata.json`.

---

# Transcribe an Audio File

Whisper can be used directly from the CLI.

Example:

```bash
python -m app.cli transcribe \
  --audio tts_data/input/louise_voice_actor.wav \
  --output tts_data/output/transcribe_test.txt
```

Whisper will:

1. Load the configured model
2. Transcribe the input audio
3. Print the transcript
4. Save the transcript to the requested output file

Example:

```text
============================================================
Loading Whisper
============================================================
Model:        large-v3
Device:       cuda
Compute type: float16
Whisper loaded successfully

Transcribing:
tts_data/input/louise_voice_actor.wav

Transcript:

Yes, you can keep chewing on my sweater.
He likes his apple pie warm and his a la mode cold.
Good luck.

...

Saved transcript ->
tts_data/output/transcribe_test.txt
```

---

# Character Roleplay

Character roleplay uses:

- A stored character
- Cached Qwen voice clone prompt
- Character metadata
- Optional instructions
- Optional emotion
- Input dialogue

The CLI roleplay command can be used for local testing.

Example:

```bash
python -m app.cli roleplay \
  --character molly \
  --script "How are you doing, lass? Been a while since our last fight." \
  --instructions "Concerned and sympathetic" \
  --emotion "happy" \
  --output tts_data/output/molly_test.wav
```

The generated WAV file is written to:

```text
tts_data/output/molly_test.wav
```

---

# Character Generation Architecture

Character creation and runtime generation are separate workflows.

## Character Creation

```text
Reference Audio
      |
      v
     Whisper
      |
      v
   Transcript
      |
      +-------------------+
      |                   |
      v                   v
Character Metadata   Voice Clone Prompt
      |                   |
      v                   v
metadata.json      voice_prompt.pt
      |                   |
      +---------+---------+
                |
                v
        Stored Character
```

## Runtime Roleplay

```text
User Text
    |
    v
Character Selection
    |
    v
Load Character
    |
    +--------------------+
    |                    |
    v                    v
Metadata          voice_prompt.pt
    |                    |
    +---------+----------+
              |
              v
     Instructions
              +
          Emotion
              |
              v
        Qwen3-TTS
              |
              v
          WAV Audio
```

---

# Voice Clone vs CustomVoice

Mimic TTS supports two conceptual Qwen3-TTS workflows.

## Voice Clone

Used for stored characters created from reference audio.

```text
Reference Audio
      |
      v
Voice Clone Prompt
      |
      v
Cached voice_prompt.pt
      |
      v
Character
      |
      v
Roleplay / TTS
```

The goal is to preserve the identity and characteristics of the reference voice while allowing different dialogue, emotions, and delivery instructions.

## CustomVoice

CustomVoice is used when a supported Qwen speaker is selected directly rather than using a stored cloned character.

The workflow is:

```text
Text
  |
  v
Qwen CustomVoice Speaker
  |
  +--> Instructions
  |
  v
Generated Audio
```


# Roleplay Generation Flow

Character roleplay generation follows this process:

```text
Client
  |
  v
POST /v1/audio/speech
  |
  v
Resolve Character
  |
  v
Load Character
  |
  v
Load Metadata + Voice Clone Prompt
  |
  v
Build RoleplayRequest
  |
  v
CharacterManager
  |
  v
Qwen3-TTS
  |
  v
Generate Audio
  |
  v
Return WAV
```

The character's cached `voice_prompt.pt` is reused during generation.

---

# Example: Character Voice With Instructions

```bash
curl \
  -X POST \
  http://localhost:8188/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mimic" \
  -d '{
    "model": "mimic-tts",
    "voice": "louise",
    "input": "You are seriously going to make me clean all of this up?",
    "instructions": "Sarcastic, confident, energetic child genius"
  }' \
  --output /tmp/louise.wav
```

---

# Example: Character Voice With Emotion

```bash
curl \
  -X POST \
  http://localhost:8188/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimic-tts",
    "voice": "molly",
    "input": "I was worried about you. You should have told me.",
    "instructions": "Warm and sympathetic",
    "emotion": "concerned"
  }' \
  --output /tmp/molly.wav
```
