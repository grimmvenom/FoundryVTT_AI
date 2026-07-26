from pathlib import Path

from app.core.speech_to_text import SpeechToText
from app.core.transcribe import Transcriber


def transcribe_command(args):

    transcriber = Transcriber(
        SpeechToText(
            model=args.model,
            device=args.device,
        )
    )

    result = transcriber.transcribe(
        Path(args.audio)
    )

    print()
    print("Transcript:\n")
    print(result.transcript)

    if args.output:

        output = Path(args.output)

        output.write_text(
            result.transcript,
            encoding="utf-8",
        )

        print()
        print(f"Saved transcript -> {output}")