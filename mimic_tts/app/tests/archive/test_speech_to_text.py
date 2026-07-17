from pathlib import Path

import pytest

from app.core.speech_to_text import SpeechToText


# ---------------------------------------------------------
# Test configuration
# ---------------------------------------------------------

TEST_AUDIO = Path("/app/input/louise_voice_actor.wav")


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture(scope="module")
def speech_service():
    """
    Creates a SpeechToText instance.

    Model loading is intentionally deferred until transcription
    happens, so this fixture itself should remain lightweight.
    """
    return SpeechToText()


# ---------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------

@pytest.mark.unit
def test_missing_audio_file_raises_error(speech_service):
    """
    Expected failure:
    A file that does not exist should fail cleanly.
    """

    missing_file = Path(
        "/app/input/this_file_should_not_exist.wav"
    )

    with pytest.raises(FileNotFoundError) as error:

        speech_service.transcribe(
            missing_file
        )

    assert "Audio file not found" in str(error.value)



@pytest.mark.unit
def test_invalid_audio_extension(speech_service):
    """
    Expected failure:
    Only supported audio formats should be accepted.
    """

    fake_file = Path(
        "/app/input/test.txt"
    )

    fake_file.touch()

    try:

        with pytest.raises(ValueError) as error:

            speech_service.transcribe(
                fake_file
            )

        assert (
            "Unsupported audio format"
            in str(error.value)
        )

    finally:
        fake_file.unlink()



@pytest.mark.unit
def test_audio_path_must_be_file(speech_service):
    """
    Expected failure:
    Directory paths should not be accepted.
    """

    directory = Path("/app/input")

    with pytest.raises(ValueError) as error:

        speech_service.transcribe(
            directory
        )

    assert (
        "Path is not a file"
        in str(error.value)
    )


# ---------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------

@pytest.mark.integration
def test_transcribe_real_audio(
    speech_service
):
    """
    Integration test:

    Requires:
    - Whisper model available
    - GPU/CPU inference available
    - test audio file exists
    """

    if not TEST_AUDIO.exists():

        pytest.skip(
            f"Missing integration audio file: {TEST_AUDIO}"
        )


    transcript = speech_service.transcribe(
        TEST_AUDIO
    )


    assert transcript is not None

    assert len(transcript.strip()) > 0


    # Louise sample should contain recognizable words
    # This is intentionally loose because Whisper output
    # may vary slightly between versions.

    expected_terms = [
        "apple",
        "pie",
        "luck",
        "casserole",
    ]

    assert any(
        word in transcript.lower()
        for word in expected_terms
    )