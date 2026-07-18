from pathlib import Path


class SpeechToText:
    """
    Speech-to-text abstraction.

    Currently uses faster-whisper.
    Can later be swapped for another backend.
    """

    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    }


    def __init__(
        self,
        model="large-v3",
        device="cuda",
        compute_type="float16",
    ):

        from faster_whisper import WhisperModel
        self.model_name = model
        self.device = device
        self.compute_type = compute_type

        self.model = None


    def load(self):
        """
        Lazy load Whisper model.

        Prevents loading Whisper when:
        - running CLI help
        - testing validation
        - importing the module
        """

        if self.model:
            return


        print("=" * 60)
        print("Loading Whisper")
        print("=" * 60)
        print(f"Model:        {self.model_name}")
        print(f"Device:       {self.device}")
        print(f"Compute type: {self.compute_type}")


        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
        )

        print("Whisper loaded successfully")



    def validate_audio(
        self,
        audio_path: Path
    ):
        """
        Validate audio input before transcription.
        """

        audio_path = Path(audio_path)


        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )


        if not audio_path.is_file():
            raise ValueError(
                f"Path is not a file: {audio_path}"
            )


        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}"
            )



    def transcribe(
        self,
        audio_path: Path
    ) -> str:

        audio_path = Path(audio_path)


        self.validate_audio(
            audio_path
        )


        self.load()


        print(
            f"Transcribing: {audio_path}"
        )


        segments, info = self.model.transcribe(
            str(audio_path)
        )


        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        )


        return transcript