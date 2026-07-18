"""
######################################
Summary:
######################################
- Character filesystem access
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from dataclasses import asdict
from app.config import settings

from .models import (
    Character,
    CharacterMetadata,
)


class CharacterStorage:

    def __init__(
        self,
        root: Path | None = None,
    ):

        self.root = Path(
            root or settings.characters_dir
        )

    #
    # Helpers
    #

    def character_path(
        self,
        name: str,
    ) -> Path:

        return self.root / name

    #
    # CRUD
    #

    def create(
        self,
        name: str,
    ) -> Character:

        directory = self.character_path(
            name
        )

        directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        return Character(
            name=name,
            directory=directory,
        )

    def exists(
        self,
        name: str,
    ) -> bool:

        return self.character_path(
            name
        ).exists()

    def delete(
        self,
        name: str,
    ):

        shutil.rmtree(
            self.character_path(name),
            ignore_errors=True,
        )

    #
    # Transcript
    #

    def save_transcript(
        self,
        character: Character,
        transcript: str,
    ):

        character.transcript_path.write_text(
            transcript
        )

    def load_transcript(
        self,
        character: Character,
    ) -> str:

        return character.transcript_path.read_text()

    #
    # Metadata
    #

    def save_metadata(
        self,
        character: Character,
        metadata: CharacterMetadata,
    ):

        character.metadata_path.write_text(
            json.dumps(
                asdict(metadata),
                indent=4,
            )
        )

    def load_metadata(
        self,
        character: Character,
    ) -> CharacterMetadata:

        data = json.loads(
            character.metadata_path.read_text()
        )

        return CharacterMetadata(
            **data
        )