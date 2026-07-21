"""
Roleplay Command

Generate character dialogue using
a stored voice profile.
"""

from pathlib import Path

from app.core.audio.utils import (
    default_roleplay_filename,
)

from app.core.audio.writer import (
    write_wav,
)


def roleplay_command(
    args,
    manager_factory=None,
):
    """
    Generate roleplay audio.

    manager_factory exists to make this
    command easy to unit test without
    loading Qwen/PyTorch.
    """

    #
    # Dependency injection
    #

    if manager_factory:

        manager = manager_factory()

    else:

        from app.core.characters.manager import (
            CharacterManager,
        )

        manager = CharacterManager()


    #
    # Load character
    #

    character = manager.get(
        args.character
    )


    #
    # Resolve script
    #

    script = args.script

    if args.script_file:

        script = Path(
            args.script_file
        ).read_text(
            encoding="utf-8"
        )


    if not script:

        raise ValueError(
            "Provide --script or --script-file"
        )


    #
    # Resolve output path
    #

    if args.output:

        output = Path(
            args.output
        )

    else:

        output = default_roleplay_filename(
            character.name
        )


    #
    # Generate audio
    #

    wav, sample_rate = (
        manager.generate_roleplay(
            character=character,
            text=script,
            instructions=args.instructions,
            emotion=args.emotion,
        )
    )


    #
    # Save wav
    #

    write_wav(
        output,
        wav,
        sample_rate,
    )


    print(
        f"Generated: {output}"
    )