from fastapi import FastAPI
import torch

from .core.qwen3_engine import engine


app = FastAPI(
    title="Mimic TTS",
    description="Qwen3-TTS FastAPI backend"
)


@app.on_event("startup")
async def startup():

    engine.load()


@app.get("/")
def root():

    return {
        "service": "mimic-tts",
        "status": "running",
        "model_loaded": engine.loaded(),
        "cuda": torch.cuda.is_available(),
        "gpu": (
            torch.cuda.get_device_name(0)
            if torch.cuda.is_available()
            else None
        )
    }