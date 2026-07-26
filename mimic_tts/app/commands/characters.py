"""
Character management commands.

Commands:
    characters create
    characters list
"""

from pathlib import Path

from app.core.characters.manager import CharacterManager


def characters_command(args):
    """
    Dispatch character subcommands.
    """

    if args.characters_command == "create":
        create_character(args)

    elif args.characters_command == "list":
        list_characters(args)


def create_character(args):
    """
    Create a reusable character.
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
        personality=args.personality,
        description=args.description,
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


def list_characters(args):
    """
    List all stored characters.
    """

    manager = CharacterManager(
        storage=None,
        speech_to_text=None,
        engine=None,
    )

    characters = manager.list()

    if not characters:
        print("No characters found.")
        return

    print()
    print("=" * 60)
    print("Characters")
    print("=" * 60)

    for character in characters:
        print(character.name)
    print(f"\n\n")