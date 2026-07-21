"""
Speech-to-text service.

Responsibilities:
- Validate audio input
- Lazy-load Whisper model
- Transcribe audio files
- Expose transcription metadata

Backend:
- faster-whisper

Configuration:
Loaded from config/default.ini unless explicitly overridden.
"""


from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.config import settings


if TYPE_CHECKING:
    from faster_whisper import WhisperModel



class SpeechToText:
    """
    Speech-to-text abstraction.

    Currently uses faster-whisper.

    The backend can be swapped later without
    changing the rest of the application.
    """


    SUPPORTED_FORMATS = frozenset({
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    })


    def __init__(
        self,
        model: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
    ) -> None:
        """
        Initialize speech-to-text configuration.

        Arguments are optional.

        If omitted, values are loaded from:

        [transcription]
        model = large-v3
        device = cuda
        compute_type = float16

        Explicit arguments override configuration.

        This allows:
        - CLI overrides
        - unit testing
        - CPU fallback testing
        - alternate Whisper models
        """


        self.model_name = (
            model
            or settings.transcription_model
        )


        self.device = (
            device
            or settings.transcription_device
        )


        self.compute_type = (
            compute_type
            or settings.transcription_compute_type
        )


        # Whisper model is loaded lazily.
        #
        # Loading Whisper is expensive and should not happen
        # when:
        # - importing modules
        # - displaying CLI help
        # - running validation tests
        self.model: WhisperModel | None = None


        # Stores metadata returned by Whisper:
        # - detected language
        # - probabilities
        # - duration
        #
        # Useful for debugging or future API responses.
        self.last_info: Any = None



    def load(self) -> None:
        """
        Load Whisper model into memory.

        This only happens once.

        Subsequent calls reuse the already loaded model.
        """


        if self.model is not None:
            return


        from faster_whisper import WhisperModel


        print("=" * 60)
        print("Loading Whisper")
        print("=" * 60)

        print(
            f"Model:        {self.model_name}"
        )

        print(
            f"Device:       {self.device}"
        )

        print(
            f"Compute type: {self.compute_type}"
        )


        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
        )


        print(
            "Whisper loaded successfully"
        )



    def validate_audio(
        self,
        audio_path: Path,
    ) -> None:
        """
        Validate an audio file before transcription.

        Checks:
        - file exists
        - path points to a file
        - extension is supported
        """


        audio_path = Path(
            audio_path
        )


        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )


        if not audio_path.is_file():

            raise ValueError(
                f"Path is not a file: {audio_path}"
            )


        if (
            audio_path.suffix.lower()
            not in self.SUPPORTED_FORMATS
        ):

            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}"
            )



    def transcribe(
        self,
        audio_path: Path,
        **kwargs: Any,
    ) -> str:
        """
        Convert speech audio into text.

        Parameters:
            audio_path:
                Audio file to transcribe.

            kwargs:
                Additional options passed directly to:

                faster_whisper.WhisperModel.transcribe()

        Returns:
            Transcript string.
        """


        audio_path = Path(
            audio_path
        )


        self.validate_audio(
            audio_path
        )


        self.load()


        print(
            f"Transcribing: {audio_path}"
        )


        assert self.model is not None


        segments, info = self.model.transcribe(
            str(audio_path),
            **kwargs,
        )


        self.last_info = info


        transcript_parts = []

        for segment in segments:

            text = segment.text.strip()

            if text:
                transcript_parts.append(
                    text
                )


        return " ".join(
            transcript_parts
        )