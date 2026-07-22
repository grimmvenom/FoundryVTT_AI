"""
Create a reusable character voice.

CLI wrapper around CharacterManager.
"""

from pathlib import Path

from app.core.characters.manager import CharacterManager


def create_character_command(args):
    """
    CLI command for creating a reusable character.
    """

    print()
    print("=" * 60)
    print("Creating Character")
    print("=" * 60)

    manager = CharacterManager(
        storage=None,
        speech_to_text=None,
        engine=None,
    )

    result = manager.create_character(
        name=args.name,
        audio_path=Path(args.audio),
        instructions=args.instructions,
        overwrite=args.overwrite,
    )

    print()
    print("=" * 60)
    print("Character Created")
    print("=" * 60)

    print()
    print(f"Name: {result.character.name}")
    print(f"Voice Profile: {result.character.voice_path}")
    print(f"Transcript: {result.character.transcript_path}")
    print(f"Metadata: {result.character.metadata_path}")