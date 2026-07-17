import pytest
from pathlib import Path

from app.commands.create_character import (
    create_character_command
)



@pytest.mark.unit
def test_create_character_command_exists():

    assert callable(
        create_character_command
    )



@pytest.mark.unit
def test_missing_audio_file_fails():

    class Args:
        audio = "/does/not/exist.wav"
        name = "missing"
        output_dir = "/tmp/test-character"
        instructions = None


    with pytest.raises(
        FileNotFoundError
    ):

        create_character_command(
            Args()
        )