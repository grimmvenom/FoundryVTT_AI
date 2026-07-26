"""
Audio helper utilities.
"""

from datetime import datetime
from pathlib import Path


def default_roleplay_filename(
    character_name: str,
) -> Path:
    """
    Generate default roleplay output filename.

    Format:
        <character_name>_%MM-%DD-%YY.wav

    Example:
        louise_07-18-26.wav
    """

    date = datetime.now().strftime(
        "%m-%d-%y"
    )

    return Path(
        f"{character_name}_{date}.wav"
    )