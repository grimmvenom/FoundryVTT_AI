from app.core.characters.manager import CharacterManager
from app.core.characters.storage import CharacterStorage


class FakeSpeechToText:

    def __init__(self, transcript="hello there"):
        self.transcript = transcript
        self.calls = []

    def transcribe(self, audio):
        self.calls.append(audio)
        return self.transcript


class FakeQwen:

    def __init__(self):
        self.loaded = False
        self.calls = []

    def load(self):
        self.loaded = True

    def create_character(
        self,
        audio_path,
        transcript,
        output_path,
        instructions=None,
    ):

        self.calls.append(
            {
                "audio_path": audio_path,
                "transcript": transcript,
                "output_path": output_path,
                "instructions": instructions,
            }
        )

        output_path.write_text(
            "fake qvp"
        )


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

    return manager, stt, qwen


def test_create_character_success(tmp_path):

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
    assert result.transcript == "hello there"

    assert qwen.loaded is True
    assert len(qwen.calls) == 1


def test_create_character_saves_transcript(tmp_path):

    manager, _, _ = create_manager(
        tmp_path
    )

    audio = tmp_path / "voice.wav"
    audio.touch()

    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )

    assert (
        manager.storage.load_transcript(
            result.character
        )
        == "hello there"
    )


def test_create_character_saves_metadata(tmp_path):

    manager, _, _ = create_manager(
        tmp_path
    )

    audio = tmp_path / "voice.wav"
    audio.touch()

    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )

    metadata = (
        manager.storage.load_metadata(
            result.character
        )
    )

    assert metadata.source_audio == str(audio)
    assert metadata.personality == ""
    assert metadata.description == ""


def test_engine_receives_parameters(tmp_path):

    manager, _, qwen = create_manager(
        tmp_path
    )

    audio = tmp_path / "voice.wav"
    audio.touch()

    manager.create_character(
        name="louise",
        audio_path=audio,
        instructions="Whispery child voice",
    )

    call = qwen.calls[0]

    assert call["audio_path"] == audio
    assert call["transcript"] == "hello there"
    assert call["instructions"] == "Whispery child voice"


def test_create_character_creates_voice_profile(tmp_path):

    manager, _, _ = create_manager(
        tmp_path
    )

    audio = tmp_path / "voice.wav"
    audio.touch()

    result = manager.create_character(
        name="louise",
        audio_path=audio,
    )

    assert result.character.voice_path.exists()
    assert result.character.voice_path.name == "voice.qvp"