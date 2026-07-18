from pathlib import Path

from app.core.characters.models import (
    Character,
    CharacterMetadata,
    CreateCharacterResult,
)


def test_character_dataclass():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    assert character.name == "louise"
    assert character.directory == Path("/tmp/louise")

    assert character.voice_path.name == "voice.qvp"
    assert character.metadata_path.name == "metadata.json"
    assert character.transcript_path.name == "transcript.txt"


def test_character_metadata_defaults():

    metadata = CharacterMetadata(
        name="louise",
        source_audio="/tmp/audio.wav",
    )

    assert metadata.name == "louise"
    assert metadata.source_audio == "/tmp/audio.wav"

    assert metadata.personality == ""
    assert metadata.description == ""

    assert metadata.voice_filename == "voice.qvp"


def test_character_metadata_custom_values():

    metadata = CharacterMetadata(
        name="louise",
        source_audio="/tmp/audio.wav",
        personality="Smart and sarcastic",
        description="Child genius",
        voice_filename="custom.qvp",
    )

    assert metadata.personality == "Smart and sarcastic"
    assert metadata.description == "Child genius"
    assert metadata.voice_filename == "custom.qvp"


def test_create_character_result():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    result = CreateCharacterResult(
        character=character,
        transcript="hello world",
    )

    assert result.character.name == "louise"
    assert result.transcript == "hello world"