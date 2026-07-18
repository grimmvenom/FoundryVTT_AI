"""
High-level transcription workflow.

Coordinates the SpeechToText service and returns a
structured result.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TranscriptionResult:
    audio_path: Path
    transcript: str


class Transcriber:
    """
    High-level transcription service.
    """

    def __init__(
        self,
        speech_to_text=None,
    ):
        from app.core.speech_to_text import SpeechToText

        self.stt = (
            speech_to_text
            or SpeechToText()
        )

    def transcribe(
        self,
        audio_path,
    ) -> TranscriptionResult:

        audio_path = Path(audio_path)

        transcript = self.stt.transcribe(
            audio_path
        )

        return TranscriptionResult(
            audio_path=audio_path,
            transcript=transcript,
        )