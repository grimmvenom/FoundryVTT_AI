"""
######################################
Summary:
######################################
- Character filesystem access
- Handles persistence of:
    - metadata.json
    - transcript.txt
    - voice.pt
    - voice_prompt.pt
"""

from __future__ import annotations

import json
import shutil

from dataclasses import asdict
from pathlib import Path
from typing import Any

import torch

from app.config import settings

from .models import (
    Character,
    CharacterMetadata,
)


class CharacterStorage:
    """
    Handles all filesystem operations
    related to character storage.

    This class intentionally knows nothing
    about Qwen or Whisper.

    It only manages files.
    """

    def __init__(
        self,
        root: Path |None = None,
    ):
        """
        Initialize character storage.

        Args:
            root:
                Optional override directory.

                Defaults to:
                settings.characters_dir
        """

        self.root = Path(
            root or settings.characters_dir
        )

    ############################################################
    #
    # Path Helpers
    #
    ############################################################

    def character_path(
        self,
        name: str,
    ) -> Path:
        """
        Return filesystem directory
        for a character.
        """

        return self.root / name

    ############################################################
    #
    # Character CRUD
    #
    ############################################################

    def create(
        self,
        name: str,
        overwrite: bool = False,
    ) -> Character:
        """
        Create a new character directory.

        Args:
            name:
                Character name.

            overwrite:
                Delete existing character
                before recreating.

        Returns:
            Character object.
        """

        directory = self.character_path(
            name
        )

        if directory.exists():

            if not overwrite:

                raise FileExistsError(
                    f"Character already exists: {name}"
                )

            shutil.rmtree(
                directory
            )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return Character(
            name=name,
            directory=directory,
        )

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check if character exists.
        """

        return self.character_path(
            name
        ).is_dir()

    def delete(
        self,
        name: str,
    ) -> None:
        """
        Delete a character completely.
        """

        shutil.rmtree(
            self.character_path(name),
            ignore_errors=True,
        )

    def load(
        self,
        name: str,
    ) -> Character:
        """
        Load character filesystem reference.
        """

        directory = self.character_path(
            name
        )

        if not directory.exists():

            raise FileNotFoundError(
                f"Character not found: {name}"
            )

        return Character(
            name=name,
            directory=directory,
        )

    def list(
        self,
    ) -> list[Character]:
        """
        Return all stored characters
        sorted by name.
        """

        if not self.root.exists():
            return []

        characters = [
            Character(
                name=directory.name,
                directory=directory,
            )
            for directory in self.root.iterdir()
            if directory.is_dir()
        ]

        return sorted(
            characters,
            key=lambda c: c.name.lower(),
        )

    ############################################################
    #
    # Transcript Handling
    #
    ############################################################

    def save_transcript(
        self,
        character: Character,
        transcript: str,
    ) -> None:
        """
        Save Whisper transcript.
        """

        character.transcript_path.write_text(
            transcript,
            encoding="utf-8",
        )

    def load_transcript(
        self,
        character: Character,
    ) -> str:
        """
        Load saved transcript.
        """

        return character.transcript_path.read_text(
            encoding="utf-8",
        )

    ############################################################
    #
    # Metadata Handling
    #
    ############################################################

    def save_metadata(
        self,
        character: Character,
        metadata: CharacterMetadata,
    ) -> None:
        """
        Save character metadata.
        """

        character.metadata_path.write_text(
            json.dumps(
                asdict(metadata),
                indent=4,
            ),
            encoding="utf-8",
        )

    def load_metadata(
        self,
        character: Character,
    ) -> CharacterMetadata:
        """
        Load character metadata.
        """

        data = json.loads(
            character.metadata_path.read_text(
                encoding="utf-8",
            )
        )

        return CharacterMetadata(
            **data
        )

    def load_assets(
        self,
        character: Character,
    ) -> tuple[
        CharacterMetadata,
        Any,
    ]:
        """
        Load all runtime character assets.

        Returns:
            (
                CharacterMetadata,
                VoiceClonePromptItem list,
            )
        """

        return (
            self.load_metadata(character),
            self.load_voice_prompt(character),
        )

    ############################################################
    #
    # Voice Profile Handling
    #
    ############################################################

    def save_voice_profile(
        self,
        character: Character,
        source_path: Path,
    ) -> None:
        """
        Save legacy voice profile.

        This is metadata only.

        The actual Qwen prompt is stored
        separately in voice_prompt.pt.
        """

        shutil.copy2(
            source_path,
            character.voice_path,
        )

    def load_voice_profile(
        self,
        character: Character,
    ) -> Path:
        """
        Return path to legacy voice profile.
        """

        return character.voice_path

    ############################################################
    #
    # Qwen Voice Clone Prompt Handling
    #
    ############################################################

    def has_voice_prompt(
        self,
        character: Character,
    ) -> bool:
        """
        Check whether a cached voice prompt exists.
        """

        return character.prompt_path.exists()

    def save_voice_prompt(
        self,
        character: Character,
        prompt: Any,
    ) -> None:
        """
        Save Qwen VoiceClonePromptItem data.

        Stores:
            - reference audio codes
            - speaker embedding
            - clone settings

        This avoids recreating the prompt
        on every generation.
        """

        torch.save(
            prompt,
            character.prompt_path,
        )

    def load_voice_prompt(
        self,
        character: Character,
    ) -> Any:
        """
        Load Qwen VoiceClonePromptItem data.

        Returns:
            List[VoiceClonePromptItem]
        """

        if not character.prompt_path.exists():

            raise FileNotFoundError(
                f"Missing voice prompt: {character.prompt_path}"
            )

        return torch.load(
            character.prompt_path,
            map_location="cpu",
            weights_only=False,
        )