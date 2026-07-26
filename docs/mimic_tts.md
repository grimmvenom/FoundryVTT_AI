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



---

# API Authentication

The current API does not enforce authentication.

Open WebUI may still send an API key such as:

```text
Authorization: Bearer mimic
```

The current Mimic TTS API accepts the request regardless of the bearer token.

This is suitable for a trusted local Docker network.

If the API is exposed outside the trusted network, authentication should be added.

---

# Health Check

## `GET /`

Returns service information.

Example:

```bash
curl http://localhost:8188/
```

Example response:

```json
{
    "service": "mimic-tts",
    "status": "running",
    "model_loaded": true,
    "cuda": true,
    "gpu": "NVIDIA GPU"
}
```

---

## `GET /health`

Returns a basic health status.

```bash
curl http://localhost:8188/health
```

Example response:

```json
{
    "status": "ok",
    "model_loaded": true
}
```

---

# List Available Voices

## `GET /v1/voices`

Returns all stored character voices.

```bash
curl http://localhost:8188/v1/voices
```

Example response:

```json
{
    "object": "list",
    "data": [
        {
            "id": "jester",
            "name": "Jester",
            "object": "voice",
            "description": "Female Tiefling from the might nein - playful and mischievous",
            "language": "en-US",
            "gender": "female"
        },
        {
            "id": "louise",
            "name": "Louise",
            "object": "voice",
            "description": "Louise Belcher character voice - confident and sarcastic",
            "language": "en-US",
            "gender": "female"
        },
        {
            "id": "molly",
            "name": "Molly",
            "object": "voice",
            "description": "Molly character voice - warm and thoughtful",
            "language": "en-US",
            "gender": "male"
        }
    ]
}
```

The available voices are determined from stored characters.

Voice metadata may optionally be provided through:

```text
config/voices.json
```

---

# Voice Endpoint Aliases

The following endpoints return the same voice information:

```text
GET /v1/voices
GET /v1/audio/voices
GET /voices
```

The recommended endpoint is:

```text
GET /v1/voices
```

---

# List Models

## `GET /v1/models`

Returns available character voices as models.

```bash
curl http://localhost:8188/v1/models
```

Example response:

```json
{
    "object": "list",
    "data": [
        {
            "id": "jester",
            "object": "model",
            "owned_by": "mimic-tts"
        },
        {
            "id": "louise",
            "object": "model",
            "owned_by": "mimic-tts"
        },
        {
            "id": "molly",
            "object": "model",
            "owned_by": "mimic-tts"
        }
    ]
}
```

Alias:

```text
GET /models
```

---

# Text-to-Speech

## `POST /v1/audio/speech`

This is the primary OpenAI-compatible TTS endpoint.

It is compatible with clients that support the OpenAI-style speech API.

Example:

```bash
curl \
  -X POST \
  http://localhost:8188/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mimic" \
  -d '{
    "model": "mimic-tts",
    "voice": "jester",
    "input": "Hello there! How are you doing today?"
  }' \
  --output /tmp/test.wav
```

The generated audio is returned directly as a WAV file.

---

# TTS Request Fields

The API accepts the following JSON fields:

| Field | Type | Description |
|---|---|---|
| `input` | string | Primary text to synthesize |
| `text` | string | Alternative text field |
| `model` | string | Model name or voice alias |
| `voice` | string | Character / voice name |
| `character` | string | Stored character name |
| `speaker` | string | Alternative character selector |
| `instructions` | string | Temporary voice performance instructions |
| `emotion` | string | Requested emotion |
| `response_format` | string | Output format; currently only `wav` is supported |

---

# Character Selection

The API resolves the character in the following order:

```text
character
    ↓
voice
    ↓
speaker
    ↓
model
```

For example, these are all valid character selectors:

```json
{
    "input": "Hello!",
    "character": "jester"
}
```

```json
{
    "input": "Hello!",
    "voice": "jester"
}
```

```json
{
    "input": "Hello!",
    "speaker": "jester"
}
```

```json
{
    "input": "Hello!",
    "model": "jester"
}
```

For OpenAI-compatible clients, the recommended format is:

```json
{
    "model": "mimic-tts",
    "voice": "jester",
    "input": "Hello!"
}
```

---

# Roleplay TTS

## `POST /tts/roleplay`

The roleplay endpoint uses the stored character voice and supports additional performance controls.

Example:

```bash
curl \
  -X POST \
  http://localhost:8188/tts/roleplay \
  -H "Content-Type: application/json" \
  -d '{
    "character": "molly",
    "input": "How are you doing, lass? Been a while since our last fight.",
    "instructions": "Concerned and sympathetic",
    "emotion": "happy"
  }' \
  --output /tmp/molly.wav
```

The result is returned as:

```text
audio/wav
```

---

# TTS Endpoint Alias

The following endpoints provide speech synthesis:

```text
POST /tts/speech
POST /v1/audio/speech
```

The recommended endpoint for external clients is:

```text
POST /v1/audio/speech
```

---

# Output Format

The API currently supports:

```text
wav
```

The response MIME type is:

```text
audio/wav
```

Other formats such as:

```text
mp3
opus
flac
```

are not currently supported by the API endpoint.

Requests using an unsupported format return HTTP 400.

---

# Open WebUI Integration

Mimic TTS can be configured as an OpenAI-compatible TTS provider.

In Docker, Open WebUI connects to Mimic TTS using the internal Docker hostname:

