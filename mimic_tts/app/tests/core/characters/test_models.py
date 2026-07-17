from pathlib import Path
import pytest

from app.core.characters.models import (
    Character,
    CharacterMetadata,
    CreateCharacterResult,
)
# from app.core.characters.manager import CharacterManager
# from app.core.characters.storage import CharacterStorage


def test_character_dataclass():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
        voice_path=Path("/tmp/louise/voice.qvp"),
        transcript_path=Path("/tmp/louise/transcript.txt"),
        metadata_path=Path("/tmp/louise/metadata.json"),
    )

    assert character.name == "louise"
    assert character.voice_path.name == "voice.qvp"


def test_character_metadata_defaults():

    metadata = CharacterMetadata(
        name="louise",
        source_audio="/tmp/audio.wav",
    )

    assert metadata.version == 1
    assert metadata.voice_filename == "voice.qvp"
    assert metadata.transcript_filename == "transcript.txt"
    assert metadata.created_by == "mimic-tts"


def test_create_character_result():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
        voice_path=Path("/tmp/louise/voice.qvp"),
        transcript_path=Path("/tmp/louise/transcript.txt"),
        metadata_path=Path("/tmp/louise/metadata.json"),
    )

    result = CreateCharacterResult(
        character=character,
        transcript="hello world",
    )

    assert result.character.name == "louise"
    assert result.transcript == "hello world"


