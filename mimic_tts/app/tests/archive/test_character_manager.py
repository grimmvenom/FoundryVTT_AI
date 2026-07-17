from pathlib import Path
import pytest

from mimic_tts.app.core.characters.manager import CharacterManager


@pytest.fixture
def character_manager(tmp_path):
    return CharacterManager(
        output_directory=tmp_path
    )


@pytest.mark.unit
def test_missing_audio_file_raises_error(
    character_manager
):

    missing = Path(
        "/app/input/does_not_exist.wav"
    )

    with pytest.raises(FileNotFoundError) as error:

        character_manager.validate_audio(
            missing
        )

    assert (
        "Audio file not found"
        in str(error.value)
    )



@pytest.mark.unit
def test_audio_path_must_be_file(
    character_manager,
    tmp_path
):

    directory = tmp_path / "audio"

    directory.mkdir()


    with pytest.raises(ValueError) as error:

        character_manager.validate_audio(
            directory
        )


    assert (
        "Path is not a file"
        in str(error.value)
    )



@pytest.mark.unit
def test_invalid_audio_extension(
    character_manager,
    tmp_path
):

    file = tmp_path / "test.txt"

    file.write_text(
        "not audio"
    )


    with pytest.raises(ValueError) as error:

        character_manager.validate_audio(
            file
        )


    assert (
        "Unsupported audio format"
        in str(error.value)
    )



@pytest.mark.unit
def test_empty_transcript_fails(
    character_manager,
    tmp_path
):

    audio = tmp_path / "voice.wav"

    audio.write_bytes(
        b"fake"
    )


    class FakeEngine:
        pass


    with pytest.raises(ValueError) as error:

        character_manager.create_character(
            name="test",
            audio_path=audio,
            transcript="",
            engine=FakeEngine()
        )


    assert (
        "Transcript cannot be empty"
        in str(error.value)
    )