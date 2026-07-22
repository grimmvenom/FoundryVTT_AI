from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.speech_to_text import SpeechToText


def test_speech_to_text_initial_state():

    stt = SpeechToText(
        model="test-model",
        device="cpu",
        compute_type="int8",
    )

    assert stt.model_name == "test-model"
    assert stt.device == "cpu"
    assert stt.compute_type == "int8"

    # Lazy loading
    assert stt.model is None

    assert stt.last_info is None



def test_validate_audio_missing(tmp_path):

    stt = SpeechToText()

    audio = tmp_path / "missing.wav"

    with pytest.raises(
        FileNotFoundError
    ):
        stt.validate_audio(
            audio
        )



def test_validate_audio_not_file(tmp_path):

    stt = SpeechToText()

    directory = tmp_path / "audio.wav"

    directory.mkdir()

    with pytest.raises(
        ValueError
    ):
        stt.validate_audio(
            directory
        )



def test_validate_audio_bad_format(tmp_path):

    stt = SpeechToText()

    audio = tmp_path / "audio.txt"

    audio.write_bytes(
        b"fake audio"
    )

    with pytest.raises(
        ValueError
    ):
        stt.validate_audio(
            audio
        )



@pytest.mark.parametrize(
    "extension",
    [
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    ],
)
def test_validate_audio_supported_formats(
    tmp_path,
    extension,
):

    stt = SpeechToText()

    audio = tmp_path / (
        f"audio{extension}"
    )

    audio.write_bytes(
        b"fake audio"
    )

    # should not raise
    stt.validate_audio(
        audio
    )



def test_transcribe_returns_combined_segments(
    tmp_path,
):

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake audio"
    )


    stt = SpeechToText()


    fake_model = MagicMock()


    fake_segments = [
        MagicMock(text="Hello"),
        MagicMock(text="world"),
    ]


    fake_info = {
        "language": "en"
    }


    fake_model.transcribe.return_value = (
        fake_segments,
        fake_info,
    )


    stt.model = fake_model


    result = stt.transcribe(
        audio
    )


    assert result == (
        "Hello world"
    )


    assert stt.last_info == (
        fake_info
    )


    fake_model.transcribe.assert_called_once_with(
        str(audio)
    )



def test_transcribe_strips_segment_whitespace(
    tmp_path,
):

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake audio"
    )


    stt = SpeechToText()


    fake_model = MagicMock()


    fake_model.transcribe.return_value = (
        [
            MagicMock(text="  hello  "),
            MagicMock(text=" world "),
        ],
        None,
    )


    stt.model = fake_model


    result = stt.transcribe(
        audio
    )


    assert result == (
        "hello world"
    )



def test_load_skips_when_model_already_loaded():

    stt = SpeechToText()

    fake_model = object()

    stt.model = fake_model


    stt.load()


    assert stt.model is fake_model



def test_load_creates_model_when_missing():

    stt = SpeechToText(
        model="tiny",
        device="cpu",
        compute_type="int8",
    )


    fake_whisper = MagicMock()


    with patch(
        "faster_whisper.WhisperModel",
        return_value=fake_whisper,
    ) as mock_model:


        stt.load()


    mock_model.assert_called_once_with(
        "tiny",
        device="cpu",
        compute_type="int8",
    )


    assert stt.model is fake_whisper
