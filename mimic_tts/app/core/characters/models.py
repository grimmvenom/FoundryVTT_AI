"""
Character Models

Responsibilities:

- Define persistent character data structures
- Define character filesystem layout
- Provide shared objects between:
  - CLI
  - CharacterManager
  - CharacterStorage
  - Qwen3Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


############################################################
#
# Character File Defaults
#
############################################################

# Human-readable character information.
DEFAULT_METADATA_FILENAME = "metadata.json"

# Whisper generated transcript.
DEFAULT_TRANSCRIPT_FILENAME = "transcript.txt"

# Cached Qwen VoiceClonePrompt.
#
# Contains the expensive voice-cloning data generated from
# the source audio and transcript.
DEFAULT_PROMPT_FILENAME = "voice_prompt.pt"


############################################################
#
# Character
#
############################################################

@dataclass(slots=True)
class Character:
    """
    Represents a persistent roleplay character.

    Example:

        characters/
        └── jester/
            ├── metadata.json
            ├── transcript.txt
            └── voice_prompt.pt
    """

    name: str
    directory: Path

    def __post_init__(self):
        """
        Ensure directory is always stored as Path.
        """

        self.directory = Path(self.directory)

    @property
    def metadata_path(self) -> Path:
        """
        Path to character metadata.
        """

        return (
            self.directory
            / DEFAULT_METADATA_FILENAME
        )

    @property
    def transcript_path(self) -> Path:
        """
        Path to Whisper transcript.
        """

        return (
            self.directory
            / DEFAULT_TRANSCRIPT_FILENAME
        )

    @property
    def prompt_path(self) -> Path:
        """
        Path to cached Qwen voice clone prompt.

        This is the character's sole persistent
        voice-cloning asset.
        """

        return (
            self.directory
            / DEFAULT_PROMPT_FILENAME
        )


############################################################
#
# Character Metadata
#
############################################################

@dataclass(slots=True)
class CharacterMetadata:
    """
    Metadata describing a character.

    Supports:

    - Voice cloning
    - CustomVoice
    - Character personality
    - Character description
    - Default performance instructions
    """

    #
    # Metadata schema
    #

    schema_version: int = 1

    #
    # Identity
    #

    name: str = ""

    #
    # Qwen CustomVoice
    #
    # Kept for compatibility with potential future
    # CustomVoice characters.
    #

    speaker: str = ""

    #
    # Voice clone source
    #
    # Informational only. The source audio itself is
    # not stored as part of the character.
    #

    source_audio: str = ""

    #
    # Default character settings
    #

    instructions: str = ""

    personality: str = ""

    description: str = ""


############################################################
#
# Creation Result
#
############################################################

@dataclass(slots=True)
class CreateCharacterResult:
    """
    Returned after creating a character.
    """

    character: Character

    transcript: str


############################################################
#
# Update Result
#
############################################################

@dataclass(slots=True)
class UpdateCharacterResult:
    """
    Returned after updating a character.
    """

    character: Character

    transcript: str | None = None

    audio_updated: bool = False


############################################################
#
# Roleplay Request
#
############################################################

@dataclass(slots=True)
class RoleplayRequest:
    """
    Request to generate character speech.
    """

    character: Character

    text: str

    instructions: str = ""

    emotion: str = "neutral"

    output: Path | None = None