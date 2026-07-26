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


# Original voice profile information.
#
# Contains:
# - source audio path
# - transcript reference
# - engine metadata
#
DEFAULT_VOICE_FILENAME = "voice.pt"


# Cached Qwen VoiceClonePrompt.
#
# Contains:
# - speaker embedding
# - reference speech codes
# - clone configuration
#
# This avoids rebuilding the prompt every generation.
#
DEFAULT_PROMPT_FILENAME = "voice_prompt.pt"


# Human-readable character information.
DEFAULT_METADATA_FILENAME = "metadata.json"


# Whisper generated transcript.
DEFAULT_TRANSCRIPT_FILENAME = "transcript.txt"



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
        └── test/
            ├── metadata.json
            ├── transcript.txt
            ├── voice.pt
            └── voice_prompt.pt
    """

    name: str

    directory: Path

    voice_filename: str = DEFAULT_VOICE_FILENAME



    def __post_init__(self):
        """
        Ensure directory is always stored as Path.

        Allows callers to pass:

            "/app/characters/test"

        while internally using:

            Path(...)
        """

        self.directory = Path(
            self.directory
        )



    @property
    def voice_path(self) -> Path:
        """
        Path to stored voice profile.

        Contains:
        - source audio information
        - clone metadata
        """

        return (
            self.directory
            /
            self.voice_filename
        )



    @property
    def metadata_path(self) -> Path:
        """
        Path to character metadata.
        """

        return (
            self.directory
            /
            DEFAULT_METADATA_FILENAME
        )



    @property
    def transcript_path(self) -> Path:
        """
        Path to Whisper transcript.
        """

        return (
            self.directory
            /
            DEFAULT_TRANSCRIPT_FILENAME
        )



    @property
    def prompt_path(self) -> Path:
        """
        Path to cached Qwen voice clone prompt.

        Stores expensive generated data:

        - speaker embedding
        - speech token codes
        """

        return (
            self.directory
            /
            DEFAULT_PROMPT_FILENAME
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
    - Future voice design workflows
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

    speaker: str = ""


    #
    # Voice clone source
    #

    source_audio: str = ""


    #
    # Default performance settings
    #

    instructions: str = ""

    personality: str = ""

    description: str = ""


    #
    # Stored filename
    #

    voice_filename: str = DEFAULT_VOICE_FILENAME

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