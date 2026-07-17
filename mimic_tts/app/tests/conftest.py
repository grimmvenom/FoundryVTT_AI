"""
tests/conftest.py

Shared pytest fixtures for character core tests.
"""

from pathlib import Path
from dataclasses import asdict

import pytest

from app.core.characters.models import Character, CharacterMetadata
from app.core.characters.storage import CharacterStorage
from app.core.characters.manager import CharacterManager


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """
    Temporary application data directory.
    """
    return tmp_path / "tts_data"


@pytest.fixture
def character_storage(temp_data_dir: Path) -> CharacterStorage:
    """
    Real CharacterStorage using isolated filesystem.
    """
    return CharacterStorage(
        root=temp_data_dir / "characters"
    )


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

@pytest.fixture
def character_name() -> str:
    return "test_character"


@pytest.fixture
def sample_metadata(character_name: str) -> CharacterMetadata:
    """
    Default character metadata object.
    """
    return CharacterMetadata(
        name=character_name,
        voice_filename="voice.qvp",
        transcript_filename="transcript.txt",
    )


@pytest.fixture
def sample_character(
    character_name: str,
    temp_data_dir: Path,
) -> Character:
    """
    Example Character object.
    """
    return Character(
        name=character_name,
        path=temp_data_dir / "characters" / character_name,
    )


@pytest.fixture
def sample_audio_file(tmp_path: Path) -> Path:
    """
    Fake audio input file.

    Tests should not depend on real audio.
    """
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"fake audio data")

    return audio


# ---------------------------------------------------------------------------
# Fake dependencies
# ---------------------------------------------------------------------------

class FakeSpeechToText:
    """
    Fake transcription service.
    """

    def __init__(self, transcript: str = "Hello world"):
        self.transcript = transcript
        self.calls = []

    def transcribe(self, audio_path: Path) -> str:
        self.calls.append(audio_path)
        return self.transcript


@pytest.fixture
def fake_speech_to_text():
    return FakeSpeechToText()


class FakeVoiceEngine:
    """
    Fake Qwen3-TTS engine.

    Mimics creating a .qvp voice profile.
    """

    def __init__(self):
        self.calls = []

    def create_character(
        self,
        audio_path: Path,
        transcript: str,
        output_path: Path,
        instructions=None,
    ):
        self.calls.append(
            {
                "audio_path": audio_path,
                "transcript": transcript,
                "output_path": output_path,
                "instructions": instructions,
            }
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            "fake voice profile"
        )


@pytest.fixture
def fake_voice_engine():
    return FakeVoiceEngine()


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

@pytest.fixture
def character_manager(
    character_storage,
    fake_speech_to_text,
    fake_voice_engine,
):
    """
    Fully wired CharacterManager.
    """

    return CharacterManager(
        storage=character_storage,
        speech_to_text=fake_speech_to_text,
        engine=fake_voice_engine,
    )