"""
######################################
Summary:
######################################
- Shared Character Models
"""

from dataclasses import dataclass
from pathlib import Path


DEFAULT_VOICE_FILENAME = "voice.qvp"
DEFAULT_METADATA_FILENAME = "metadata.json"
DEFAULT_TRANSCRIPT_FILENAME = "transcript.txt"


@dataclass(slots=True)
class Character:
    """
    Represents a persistent roleplay character.
    """

    name: str
    directory: Path

    voice_filename: str = DEFAULT_VOICE_FILENAME

    @property
    def voice_path(self) -> Path:
        return self.directory / self.voice_filename

    @property
    def metadata_path(self) -> Path:
        return self.directory / DEFAULT_METADATA_FILENAME

    @property
    def transcript_path(self) -> Path:
        return self.directory / DEFAULT_TRANSCRIPT_FILENAME


@dataclass(slots=True)
class CharacterMetadata:
    name: str
    source_audio: str = ""

    personality: str = ""
    description: str = ""

    voice_filename: str = DEFAULT_VOICE_FILENAME


@dataclass(slots=True)
class CreateCharacterResult:
    character: Character
    transcript: str


@dataclass(slots=True)
class RoleplayRequest:
    character: Character
    script: str
    instructions: str = ""
    emotion: str = "neutral"
    output: Path | None = None


@dataclass(slots=True)
class RoleplayRequest:
    character: Character

    text: str

    instructions: str = ""

    emotion: str = "neutral"

    output_path: Path | None = None