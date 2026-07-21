import argparse

# from app.commands.transcribe import transcribe_command
# from app.commands.create_character import create_character_command
# from app.commands.roleplay import roleplay_command


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Mimic-TTS command line interface"
        )
    )


    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands"
    )


    #
    # Transcribe
    #

    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe an audio file",
    )

    transcribe_parser.add_argument(
        "--audio",
        required=True,
        help="Audio file to transcribe",
    )

    transcribe_parser.add_argument(
        "--model",
        default="large-v3",
        help="Whisper model",
    )

    transcribe_parser.add_argument(
        "--device",
        default="cuda",
        help="Inference device",
    )

    transcribe_parser.add_argument(
        "--output",
        help="Optional transcript output file",
    )

    #
    # Create Character
    #

    character_parser = subparsers.add_parser(
        "create-character",
        help=(
            "Create a reusable character voice"
        )
    )


    character_parser.add_argument(
        "--audio",
        required=True,
        help=(
            "Reference audio file "
            "(.wav/.mp3/.m4a/etc)"
        )
    )


    character_parser.add_argument(
        "--name",
        required=True,
        help=(
            "Character name"
        )
    )


    character_parser.add_argument(
        "--instructions",
        default=None,
        help=(
            "Voice instructions. "
            "Examples: personality, emotion, delivery style"
        )
    )


    character_parser.add_argument(
        "--output-dir",
        default="/app/voices",
        help=(
            "Directory where character files are stored"
        )
    )

    character_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing character profile",
    )


    #
    # Roleplay
    #

    roleplay_parser = subparsers.add_parser(
        "roleplay",
        help=(
            "Generate character dialogue"
        )
    )


    roleplay_parser.add_argument(
        "--character",
        required=True,
        help=(
            "Character name"
        )
    )


    roleplay_parser.add_argument(
        "--script",
        help=(
            "Text to generate"
        )
    )


    roleplay_parser.add_argument(
        "--script-file",
        help=(
            "Read script from file"
        )
    )


    roleplay_parser.add_argument(
        "--instructions",
        default=None,
        help=(
            "Temporary voice direction"
        )
    )


    roleplay_parser.add_argument(
        "--emotion",
        default=None,
        help=(
            "Emotion for delivery"
        )
    )


    roleplay_parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output wav path"
        )
    )


    args = parser.parse_args()


    if args.command == "transcribe":
        from app.commands.transcribe import (transcribe_command)
        transcribe_command(args)

    elif args.command == "create-character":
        from app.commands.create_character import (create_character_command)
        create_character_command(args)


    elif args.command == "roleplay":
        from app.commands.roleplay import (roleplay_command)
        roleplay_command(args)


if __name__ == "__main__":
    main()