# Mimic TTS

Mimic TTS is a local GPU-accelerated text-to-speech service built around **Qwen3-TTS**.

- See [Mimic Voice](./mimic_voice.md) for commandline tool instructions & details
- Foundry VTT integration script for Mimic_TTS: [Mimic_TTS_Roleplay.js](../code/Mimic_TTS_Roleplay.js)
  - go to macros -> create macro -> script -> save


<hr>

# Docker Services

The combined Docker Compose stack contains three primary services.

```text
                    +----------------+
                    |   Open WebUI   |
                    |    :9000       |
                    +-------+--------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
        +---------------+       +---------------+
        |    Ollama     |       |   Mimic TTS   |
        |    :11434     |       |    :8188      |
        +---------------+       +---------------+
                                        |
                                        v
                                +---------------+
                                |   Qwen3-TTS   |
                                |     GPU       |
                                +---------------+
```


## Open WebUI
Host address: [http://localhost:9000](http://localhost:9000)

## Ollama
- Internal Docker address: [http://ollama:11434](http://ollama:11434)
- Host address: [http://localhost:11434](http://localhost:11434)

## Mimic TTS
- Internal Docker address: [http://mimic-tts:8000](http://mimic-tts:8000):
- Host Address: [http://localhost:8188](http://localhost:8188)



---

# API

Mimic TTS exposes a FastAPI application.
The primary API base URL is: [http://localhost:8188](http://localhost:8188)
When accessed from another Docker container on the same Docker network: [http://mimic-tts:8000](http://mimic-tts:8000)


# Mimic-TTS API

Mimic-TTS provides a Qwen3-TTS based voice-cloning API with OpenAI-compatible speech generation, reusable character profiles, character management, and an explicit roleplay endpoint.

## Base URL

Examples below assume:

```text
http://mimic-tts:8000
```

---

# Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Service status |
| `GET` | `/health` | Health check |
| `GET` | `/v1/models` | List available models |
| `GET` | `/models` | Alias for `/v1/models` |
| `GET` | `/v1/voices` | List character voices |
| `GET` | `/v1/audio/voices` | Alias for `/v1/voices` |
| `GET` | `/voices` | Alias for `/v1/voices` |
| `POST` | `/v1/characters` | Create a character |
| `POST` | `/characters` | Alias for character creation |
| `PUT` | `/v1/characters/{name}` | Update a character |
| `PUT` | `/characters/{name}` | Alias for character update |
| `POST` | `/v1/audio/speech` | OpenAI-compatible speech generation |
| `POST` | `/tts/speech` | Alias for speech generation |
| `POST` | `/v1/roleplay` | Generate character roleplay speech |
| `POST` | `/roleplay` | Alias for roleplay |
| `POST` | `/tts/roleplay` | Alias for roleplay |

---

# 1. Service Status

## `GET /`

Returns general service and model status.

### Example

```bash
curl http://mimic-tts:8000/
```

### Response

```json
{
  "service": "mimic-tts",
  "status": "running",
  "model": "mimic-tts",
  "model_loaded": true,
  "cuda": true,
  "gpu": "..."
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `service` | string | Service name |
| `status` | string | Service status |
| `model` | string | Active model identifier |
| `model_loaded` | boolean | Whether Qwen3-TTS is loaded |
| `cuda` | boolean | Whether CUDA is available |
| `gpu` | string/null | CUDA GPU name, if available |

---

# 2. Health Check

## `GET /health`

Simple health check.

### Example

```bash
curl http://mimic-tts:8000/health
```

### Response

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

# 3. List Models

## `GET /v1/models`

OpenAI-compatible model listing.

### Alias

```text
GET /models
```

### Example

```bash
curl http://mimic-tts:8000/v1/models
```

### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "mimic-tts",
      "object": "model",
      "owned_by": "mimic-tts"
    }
  ]
}
```

---

# 4. List Voices

## `GET /v1/voices`

Returns the stored character voices.

### Aliases

```text
GET /v1/audio/voices
GET /voices
```

### Example

```bash
curl http://mimic-tts:8000/v1/voices
```

### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "eira",
      "name": "Eira",
      "object": "voice",
      "description": "Eira character voice",
      "language": "en-US",
      "gender": "unknown"
    }
  ]
}
```

### Voice Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Character name used when generating speech |
| `name` | string | Display name |
| `object` | string | Always `voice` |
| `description` | string | Voice description |
| `language` | string | Voice language |
| `gender` | string | Configured gender, or `unknown` |

Voice display information can be customized through the optional `voices.json` configuration.

---

# 5. Create Character

## `POST /v1/characters`

Creates a reusable voice-cloned character.

### Alias

```text
POST /characters
```

### Content Type

```text
multipart/form-data
```

### Form Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `name` | string | Yes | Character name |
| `audio` | file | Yes | Reference voice audio |
| `instructions` | string | No | Default voice/performance instructions |
| `personality` | string | No | Character personality |
| `description` | string | No | Character description |
| `overwrite` | boolean | No | Replace an existing character with the same name |

### Supported Audio Formats

```text
.wav
.mp3
.m4a
.flac
.ogg
```

### Example

```bash
curl -X POST \
  http://mimic-tts:8000/v1/characters \
  -F "name=eira" \
  -F "audio=@eira_reference.wav" \
  -F "instructions=Speak naturally and warmly." \
  -F "personality=Calm, thoughtful, and curious." \
  -F "description=A fantasy character with a warm voice." \
  -F "overwrite=false"
```

### Processing

Character creation performs the following operations:

1. Validates the character name.
2. Validates the audio file.
3. Transcribes the reference audio with Whisper.
4. Loads Qwen3-TTS.
5. Creates a native Qwen voice-clone prompt.
6. Saves the voice-clone prompt.
7. Saves the transcript.
8. Saves character metadata.

### Successful Response

HTTP status:

```text
201 Created
```

Example:

```json
{
  "success": true,
  "character": {
    "name": "eira"
  },
  "transcript": "This is the reference recording...",
  "files": {
    "metadata": ".../metadata.json",
    "transcript": ".../transcript.txt",
    "voice_prompt": ".../voice_prompt.pt"
  }
}
```

### Errors

#### Empty name

```text
400 Bad Request
```

#### Unsupported audio format

```text
400 Bad Request
```

#### Existing character with overwrite disabled

```text
409 Conflict
```

#### Other creation failure

```text
500 Internal Server Error
```

---

# 6. Update Character

## `PUT /v1/characters/{name}`

Updates an existing character's metadata and optionally replaces its reference audio and voice clone.

### Alias

```text
PUT /characters/{name}
```

### Content Type

```text
multipart/form-data
```

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `name` | string | Yes | Existing character name |

### Form Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `audio` | file | No | New reference voice audio |
| `instructions` | string | No | Replace stored instructions |
| `personality` | string | No | Replace stored personality |
| `description` | string | No | Replace stored description |

### Important Behavior

Audio is optional.

If **no audio is supplied**:

- Existing voice clone is preserved.
- Existing transcript is preserved.
- Only supplied metadata fields are changed.

If **audio is supplied**:

1. The new audio is validated.
2. Whisper generates a new transcript.
3. Qwen generates a new voice-clone prompt.
4. The existing voice prompt is replaced.
5. The existing transcript is replaced.
6. `source_audio` is updated.
7. Supplied metadata is updated.

### Example: Metadata Only

```bash
curl -X PUT \
  http://mimic-tts:8000/v1/characters/eira \
  -F "instructions=Speak softly and naturally." \
  -F "personality=Calm and thoughtful."
```

### Example: Replace Voice Audio

```bash
curl -X PUT \
  http://mimic-tts:8000/v1/characters/eira \
  -F "audio=@new_eira_reference.wav" \
  -F "instructions=Speak softly and naturally."
```

### Successful Response

```json
{
  "success": true,
  "character": {
    "name": "eira"
  },
  "audio_updated": true,
  "transcript": "This is the new reference recording...",
  "files": {
    "metadata": ".../metadata.json",
    "transcript": ".../transcript.txt",
    "voice_prompt": ".../voice_prompt.pt"
  }
}
```

When no audio is supplied, `audio_updated` is `false`.

### Errors

#### Character does not exist

```text
404 Not Found
```

#### Invalid audio

```text
400 Bad Request
```

#### Update failure

```text
500 Internal Server Error
```

---

# 7. OpenAI-Compatible Speech

## `POST /v1/audio/speech`

Generates speech using a stored character voice.

This endpoint is intended to provide compatibility with clients such as Open WebUI.

### Alias

```text
POST /tts/speech
```

### Content Type

```text
application/json
```

### Request

```json
{
  "model": "mimic-tts",
  "voice": "eira",
  "input": "Hello, welcome to my world.",
  "response_format": "wav",
  "instructions": "Speak warmly.",
  "emotion": "happy"
}
```

### Fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `model` | string | No | `mimic-tts` | Model identifier |
| `voice` | string | Yes | — | Character name |
| `input` | string | Yes | — | Text to speak |
| `response_format` | string | No | `wav` | Audio format |
| `instructions` | string/null | No | `null` | Temporary performance instructions |
| `emotion` | string/null | No | `neutral` | Desired emotion |

Currently supported output formats:

```text
wav
wave
```

### Example

```bash
curl -X POST \
  http://mimic-tts:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mimic-tts",
    "voice": "eira",
    "input": "Hello, welcome to my world.",
    "response_format": "wav",
    "instructions": "Speak warmly.",
    "emotion": "happy"
  }' \
  --output speech.wav
```

### Response

```text
Content-Type: audio/wav
```

The response body contains the generated WAV audio.

### Behavior

The OpenAI-compatible endpoint internally uses the character roleplay generation workflow:

```text
voice
  ↓
CharacterManager.get()
  ↓
stored metadata + voice_prompt.pt
  ↓
CharacterManager.generate_roleplay()
  ↓
Qwen3Engine.generate_roleplay()
  ↓
WAV
```

### Errors

#### Unsupported model

```text
400 Bad Request
```

#### Missing text

```text
400 Bad Request
```

#### Voice not found

```text
404 Not Found
```

#### Generation failure

```text
500 Internal Server Error
```

---

# 8. Roleplay Speech

## `POST /v1/roleplay`

Generates speech for a stored character using the explicit Mimic-TTS roleplay API.

Unlike `/v1/audio/speech`, this endpoint uses `character` rather than OpenAI's `voice` terminology.

### Aliases

```text
POST /roleplay
POST /tts/roleplay
```

### Content Type

```text
application/json
```

### Request

```json
{
  "character": "eira",
  "text": "Hello there. What brings you to my village?",
  "instructions": "Speak warmly but cautiously.",
  "emotion": "curious",
  "response_format": "wav"
}
```

### Fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `character` | string | Yes | — | Existing character name |
| `text` | string | Yes | — | Dialogue to synthesize |
| `instructions` | string/null | No | `null` | Temporary performance instructions |
| `emotion` | string/null | No | `neutral` | Desired emotion |
| `response_format` | string | No | `wav` | Audio format |

Currently supported output formats:

```text
wav
wave
```

### Example

```bash
curl -X POST \
  http://mimic-tts:8000/v1/roleplay \
  -H "Content-Type: application/json" \
  -d '{
    "character": "eira",
    "text": "Hello there. What brings you to my village?",
    "instructions": "Speak warmly but cautiously.",
    "emotion": "curious",
    "response_format": "wav"
  }' \
  --output eira.wav
```

### Response

```text
Content-Type: audio/wav
```

The response body contains the generated WAV audio.

### Generation Flow

The roleplay endpoint uses the stored character assets:

```text
POST /v1/roleplay
        │
        ▼
CharacterManager.get()
        │
        ▼
Load character metadata
        │
        ▼
Load voice_prompt.pt
        │
        ▼
CharacterManager.generate_roleplay()
        │
        ├── stored instructions
        ├── request instructions
        └── emotion
        │
        ▼
Qwen3Engine.generate_roleplay()
        │
        ▼
Qwen3 voice clone generation
        │
        ▼
WAV response
```

### Errors

#### Missing character

```text
400 Bad Request
```

#### Character does not exist

```text
404 Not Found
```

#### Missing text

```text
400 Bad Request
```

#### Generation failure

```text
500 Internal Server Error
```

---

# 9. Character Data Model

A character consists of three primary persistent assets.

```text
characters/
└── <character>/
    ├── metadata.json
    ├── transcript.txt
    └── voice_prompt.pt
```

## `metadata.json`

Contains character metadata such as:

- Character name
- Source audio path
- Instructions
- Personality
- Description
- Schema version

## `transcript.txt`

Contains the Whisper-generated transcript of the reference audio.

This transcript is used when creating the Qwen voice clone prompt.

## `voice_prompt.pt`

Contains the native Qwen voice clone prompt generated from the reference audio and transcript.

This is the persistent voice asset used for subsequent speech generation.

---

# 10. Voice Replacement

A character's voice can be replaced without creating a new character.

Use:

```text
PUT /v1/characters/{name}
```

with a new `audio` file.

For example:

```bash
curl -X PUT \
  http://mimic-tts:8000/v1/characters/eira \
  -F "audio=@eira_v2.wav"
```

The new audio is:

```text
new reference audio
        ↓
Whisper transcript
        ↓
Qwen voice clone prompt
        ↓
replace voice_prompt.pt
        ↓
replace transcript.txt
        ↓
update metadata.json
```

The character name remains unchanged.

---

# 11. Metadata-Only Updates

Metadata can be changed without touching the voice clone.

Example:

```bash
curl -X PUT \
  http://mimic-tts:8000/v1/characters/eira \
  -F "personality=Wise, patient, and protective." \
  -F "description=A wandering mage."
```

The existing:

```text
voice_prompt.pt
transcript.txt
```

remain unchanged.

---

# 12. Temporary Instructions vs Stored Instructions

Characters may have stored instructions:

```text
metadata.instructions
```

A generation request may also provide temporary instructions:

```json
{
  "instructions": "Whisper this line."
}
```

For roleplay generation, the engine combines the character's stored instructions with request-specific instructions and the requested emotion.

This allows the same character to have a persistent vocal style while still supporting per-line performance direction.

---

# 13. Emotion

Emotion is supplied as a generation-time parameter.

Example:

```json
{
  "character": "eira",
  "text": "You actually came back.",
  "emotion": "surprised"
}
```

The emotion is converted into a performance instruction before being passed to Qwen3-TTS.

Examples include:

```text
neutral
happy
sad
angry
surprised
fearful
excited
```

The API does not currently restrict the value to a fixed enumeration, so arbitrary descriptive emotion values may be supplied.

---

# 14. Open WebUI Integration

For OpenAI-compatible clients, configure the TTS service URL as:

```text
http://mimic-tts:8000/v1
```

The client should use:

```text
POST /v1/audio/speech
```

with:

```json
{
  "model": "mimic-tts",
  "voice": "eira",
  "input": "Text to speak."
}
```

The returned content is WAV audio.

The `/v1/audio/speech` endpoint and `/v1/roleplay` endpoint ultimately use the same character voice-cloning infrastructure.

---

# 15. ComfyUI Integration

A ComfyUI client can use the explicit roleplay endpoint:

```text
POST /v1/roleplay
```

Example request:

```json
{
  "character": "eira",
  "text": "Welcome, traveler.",
  "instructions": "",
  "emotion": "neutral",
  "response_format": "wav"
}
```

For character management, ComfyUI can use:

```text
GET  /v1/voices
POST /v1/characters
PUT  /v1/characters/{name}
```

This allows a workflow to:

1. List available characters.
2. Create a character from reference audio.
3. Update the reference audio.
4. Update character metadata.
5. Generate roleplay speech.

---

# 16. Recommended API Usage

### Create a new character

```text
POST /v1/characters
```

### Change a character's reference voice

```text
PUT /v1/characters/{name}
```

with `audio`.

### Change only character metadata

```text
PUT /v1/characters/{name}
```

without `audio`.

### List available voices

```text
GET /v1/voices
```

### Generate normal OpenAI-compatible speech

```text
POST /v1/audio/speech
```

### Generate explicit character roleplay speech

```text
POST /v1/roleplay
```

---

# 17. Status Codes

| Status | Meaning |
|---:|---|
| `200` | Successful request |
| `201` | Character successfully created |
| `400` | Invalid request, missing field, unsupported audio, etc. |
| `404` | Character/voice not found |
| `409` | Character already exists and overwrite is disabled |
| `500` | Internal TTS, transcription, or character-processing failure |

---

# 18. Design Notes

Mimic-TTS separates the application API from Qwen3-TTS internals.

The API communicates with:

```text
CharacterManager
```

rather than directly manipulating Qwen3 objects.

The character manager coordinates:

```text
Audio validation
      ↓
Whisper transcription
      ↓
Qwen voice clone prompt creation
      ↓
Character storage
      ↓
Roleplay generation
```

The Qwen engine is responsible for the actual Qwen3-TTS operations.

This separation allows the API, ComfyUI integration, and Open WebUI integration to share the same character/voice infrastructure.
