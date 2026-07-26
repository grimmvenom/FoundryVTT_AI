# Running With Docker

## Build Mimic TTS

From the root project directory:

```bash
docker compose build mimic-tts
```

To force a clean rebuild:

```bash
docker compose build --no-cache mimic-tts
```

## Start the Full AI Stack

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

The stack contains:

- Ollama
- Mimic TTS
- Open WebUI

## Stop the Stack

```bash
docker compose down
```

## View Mimic TTS Logs

```bash
docker compose logs -f mimic-tts
```

## Interactive Shell

```bash
docker compose run --rm --entrypoint bash mimic-tts
```

Example:

```text
root@container:/app#
```

---