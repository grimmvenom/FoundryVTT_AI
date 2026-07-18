from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.commands.create_character import create_character_command


def make_result(tmp_path):
    character = MagicMock()

    character.name = "louise"
    character.voice_path = tmp_path / "louise" / "voice.qvp"
    character.transcript_path = (
        tmp_path / "louise" / "transcript.txt"
    )
    character.metadata_path = (
        tmp_path / "louise" / "metadata.json"
    )

    result = MagicMock()
    result.character = character

    return result


def test_create_character_command_success(
    tmp_path,
    monkeypatch,
):
    audio = tmp_path / "voice.wav"
    audio.touch()

    args = Namespace(
        audio=str(audio),
        name="louise",
        instructions="Energetic child voice",
    )

    fake_manager = MagicMock()

    fake_manager.create_character.return_value = (
        make_result(tmp_path)
    )

    monkeypatch.setattr(
        "app.commands.create_character.CharacterManager",
        lambda *args, **kwargs: fake_manager,
    )

    create_character_command(args)

    fake_manager.create_character.assert_called_once_with(
        name="louise",
        audio_path=Path(audio),
        instructions="Energetic child voice",
    )


def test_create_character_command_without_instructions(
    tmp_path,
    monkeypatch,
):
    audio = tmp_path / "voice.wav"
    audio.touch()

    args = Namespace(
        audio=str(audio),
        name="louise",
        instructions=None,
    )

    fake_manager = MagicMock()

    fake_manager.create_character.return_value = (
        make_result(tmp_path)
    )

    monkeypatch.setattr(
        "app.commands.create_character.CharacterManager",
        lambda *args, **kwargs: fake_manager,
    )

    create_character_command(args)

    fake_manager.create_character.assert_called_once_with(
        name="louise",
        audio_path=Path(audio),
        instructions=None,
    )


def test_create_character_command_propagates_errors(
    tmp_path,
    monkeypatch,
):
    audio = tmp_path / "missing.wav"

    args = Namespace(
        audio=str(audio),
        name="louise",
        instructions=None,
    )

    fake_manager = MagicMock()

    fake_manager.create_character.side_effect = (
        FileNotFoundError("Audio file not found")
    )

    monkeypatch.setattr(
        "app.commands.create_character.CharacterManager",
        lambda *args, **kwargs: fake_manager,
    )

    with pytest.raises(FileNotFoundError):
        create_character_command(args)