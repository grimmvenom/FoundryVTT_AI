"""
Character Storage

Filesystem abstraction for character data.

Responsible for:
- creating character directories
- saving/loading metadata
- saving/loading transcripts
- locating voice profiles
"""

import json
from pathlib import Path
from app.core.characters.models import (
    Character,
    CharacterMetadata,
)
from dataclasses import asdict


class CharacterStorage:

    def __init__(
        self,
        root_directory="/app/tts_data/characters",
    ):

        self.root = Path(root_directory)

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    #
    # Path helpers
    #

    def character_directory(
        self,
        name: str,
    ) -> Path:

        return self.root / name


    def voice_path(
        self,
        name: str,
        filename="voice.qvp",
    ) -> Path:

        return (
            self.character_directory(name)
            / filename
        )


    def transcript_path(
        self,
        name: str,
    ) -> Path:

        return (
            self.character_directory(name)
            / "transcript.txt"
        )


    def metadata_path(
        self,
        name: str,
    ) -> Path:

        return (
            self.character_directory(name)
            / "metadata.json"
        )

    #
    # Character management
    #

    def exists(
        self,
        name: str,
    ) -> bool:

        return self.character_directory(name).exists()


    def create(
        self,
        name: str,
    ) -> Character:

        directory = self.character_directory(name)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return Character(
            name=name,
            directory=directory,
            voice_path=self.voice_path(name),
            transcript_path=self.transcript_path(name),
            metadata_path=self.metadata_path(name),
        )


    def delete(
        self,
        name: str,
    ):

        import shutil

        directory = self.character_directory(name)

        if directory.exists():
            shutil.rmtree(directory)

    #
    # Transcript
    #

    def save_transcript(
        self,
        character: Character,
        transcript: str,
    ):

        character.transcript_path.write_text(
            transcript,
            encoding="utf-8",
        )


    def load_transcript(
        self,
        character: Character,
    ) -> str:

        return character.transcript_path.read_text(
            encoding="utf-8"
        )

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
            ),
            encoding="utf-8",
        )


    def load_metadata(
        self,
        character: Character,
    ) -> CharacterMetadata:

        data = json.loads(
            character.metadata_path.read_text(
                encoding="utf-8"
            )
        )

        return CharacterMetadata(**data)