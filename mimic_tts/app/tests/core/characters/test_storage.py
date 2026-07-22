from pathlib import Path

import torch

from app.core.characters.models import (
    CharacterMetadata,
)
from app.core.characters.storage import (
    CharacterStorage,
)


###########################################################################
#
# Character Creation
#
###########################################################################


def test_create_character(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create("louise")

    assert character.directory.exists()

    assert character.voice_path == (
        tmp_path / "louise" / "voice.pt"
    )

    assert character.metadata_path == (
        tmp_path / "louise" / "metadata.json"
    )

    assert character.transcript_path == (
        tmp_path / "louise" / "transcript.txt"
    )

    assert character.prompt_path == (
        tmp_path / "louise" / "voice_prompt.pt"
    )


def test_create_overwrite(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create("louise")

    character.directory.joinpath(
        "junk.txt"
    ).write_text("junk")

    character2 = storage.create(
        "louise",
        overwrite=True,
    )

    assert character2.directory.exists()

    assert not character2.directory.joinpath(
        "junk.txt"
    ).exists()


###########################################################################
#
# Transcript
#
###########################################################################


def test_save_and_load_transcript(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create("louise")

    storage.save_transcript(
        character,
        "hello world",
    )

    assert (
        storage.load_transcript(character)
        == "hello world"
    )


###########################################################################
#
# Metadata
#
###########################################################################


def test_save_and_load_metadata(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create("louise")

    metadata = CharacterMetadata(

        name="louise",

        speaker="",

        source_audio="/tmp/audio.wav",

        instructions="Speak quickly",

        personality="Energetic child genius",

        description="A mischievous character",
    )

    storage.save_metadata(
        character,
        metadata,
    )

    loaded = storage.load_metadata(
        character
    )

    assert loaded.name == "louise"

    assert loaded.source_audio == "/tmp/audio.wav"

    assert loaded.instructions == (
        "Speak quickly"
    )

    assert loaded.personality == (
        "Energetic child genius"
    )

    assert loaded.description == (
        "A mischievous character"
    )


###########################################################################
#
# Voice Prompt
#
###########################################################################


def test_save_and_load_voice_prompt(tmp_path):

    storage = CharacterStorage(tmp_path)

    character = storage.create("louise")

    prompt = [
        {
            "speaker": "Louise",
            "embedding": torch.zeros(4),
        }
    ]

    storage.save_voice_prompt(
        character,
        prompt,
    )

    loaded = storage.load_voice_prompt(
        character,
    )

    assert isinstance(
        loaded,
        list,
    )

    assert len(loaded) == 1

    assert loaded[0]["speaker"] == "Louise"

    assert torch.equal(
        loaded[0]["embedding"],
        torch.zeros(4),
    )


###########################################################################
#
# Exists / Delete
#
###########################################################################


def test_exists(tmp_path):

    storage = CharacterStorage(tmp_path)

    assert not storage.exists(
        "louise"
    )

    storage.create("louise")

    assert storage.exists(
        "louise"
    )


def test_delete(tmp_path):

    storage = CharacterStorage(tmp_path)

    storage.create("louise")

    storage.delete("louise")

    assert not storage.exists(
        "louise"
    )