from app.core.characters.storage import CharacterStorage
from app.core.characters.models import CharacterMetadata


def test_create_character(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create(
        "louise"
    )

    assert character.directory.exists()
    assert character.voice_path.name == "voice.qvp"


def test_save_and_load_transcript(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create(
        "louise"
    )

    storage.save_transcript(
        character,
        "hello world",
    )

    transcript = storage.load_transcript(
        character
    )

    assert transcript == "hello world"


def test_save_and_load_metadata(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create(
        "louise"
    )

    metadata = CharacterMetadata(
        name="louise",
        source_audio="/tmp/audio.wav",
        personality="Energetic child genius",
        description="A mischievous character",
    )

    storage.save_metadata(
        character,
        metadata,
    )

    loaded = storage.load_metadata(
        character,
    )

    assert loaded.name == "louise"
    assert loaded.source_audio == "/tmp/audio.wav"

    assert loaded.personality == (
        "Energetic child genius"
    )

    assert loaded.description == (
        "A mischievous character"
    )


def test_exists(tmp_path):

    storage = CharacterStorage(tmp_path)

    assert not storage.exists(
        "louise"
    )

    storage.create(
        "louise"
    )

    assert storage.exists(
        "louise"
    )


def test_delete(tmp_path):

    storage = CharacterStorage(tmp_path)

    storage.create(
        "louise"
    )

    storage.delete(
        "louise"
    )

    assert not storage.exists(
        "louise"
    )