```text
http://mimic-tts:8000/v1
```

Example Open WebUI environment configuration:

```yaml
environment:
  - 'OLLAMA_BASE_URL=http://ollama:11434'

  - 'AUDIO_TTS_ENGINE=openai'
  - 'AUDIO_TTS_OPENAI_API_BASE_URL=http://mimic-tts:8000/v1'
  - 'AUDIO_TTS_OPENAI_API_KEY=mimic'
  - 'AUDIO_TTS_MODEL=mimic-tts'
  - 'AUDIO_TTS_VOICE=jester'
```

Available voices can be changed by modifying:

```yaml
- 'AUDIO_TTS_VOICE=jester'
```

For example:

```yaml
- 'AUDIO_TTS_VOICE=louise'
```

or:

```yaml
- 'AUDIO_TTS_VOICE=molly'
```

After changing the Docker Compose configuration, restart Open WebUI:

```bash
docker compose up -d open-webui
```

---

# Open WebUI TTS Request

Open WebUI sends an OpenAI-compatible request similar to:

```json
{
    "model": "mimic-tts",
    "voice": "jester",
    "input": "Hello there!"
}
```

Mimic TTS resolves:

```text
voice = jester
```

to the stored character:

```text
tts_data/characters/jester/
```

and generates speech using the cached Qwen voice clone prompt.

---

# Foundry VTT Integration

Mimic TTS can be called from Foundry VTT macros.

The API is available to Foundry using the host machine's network address.

Example:

```text
http://192.168.7.XXX:8188
```

Replace the IP address with the address of the machine running Mimic TTS.

---

# [Foundry VTT TTS Macro](../code/Mimic_TTS.js)




# API Fallback Behavior

The API contains a fallback mechanism for some runtime failures.

If an unknown character is requested, Mimic TTS can generate fallback audio instead of immediately failing.

If a CUDA or GPU memory error occurs, the API can also return fallback audio.

This fallback behavior is primarily intended to prevent Open WebUI or other clients from crashing when TTS generation fails.

The fallback audio is a simple generated waveform and is not intended to replace real Qwen3-TTS output.

---

# Recommended Runtime Architecture

For normal operation:

```text
                    Ollama
                      |
                      |
                      v
                 Open WebUI
                      |
                      | TTS Request
                      v
                Mimic TTS API
                      |
                      v
             CharacterManager
                      |
                      +----------------+
                      |                |
                      v                v
               Character Data    Qwen3-TTS Engine
                      |                |
                      +-------+--------+
                              |
                              v
                          WAV Audio
```

Foundry VTT can independently call the same API:

```text
Foundry VTT
     |
     | POST /v1/audio/speech
     v
Mimic TTS API
     |
     v
Qwen3-TTS
     |
     v
WAV Audio
     |
     v
Foundry AudioHelper
```

---

# Current API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Service status |
| `GET` | `/health` | Health check |
| `GET` | `/voices` | List voices |
| `GET` | `/v1/voices` | List voices |
| `GET` | `/v1/audio/voices` | List voices |
| `GET` | `/models` | List character models |
| `GET` | `/v1/models` | List character models |
| `POST` | `/tts/speech` | Generate speech |
| `POST` | `/v1/audio/speech` | OpenAI-compatible speech generation |
| `POST` | `/tts/roleplay` | Generate roleplay speech |

The recommended API endpoints for integrations are:

```text
GET  /v1/voices
POST /v1/audio/speech
```

---

# Quick API Test

## Check Service

```bash
curl http://localhost:8188/health
```

## List Voices

```bash
curl http://localhost:8188/v1/voices
```

## Generate Speech

```bash
curl \
  -X POST \
  http://localhost:8188/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mimic" \
  -d '{
    "model": "mimic-tts",
    "voice": "jester",
    "input": "Hello there! How are you doing today?"
  }' \
  --output /tmp/test.wav
```

## Play Generated Audio

Linux:

```bash
ffplay /tmp/test.wav
```

Or use any standard WAV audio player.

---

# Development Notes

The API is intentionally thin.

The primary responsibilities are:

```text
API
 |
 +-- Parse request
 |
 +-- Resolve character
 |
 +-- Build RoleplayRequest
 |
 +-- Call CharacterManager
 |
 +-- Return WAV
```

The API should not contain Qwen-specific model logic.

Qwen model logic belongs in:

```text
app/core/qwen3_engine.py
```

Character workflow logic belongs in:

```text
app/core/characters/manager.py
```

Filesystem persistence belongs in:

```text
app/core/characters/storage.py
```

Character data models belong in:

```text
app/core/characters/models.py
```

This separation allows the CLI, Open WebUI, Foundry VTT, and future clients to use the same underlying character and TTS infrastructure.

---

# Potential Future Improvements

Potential future improvements include:

- API authentication
- Streaming audio responses
- MP3 / Opus output support
- Async generation jobs
- Request queueing
- GPU memory management
- Character-specific default emotions
- Character-specific default instructions
- Automatic character metadata enrichment
- API endpoint for character creation
- API endpoint for character deletion
- API endpoint for character metadata
- API endpoint for character management
- OpenAPI documentation
- WebSocket-based streaming
- Foundry VTT actor-to-character mapping
- Per-user voice preferences in Open WebUI
- Multiple GPU support
- Persistent model lifecycle management

The current architecture intentionally keeps character creation primarily CLI-driven while exposing runtime speech generation through the API.