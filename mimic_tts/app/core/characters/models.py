"""
######################################
Summary:
######################################
- Holds Shared Return Objects

"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Character:
    """
    Where things live on disk
    """
    name: str
    directory: Path
    voice_path: Path
    transcript_path: Path
    metadata_path: Path


@dataclass(slots=True)
class CharacterMetadata:
    """
    Contents of metadata.json
    """
    name: str
    source_audio: str
    voice_filename: str = "voice.qvp"
    transcript_filename: str = "transcript.txt"
    instructions: str | None = None
    created_by: str = "mimic-tts"
    version: int = 1


@dataclass(slots=True)
class CreateCharacterResult:
    """
    Results of creating a character
    """
    character: Character
    transcript: str
