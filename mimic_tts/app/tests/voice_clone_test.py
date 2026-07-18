import torch
from faster_whisper import WhisperModel
from qwen_tts import Qwen3TTSModel
import os

AUDIO_FILE = os.environ.get(
    "VOICE_AUDIO",
    "/app/input/louise_voice_actor.wav"
)

OUTPUT_FILE = os.environ.get(
    "OUTPUT_FILE",
    "/app/output/louise_clone_test.wav"
)

MODEL_PATH = "/app/models/qwen-tts/Qwen3-TTS-12Hz-1.7B-Base"


def transcribe(audio):

    print("Loading Whisper...")

    whisper = WhisperModel(
        "large-v3",
        device="cuda",
        compute_type="float16"
    )

    segments, info = whisper.transcribe(audio)

    text = ""

    for segment in segments:
        text += segment.text + " "

    print()
    print("Transcript:")
    print(text)

    return text.strip()


def load_qwen():

    print("Loading Qwen3-TTS...")

    model = Qwen3TTSModel.from_pretrained(
        MODEL_PATH,
        device_map="cuda",
        dtype=torch.bfloat16,
    )

    return model


def clone_voice(model, audio, transcript):

    print("Generating voice clone...")

    wavs, sr = model.generate_voice_clone(
        text="Hello, this is a voice cloning test. Are you pleased with the new CHAOS You've Created!?",
        language="English",
        ref_audio=audio,
        ref_text=transcript,
    )

    import soundfile as sf

    sf.write(
        OUTPUT_FILE,
        wavs[0],
        sr
    )

    print()
    print("Saved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":

    transcript = transcribe(AUDIO_FILE)

    model = load_qwen()

    clone_voice(
        model,
        AUDIO_FILE,
        transcript
    )