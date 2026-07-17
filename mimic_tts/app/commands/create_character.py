"""
Create a reusable character voice.

Workflow:

Audio File
    |
    v
Whisper transcription
    |
    v
Qwen3 voice clone profile (.qvp)
    |
    v
Character metadata
"""

from pathlib import Path

from app.core.speech_to_text import SpeechToText
from app.core.qwen3_engine import Qwen3Engine
from mimic_tts.app.core.characters.manager import CharacterManager



def create_character_command(args):
    """
    CLI command for creating a character voice.

    Steps:
        1. Validate audio
        2. Transcribe reference audio
        3. Create Qwen3 character profile
        4. Save character data
    """


    audio = Path(args.audio)


    print()
    print("=" * 60)
    print("Creating Character")
    print("=" * 60)



    #
    # Step 1:
    # Validate input
    #

    manager = CharacterManager(
        output_directory=args.output_dir
    )


    manager.validate_audio(
        audio
    )



    #
    # Step 2:
    # Transcribe
    #

    print()
    print("Transcribing reference audio...")


    stt = SpeechToText()

    transcript = stt.transcribe(
        audio
    )


    print()
    print("Transcript:")
    print(transcript)



    #
    # Step 3:
    # Load Qwen
    #

    engine = Qwen3Engine()

    engine.load()



    #
    # Step 4:
    # Create character
    #

    print()
    print("Creating character voice...")


    result = manager.create_character(
        name=args.name,
        audio_path=audio,
        transcript=transcript,
        engine=engine,
        instructions=args.instructions,
    )


    print()
    print("=" * 60)
    print("Character Created")
    print("=" * 60)

    print()
    print("Name:")
    print(result.name)

    print()
    print("Profile:")
    print(result.path)
