from pathlib import Path

from app.core.characters.models import (
    Character,
    CharacterMetadata,
    CreateCharacterResult,
    RoleplayRequest,
)


###########################################################################
#
# Character
#
###########################################################################


def test_character_dataclass():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    assert character.name == "louise"
    assert character.directory == Path("/tmp/louise")

    assert character.voice_path == Path("/tmp/louise/voice.pt")
    assert character.metadata_path == Path("/tmp/louise/metadata.json")
    assert character.transcript_path == Path("/tmp/louise/transcript.txt")
    assert character.prompt_path == Path("/tmp/louise/voice_prompt.pt")


###########################################################################
#
# CharacterMetadata
#
###########################################################################


def test_character_metadata_defaults():

    metadata = CharacterMetadata(
        name="louise",
        source_audio="/tmp/audio.wav",
    )

    assert metadata.name == "louise"
    assert metadata.speaker == ""

    assert metadata.source_audio == "/tmp/audio.wav"

    assert metadata.instructions == ""
    assert metadata.personality == ""
    assert metadata.description == ""

    assert metadata.voice_filename == "voice.pt"


def test_character_metadata_custom_values():

    metadata = CharacterMetadata(
        name="louise",
        speaker="Louise",

        source_audio="/tmp/audio.wav",

        instructions="Energetic child",

        personality="Smart and sarcastic",

        description="Child genius",

        voice_filename="custom.pt",
    )

    assert metadata.speaker == "Louise"

    assert metadata.instructions == "Energetic child"

    assert metadata.personality == "Smart and sarcastic"

    assert metadata.description == "Child genius"

    assert metadata.voice_filename == "custom.pt"


###########################################################################
#
# CreateCharacterResult
#
###########################################################################


def test_create_character_result():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    result = CreateCharacterResult(
        character=character,
        transcript="hello world",
    )

    assert result.character is character
    assert result.transcript == "hello world"


###########################################################################
#
# RoleplayRequest
#
###########################################################################


def test_roleplay_request_defaults():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    request = RoleplayRequest(
        character=character,
        text="Hello!",
    )

    assert request.character is character

    assert request.text == "Hello!"

    assert request.instructions == ""

    assert request.emotion == "neutral"

    assert request.output is None


def test_roleplay_request_custom_values():

    character = Character(
        name="louise",
        directory=Path("/tmp/louise"),
    )

    output = Path("/tmp/output.wav")

    request = RoleplayRequest(
        character=character,
        text="Hello!",

        instructions="Speak quickly",

        emotion="excited",

        output=output,
    )

    assert request.instructions == "Speak quickly"

    assert request.emotion == "excited"

    assert request.output == output