import argparse

from app.commands.transcribe import transcribe_command
from app.commands.create_character import create_character_command



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
        help=(
            "Transcribe an audio file using Whisper"
        )
    )


    transcribe_parser.add_argument(
        "--audio",
        required=True,
        help=(
            "Path to audio file"
        )
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



    #
    # Roleplay / Generation placeholder
    #
    # Added later:
    #
    # roleplay
    #   --character
    #   --text
    #   --emotion
    #   --output
    #



    args = parser.parse_args()



    if args.command == "transcribe":

        transcribe_command(args)



    elif args.command == "create-character":

        create_character_command(args)



if __name__ == "__main__":
    main()