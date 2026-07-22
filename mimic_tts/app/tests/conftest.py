"""
Shared pytest fixtures.

These fixtures intentionally avoid loading:
- Whisper
- Qwen3-TTS
- CUDA

Everything here should be lightweight.
"""

from pathlib import Path

import pytest

from app.core.characters.models import (
    Character,
    CharacterMetadata,
)
from app.core.characters.storage import CharacterStorage
from app.core.characters.manager import CharacterManager


###########################################################################
#
# Temporary filesystem
#
###########################################################################


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    return tmp_path / "tts_data"


@pytest.fixture
def character_storage(temp_data_dir: Path):

    return CharacterStorage(
        root=temp_data_dir / "characters"
    )


###########################################################################
#
# Sample objects
#
###########################################################################


@pytest.fixture
def character_name():

    return "test"


@pytest.fixture
def sample_character(
    character_name,
    character_storage,
):

    character = character_storage.create(
        character_name,
        overwrite=True,
    )

    return character


@pytest.fixture
def sample_metadata():

    return CharacterMetadata(

        name="test",

        speaker="",

        source_audio="sample.wav",

        instructions="Energetic child",

        personality="",

        description="",
    )


@pytest.fixture
def sample_audio_file(tmp_path):

    audio = tmp_path / "sample.wav"

    audio.write_bytes(
        b"fake audio"
    )

    return audio


###########################################################################
#
# Fake Speech-To-Text
#
###########################################################################


class FakeSpeechToText:

    def __init__(self):

        self.calls = []

        self.transcript = (
            "This is a fake transcript."
        )


    def transcribe(
        self,
        audio_path,
    ):

        self.calls.append(
            Path(audio_path)
        )

        return self.transcript


@pytest.fixture
def fake_speech_to_text():

    return FakeSpeechToText()


###########################################################################
#
# Fake Qwen Engine
#
###########################################################################


class FakeVoiceEngine:

    def __init__(self):

        self.loaded = False

        self.calls = []


    def load(self):

        self.loaded = True


    def create_voice_profile(
        self,
        audio_path,
        transcript,
        output_path,
        instructions="",
    ):

        output_path.write_text(
            "fake profile"
        )

        self.calls.append(
            (
                "create_voice_profile",
                audio_path,
                transcript,
                output_path,
                instructions,
            )
        )

        return output_path


    def create_voice_clone_prompt(
        self,
        audio_path,
        transcript,
    ):

        prompt = [
            "fake-prompt"
        ]

        self.calls.append(
            (
                "create_voice_clone_prompt",
                audio_path,
                transcript,
            )
        )

        return prompt


    def generate_roleplay(
        self,
        text,
        prompt,
        metadata,
        instructions="",
        emotion="neutral",
    ):

        self.calls.append(
            (
                "generate_roleplay",
                text,
                prompt,
                metadata,
                instructions,
                emotion,
            )
        )

        return (
            b"fake wav",
            24000,
        )


@pytest.fixture
def fake_voice_engine():

    return FakeVoiceEngine()


###########################################################################
#
# CharacterManager
#
###########################################################################


@pytest.fixture
def character_manager(
    character_storage,
    fake_speech_to_text,
    fake_voice_engine,
):

    return CharacterManager(

        storage=character_storage,

        speech_to_text=fake_speech_to_text,

        engine=fake_voice_engine,
    )