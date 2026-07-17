from pathlib import Path

from app.core.speech_to_text import SpeechToText


def transcribe_command(args):

    audio = Path(args.audio)

    if not audio.exists():
        raise FileNotFoundError(audio)

    stt = SpeechToText(
        model=args.model,
        device=args.device,
    )

    print()

    print(f"Transcribing: {audio}")

    transcript = stt.transcribe(audio)

    print("\nTranscript:\n")
    print(transcript)

    if args.output:

        output = Path(args.output)

        output.write_text(
            transcript,
            encoding="utf-8",
        )

        print()
        print(f"Saved transcript -> {output}")