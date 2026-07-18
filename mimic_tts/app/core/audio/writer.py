from pathlib import Path

import soundfile as sf


def write_wav(
    output_path: Path,
    audio,
    sample_rate: int,
):
    """
    Save generated audio to wav.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sf.write(
        output_path,
        audio,
        sample_rate,
    )

    return output_path