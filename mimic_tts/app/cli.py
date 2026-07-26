import argparse


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Mimic-TTS command line interface"
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
    )

    ############################################################
    #
    # Transcribe
    #
    ############################################################

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

    ############################################################
    #
    # Characters
    #
    ############################################################

    characters_parser = subparsers.add_parser(
        "characters",
        help="Manage reusable characters",
    )

    characters_subparsers = (
        characters_parser.add_subparsers(
            dest="characters_command",
            required=True,
        )
    )

    #
    # characters create
    #

    create_parser = (
        characters_subparsers.add_parser(
            "create",
            help="Create a reusable character",
        )
    )

    create_parser.add_argument(
        "--audio",
        required=True,
        help=(
            "Reference audio file "
            "(.wav/.mp3/.m4a/etc)"
        ),
    )

    create_parser.add_argument(
        "--name",
        required=True,
        help="Character name",
    )

    create_parser.add_argument(
        "--instructions",
        default=None,
        help=(
            "Voice instructions. "
            "Examples: personality, emotion, delivery style"
        ),
    )

    create_parser.add_argument(
        "--personality",
        default="",
        help=(
            "Character personality description"
        ),
    )

    create_parser.add_argument(
        "--description",
        default="",
        help=(
            "Character background description"
        ),
    )

    create_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing character profile",
    )

    #
    # characters list
    #

    characters_subparsers.add_parser(
        "list",
        help="List stored characters",
    )

    ############################################################
    #
    # Roleplay
    #
    ############################################################

    roleplay_parser = subparsers.add_parser(
        "roleplay",
        help="Generate character dialogue",
    )

    roleplay_parser.add_argument(
        "--character",
        required=True,
        help="Character name",
    )

    roleplay_parser.add_argument(
        "--script",
        help="Text to generate",
    )

    roleplay_parser.add_argument(
        "--script-file",
        help="Read script from file",
    )

    roleplay_parser.add_argument(
        "--instructions",
        default=None,
        help="Temporary voice direction",
    )

    roleplay_parser.add_argument(
        "--emotion",
        default=None,
        help="Emotion for delivery",
    )

    roleplay_parser.add_argument(
        "--output",
        default=None,
        help="Output wav path",
    )

    ############################################################
    #
    # Dispatch
    #
    ############################################################

    args = parser.parse_args()

    if args.command == "transcribe":

        from app.commands.transcribe import (
            transcribe_command,
        )

        transcribe_command(args)

    elif args.command == "characters":

        from app.commands.characters import (
            characters_command,
        )

        characters_command(args)

    elif args.command == "roleplay":

        from app.commands.roleplay import (
            roleplay_command,
        )

        roleplay_command(args)


if __name__ == "__main__":
    main()