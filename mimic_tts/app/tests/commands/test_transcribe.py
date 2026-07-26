from pathlib import Path

from app.core.transcribe import (
    Transcriber,
    TranscriptionResult,
)


class FakeSpeechToText:
    """
    Fake STT backend for unit tests.
    """

    def __init__(
        self,
        transcript="hello there",
    ):
        self.transcript = transcript
        self.called_with = None

    def transcribe(
        self,
        audio_path,
    ):
        self.called_with = audio_path
        return self.transcript



def test_transcribe_success(tmp_path):
    """
    Successful transcription returns structured result.
    """

    audio = tmp_path / "voice.wav"

    # SpeechToText validates files exist
    audio.write_bytes(
        b"fake audio"
    )


    stt = FakeSpeechToText()

    transcriber = Transcriber(
        speech_to_text=stt,
    )


    result = transcriber.transcribe(
        audio
    )


    assert isinstance(
        result,
        TranscriptionResult,
    )

    assert result.audio_path == audio

    assert result.transcript == (
        "hello there"
    )

    assert stt.called_with == audio



def test_transcribe_accepts_string_path(
    tmp_path,
):
    """
    Transcriber normalizes string paths.
    """

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake audio"
    )


    stt = FakeSpeechToText()

    transcriber = Transcriber(
        speech_to_text=stt,
    )


    result = transcriber.transcribe(
        str(audio)
    )


    assert isinstance(
        result.audio_path,
        Path,
    )

    assert result.audio_path == audio



def test_empty_transcript(
    tmp_path,
):
    """
    Empty Whisper result is preserved.
    """

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake audio"
    )


    stt = FakeSpeechToText(
        transcript=""
    )


    transcriber = Transcriber(
        speech_to_text=stt,
    )


    result = transcriber.transcribe(
        audio
    )


    assert result.transcript == ""



def test_transcriber_passes_audio_to_backend(
    tmp_path,
):
    """
    Backend receives the normalized Path.
    """

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake audio"
    )


    stt = FakeSpeechToText()

    transcriber = Transcriber(
        speech_to_text=stt,
    )


    transcriber.transcribe(
        audio
    )


    assert stt.called_with == audio

