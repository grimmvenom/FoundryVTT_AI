from pathlib import Path

import pytest

from app.core.transcribe import (
    Transcriber,
    TranscriptionResult,
)


class FakeSpeechToText:

    def __init__(self):
        self.called_with = None

    def transcribe(self, audio):

        self.called_with = audio

        return "hello there"


class EmptySpeech:

    def transcribe(self, audio):

        return ""


def test_transcribe_success(tmp_path):

    stt = FakeSpeechToText()

    transcriber = Transcriber(
        speech_to_text=stt,
    )

    audio = tmp_path / "voice.wav"

    result = transcriber.transcribe(
        audio
    )

    assert isinstance(
        result,
        TranscriptionResult,
    )

    assert result.audio_path == audio
    assert result.transcript == "hello there"

    assert stt.called_with == audio


def test_empty_transcript(tmp_path):

    transcriber = Transcriber(
        speech_to_text=EmptySpeech(),
    )

    audio = tmp_path / "voice.wav"

    result = transcriber.transcribe(
        audio
    )

    assert result.transcript == ""
