from pathlib import Path
from types import SimpleNamespace

import numpy as np

from app.commands.roleplay import roleplay_command
from app.core.characters.models import Character


# ---------------------------------------------------------------------------
# Fake Manager
# ---------------------------------------------------------------------------

class FakeManager:

    def __init__(self, character):

        self.character = character

        self.calls = []


    def get(
        self,
        name,
    ):

        return self.character


    def generate_roleplay(
        self,
        *,
        character,
        text,
        instructions=None,
        emotion=None,
    ):

        self.calls.append(
            {
                "character": character,
                "text": text,
                "instructions": instructions,
                "emotion": emotion,
            }
        )


        # fake 1 second audio buffer
        audio = np.zeros(
            16000,
            dtype=np.float32,
        )


        return (
            audio,
            16000,
        )



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_args(
    **kwargs,
):

    defaults = {

        "character": "louise",

        "script": "Hello there",

        "script_file": None,

        "instructions": None,

        "emotion": "neutral",

        "output": None,
    }


    defaults.update(
        kwargs
    )


    return SimpleNamespace(
        **defaults
    )



def create_character(
    tmp_path,
):

    return Character(

        name="louise",

        directory=tmp_path / "louise",
    )



# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_roleplay_generates_audio(
    tmp_path,
):

    character = create_character(
        tmp_path
    )


    manager = FakeManager(
        character
    )


    output = (
        tmp_path / "test.wav"
    )


    args = make_args(
        output=str(output)
    )


    roleplay_command(
        args,
        manager_factory=lambda: manager,
    )


    assert output.exists()


    assert len(
        manager.calls
    ) == 1



    call = manager.calls[0]


    assert call["character"] == character

    assert call["text"] == (
        "Hello there"
    )



def test_roleplay_passes_instructions_and_emotion(
    tmp_path,
):

    character = create_character(
        tmp_path
    )


    manager = FakeManager(
        character
    )


    args = make_args(

        instructions=(
            "Speak angrily"
        ),

        emotion="rage",

        output=str(
            tmp_path / "voice.wav"
        ),
    )


    roleplay_command(
        args,
        manager_factory=lambda: manager,
    )


    call = manager.calls[0]


    assert call["instructions"] == (
        "Speak angrily"
    )


    assert call["emotion"] == (
        "rage"
    )



def test_roleplay_reads_script_file(
    tmp_path,
):

    script_file = (
        tmp_path / "script.txt"
    )


    script_file.write_text(
        "A secret message"
    )



    character = create_character(
        tmp_path
    )


    manager = FakeManager(
        character
    )


    args = make_args(

        script=None,

        script_file=str(
            script_file
        ),

        output=str(
            tmp_path / "voice.wav"
        ),
    )


    roleplay_command(
        args,
        manager_factory=lambda: manager,
    )


    call = manager.calls[0]


    assert call["text"] == (
        "A secret message"
    )



def test_roleplay_requires_script(
    tmp_path,
):

    character = create_character(
        tmp_path
    )


    manager = FakeManager(
        character
    )


    args = make_args(
        script=None,
    )


    try:

        roleplay_command(
            args,
            manager_factory=lambda: manager,
        )


        assert False, (
            "Expected ValueError"
        )


    except ValueError as e:

        assert (
            "Provide --script"
            in str(e)
        )