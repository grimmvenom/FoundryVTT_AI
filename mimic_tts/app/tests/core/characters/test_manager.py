from pathlib import Path

from app.core.characters.manager import CharacterManager
from app.core.characters.storage import CharacterStorage
from app.core.characters.models import RoleplayRequest



###########################################################################
#
# Fake Speech-To-Text
#
###########################################################################


class FakeSpeechToText:

    def __init__(
        self,
        transcript="hello there",
    ):
        self.transcript = transcript
        self.calls = []


    def transcribe(
        self,
        audio,
    ):
        self.calls.append(
            audio
        )

        return self.transcript



###########################################################################
#
# Fake Qwen Engine
#
###########################################################################


class FakeQwen:

    def __init__(self):

        self.loaded = False

        self.calls = []



    def load(self):

        self.loaded = True



    def create_voice_clone_prompt(
        self,
        audio_path,
        transcript,
    ):

        self.calls.append(
            (
                "prompt",
                audio_path,
                transcript,
            )
        )


        return [
            "fake prompt"
        ]



    def generate_roleplay(
        self,
        text,
        prompt,
        metadata,
        instructions="",
        emotion="neutral",
    ):

        self.calls.append(
            (
                "roleplay",
                text,
                prompt,
                metadata,
                instructions,
                emotion,
            )
        )


        return (
            b"fake audio",
            24000,
        )



###########################################################################
#
# Helper
#
###########################################################################


def create_manager(
    tmp_path,
    transcript="hello there",
):

    stt = FakeSpeechToText(
        transcript
    )

    qwen = FakeQwen()


    manager = CharacterManager(
        storage=CharacterStorage(
            tmp_path
        ),
        speech_to_text=stt,
        engine=qwen,
    )


    return (
        manager,
        stt,
        qwen,
    )



###########################################################################
#
# Character Creation
#
###########################################################################


def test_create_character_success(
    tmp_path,
):

    manager, stt, qwen = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )



    assert result.character.name == "louise"

    assert result.transcript == (
        "hello there"
    )


    assert qwen.loaded is True


    assert len(qwen.calls) == 1

    assert qwen.calls[0][0] == (
        "prompt"
    )



def test_create_character_calls_transcriber(
    tmp_path,
):

    manager, stt, _ = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    manager.create_character(
        name="louise",
        audio_path=audio,
    )



    assert stt.calls == [
        audio
    ]



def test_create_character_saves_transcript(
    tmp_path,
):

    manager, _, _ = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )



    transcript = (
        manager.storage.load_transcript(
            result.character
        )
    )


    assert transcript == (
        "hello there"
    )



def test_create_character_saves_metadata(
    tmp_path,
):

    manager, _, _ = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    result = manager.create_character(
        name="louise",
        audio_path=audio,
        instructions="Energetic child voice",
    )



    metadata = (
        manager.storage.load_metadata(
            result.character
        )
    )



    assert metadata.name == "louise"

    assert metadata.source_audio == str(
        audio
    )

    assert metadata.instructions == (
        "Energetic child voice"
    )



def test_create_character_saves_voice_prompt(
    tmp_path,
):

    manager, _, _ = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )



    prompt = (
        manager.storage.load_voice_prompt(
            result.character
        )
    )


    assert prompt == [
        "fake prompt"
    ]



    assert result.character.prompt_path.exists()



def test_engine_receives_prompt_parameters(
    tmp_path,
):

    manager, _, qwen = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    manager.create_character(
        name="louise",
        audio_path=audio,
    )



    call = qwen.calls[0]



    assert call[0] == (
        "prompt"
    )


    assert call[1] == audio


    assert call[2] == (
        "hello there"
    )



###########################################################################
#
# Roleplay
#
###########################################################################


def test_generate_roleplay(
    tmp_path,
):

    manager, _, qwen = create_manager(
        tmp_path
    )


    audio = tmp_path / "voice.wav"

    audio.touch()



    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )



    request = RoleplayRequest(

        character=result.character,

        text="Hello, I am Louise!",

        instructions="Goofy and energetic",

        emotion="excited",
    )



    audio_data, sample_rate = (
        manager.generate_roleplay(
            request
        )
    )



    assert audio_data == (
        b"fake audio"
    )


    assert sample_rate == 24000



    call = qwen.calls[-1]



    assert call[0] == (
        "roleplay"
    )


    assert call[1] == (
        "Hello, I am Louise!"
    )


    assert call[4] == (
        "Goofy and energetic"
    )


    assert call[5] == (
        "excited"
    )