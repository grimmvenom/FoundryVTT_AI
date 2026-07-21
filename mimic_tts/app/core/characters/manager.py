"""
Character Manager

Responsibilities:

- Validate source audio
- Generate transcripts
- Create Qwen voice clone profiles
- Save character metadata

This class coordinates services.

It does NOT contain:
- Qwen model logic
- Whisper logic
- filesystem details
"""


from pathlib import Path


from app.core.characters.models import (
    CharacterMetadata,
    CreateCharacterResult,
)


from app.core.characters.storage import (
    CharacterStorage,
)


from app.core.speech_to_text import (
    SpeechToText,
)


from app.core.qwen3_engine import (
    Qwen3Engine,
)



class CharacterManager:
    """
    Coordinates character creation and retrieval.

    Dependencies are injectable for testing.
    """



    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    }



    def __init__(
        self,
        storage=None,
        speech_to_text=None,
        engine=None,
    ):
        """
        Initialize manager services.

        Defaults:
            CharacterStorage
            SpeechToText
            Qwen3Engine

        Tests may inject mocks.
        """


        self.storage = (
            storage
            or CharacterStorage()
        )


        self.stt = (
            speech_to_text
            or SpeechToText()
        )


        self.engine = (
            engine
            or Qwen3Engine()
        )



    #
    # Validation
    #



    def validate_audio(
        self,
        audio_path,
    ) -> None:
        """
        Validate reference voice audio.
        """


        audio_path = Path(
            audio_path
        )


        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )


        if not audio_path.is_file():

            raise ValueError(
                f"Path is not a file: {audio_path}"
            )


        if (
            audio_path.suffix.lower()
            not in self.SUPPORTED_FORMATS
        ):

            raise ValueError(
                f"Unsupported audio format: {audio_path.suffix}"
            )



    #
    # Character creation
    #


    def create_character(
        self,
        *,
        name: str,
        audio_path,
        instructions=None,
        overwrite: bool = False,
    ):
        """
        Create a reusable cloned voice character.

        Pipeline:

        1. Validate reference audio
        2. Transcribe audio with Whisper
        3. Create character directory
        4. Generate Qwen voice clone prompt
        5. Save prompt cache
        6. Save transcript
        7. Save metadata
        """

        audio_path = Path(
            audio_path
        )


        #
        # Validate input audio
        #

        self.validate_audio(
            audio_path
        )


        #
        # Generate transcript
        #

        transcript = self.stt.transcribe(
            audio_path
        )


        if not transcript.strip():

            raise ValueError(
                "Transcript cannot be empty."
            )



        #
        # Create character directory
        #

        character = self.storage.create(
            name,
            overwrite=overwrite,
        )



        #
        # Load Qwen
        #

        self.engine.load()



        #
        # Generate cached VoiceClonePromptItem
        #
        # This is the expensive operation.
        #
        # It creates:
        # - reference speech codes
        # - speaker embedding
        #

        voice_prompt = (
            self.engine.create_voice_clone_prompt(
                audio_path=audio_path,
                transcript=transcript,
            )
        )



        #
        # Save prompt cache
        #

        self.storage.save_voice_prompt(
            character,
            voice_prompt,
        )



        #
        # Save transcript
        #

        self.storage.save_transcript(
            character,
            transcript,
        )



        #
        # Save metadata
        #

        metadata = CharacterMetadata(

            name=name,

            source_audio=str(
                audio_path
            ),

            instructions=(
                instructions
                or ""
            ),

            personality="",

            description="",
        )


        self.storage.save_metadata(
            character,
            metadata,
        )



        return CreateCharacterResult(
            character=character,
            transcript=transcript,
        )


    #
    # Helpers
    #



    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check if character exists.
        """


        return self.storage.exists(
            name
        )



    def delete(
        self,
        name: str,
    ):
        """
        Remove character.
        """


        self.storage.delete(
            name
        )



    def get(
        self,
        name: str,
    ):
        """
        Load existing character.
        """


        if not self.exists(name):

            raise FileNotFoundError(
                f"Character not found: {name}"
            )


        return self.storage.load(
            name
        )
    

    def generate_roleplay(
        self,
        character,
        text,
        instructions="",
        emotion="neutral",
    ):
        """
        Generate character speech.

        CharacterManager responsibilities:
        - load character assets
        - assemble generation request

        Qwen3Engine responsibilities:
        - perform inference
        """

        metadata = self.storage.load_metadata(
            character
        )

        prompt = self.storage.load_voice_prompt(
            character
        )

        return self.engine.generate_roleplay(
            text=text,
            prompt=prompt,
            metadata=metadata,
            instructions=instructions,
            emotion=emotion,
        )