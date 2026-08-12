import io
import json
import wave

import numpy as np
import torch

from .client import MimicTTSClient


############################################################
#
# List Characters
#
############################################################

class MimicTTSListCharacters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_url": (
                    "STRING",
                    {
                        "default": "http://mimic-tts:8000",
                        "multiline": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("characters",)

    FUNCTION = "list_characters"
    CATEGORY = "mimic_tts"

    def list_characters(
        self,
        tts_url,
    ):
        client = MimicTTSClient(tts_url)

        characters = client.list_characters()

        return (
            json.dumps(
                characters,
                indent=2,
                ensure_ascii=False,
            ),
        )


############################################################
#
# Create Character
#
############################################################

class MimicTTSCreateCharacter:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_url": (
                    "STRING",
                    {
                        "default": "http://mimic-tts:8000",
                        "multiline": False,
                    },
                ),
                "character_name": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "audio": ("AUDIO",),
                "instructions": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "personality": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "overwrite": (
                    "BOOLEAN",
                    {
                        "default": False,
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status", "transcript")

    FUNCTION = "create_character"
    CATEGORY = "mimic_tts"

    def create_character(
        self,
        tts_url,
        character_name,
        audio,
        instructions,
        personality,
        description,
        overwrite,
    ):
        if not character_name.strip():
            raise ValueError(
                "Character name cannot be empty."
            )

        if audio is None:
            raise ValueError(
                "Audio input is required."
            )

        wav_bytes = self._audio_to_wav(audio)

        client = MimicTTSClient(tts_url)

        result = client.create_character(
            name=character_name.strip(),
            audio=wav_bytes,
            instructions=instructions or "",
            personality=personality or "",
            description=description or "",
            overwrite=overwrite,
        )

        print(
            "Mimic TTS create_character response:"
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        transcript = result.get(
            "transcript",
            "",
        )

        status = result.get(
            "status",
            "Character created successfully.",
        )

        return (
            status,
            transcript,
        )

    @staticmethod
    def _audio_to_wav(audio) -> bytes:

        if not isinstance(
            audio,
            dict,
        ):
            raise ValueError(
                "AUDIO input is not a valid "
                "ComfyUI AUDIO object."
            )

        waveform = audio.get(
            "waveform"
        )

        if waveform is None:
            raise ValueError(
                "AUDIO input does not contain "
                "a waveform."
            )

        sample_rate = audio.get(
            "sample_rate"
        )

        if sample_rate is None:
            raise ValueError(
                "AUDIO input does not contain "
                "a sample rate."
            )

        #
        # ComfyUI normally supplies a torch.Tensor.
        # However, accept numpy arrays as well.
        #

        if hasattr(
            waveform,
            "detach",
        ):
            waveform = waveform.detach()

        if hasattr(
            waveform,
            "cpu",
        ):
            waveform = waveform.cpu()

        if hasattr(
            waveform,
            "numpy",
        ):
            waveform = waveform.numpy()

        waveform = np.asarray(
            waveform
        )

        #
        # Expected:
        #
        # [batch, channels, samples]
        #
        # or
        #
        # [channels, samples]
        #

        if waveform.ndim == 3:

            if waveform.shape[0] < 1:
                raise ValueError(
                    "AUDIO waveform contains "
                    "no batch items."
                )

            waveform = waveform[0]

        if waveform.ndim == 1:

            waveform = waveform[
                np.newaxis,
                :
            ]

        if waveform.ndim != 2:
            raise ValueError(
                "Unsupported AUDIO waveform "
                f"shape: {waveform.shape}. "
                "Expected [channels, samples] "
                "or [batch, channels, samples]."
            )

        #
        # Convert:
        #
        # [channels, samples]
        #
        # to:
        #
        # [samples, channels]
        #

        waveform = waveform.T

        waveform = waveform.astype(
            np.float32,
            copy=False,
        )

        waveform = np.clip(
            waveform,
            -1.0,
            1.0,
        )

        #
        # Convert float32 [-1, 1] to
        # signed 16-bit PCM.
        #

        pcm = (
            waveform * 32767.0
        ).astype(
            np.int16
        )

        buffer = io.BytesIO()

        with wave.open(
            buffer,
            "wb",
        ) as wav:

            wav.setnchannels(
                pcm.shape[1]
            )

            wav.setsampwidth(
                2
            )

            wav.setframerate(
                int(sample_rate)
            )

            wav.writeframes(
                pcm.tobytes()
            )

        return buffer.getvalue()


############################################################
#
# Update Character
#
############################################################

class MimicTTSUpdateCharacter:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_url": (
                    "STRING",
                    {
                        "default": "http://mimic-tts:8000",
                        "multiline": False,
                    },
                ),
                "character_name": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "instructions": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "personality": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "description": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            },
            "optional": {
                "audio": ("AUDIO",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)

    FUNCTION = "update_character"
    CATEGORY = "mimic_tts"

    def update_character(
        self,
        tts_url,
        character_name,
        instructions,
        personality,
        description,
        audio=None,
    ):
        if not character_name.strip():
            raise ValueError(
                "Character name cannot be empty."
            )

        wav_bytes = None

        if audio is not None:
            wav_bytes = (
                MimicTTSCreateCharacter
                ._audio_to_wav(audio)
            )

        client = MimicTTSClient(tts_url)

        result = client.update_character(
            name=character_name.strip(),
            audio=wav_bytes,
            instructions=instructions,
            personality=personality,
            description=description,
        )

        print(
            "Mimic TTS update_character response:"
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        status = result.get(
            "status",
            "Character updated successfully.",
        )

        return (
            status,
        )


############################################################
#
# Roleplay
#
############################################################

class MimicTTSRoleplay:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tts_url": (
                    "STRING",
                    {
                        "default": "http://mimic-tts:8000",
                        "multiline": False,
                    },
                ),
                "character": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "emotion": (
                    "STRING",
                    {
                        "default": "neutral",
                        "multiline": False,
                    },
                ),
                "instructions": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "AUDIO",
        "STRING",
    )

    RETURN_NAMES = (
        "audio",
        "response",
    )

    FUNCTION = "roleplay"
    CATEGORY = "mimic_tts"

    def roleplay(
        self,
        tts_url,
        character,
        text,
        emotion,
        instructions,
    ):
        character = character.strip()

        if not character:
            raise ValueError(
                "Character name cannot be empty."
            )

        if not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        client = MimicTTSClient(
            tts_url
        )

        #
        # The API returns raw audio/wav bytes.
        #

        audio_bytes = client.roleplay(
            character=character,
            text=text,
            instructions=instructions or "",
            emotion=emotion or "neutral",
        )

        if not audio_bytes:
            raise RuntimeError(
                "Roleplay API returned empty "
                "audio data."
            )

        print(
            f"Mimic TTS roleplay generated "
            f"{len(audio_bytes)} bytes of WAV audio."
        )

        #
        # Decode WAV.
        #

        try:

            with wave.open(
                io.BytesIO(audio_bytes),
                "rb",
            ) as wav:

                channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                sample_rate = wav.getframerate()
                frame_count = wav.getnframes()

                frames = wav.readframes(
                    frame_count
                )

        except wave.Error as exc:

            raise RuntimeError(
                "Roleplay API returned data that "
                "is not a valid WAV file."
            ) from exc

        #
        # Decode PCM.
        #

        if sample_width == 1:

            #
            # 8-bit WAV is unsigned PCM.
            #

            pcm = np.frombuffer(
                frames,
                dtype=np.uint8,
            )

            waveform = (
                pcm.astype(np.float32)
                - 128.0
            ) / 128.0

        elif sample_width == 2:

            pcm = np.frombuffer(
                frames,
                dtype=np.int16,
            )

            waveform = (
                pcm.astype(np.float32)
                / 32768.0
            )

        elif sample_width == 3:

            #
            # 24-bit PCM.
            #

            raw = np.frombuffer(
                frames,
                dtype=np.uint8,
            )

            if len(raw) % 3 != 0:
                raise RuntimeError(
                    "Invalid 24-bit WAV data."
                )

            raw = raw.reshape(
                -1,
                3,
            )

            pcm = (
                raw[:, 0].astype(np.int32)
                | (
                    raw[:, 1].astype(np.int32)
                    << 8
                )
                | (
                    raw[:, 2].astype(np.int32)
                    << 16
                )
            )

            #
            # Sign extend 24-bit values.
            #

            negative = (
                pcm & 0x800000
            ) != 0

            pcm[negative] -= 0x1000000

            waveform = (
                pcm.astype(np.float32)
                / 8388608.0
            )

        elif sample_width == 4:

            pcm = np.frombuffer(
                frames,
                dtype=np.int32,
            )

            waveform = (
                pcm.astype(np.float32)
                / 2147483648.0
            )

        else:

            raise RuntimeError(
                "Unsupported WAV sample width: "
                f"{sample_width} bytes."
            )

        #
        # Convert interleaved multi-channel audio:
        #
        # [samples * channels]
        #
        # into:
        #
        # [channels, samples]
        #

        if channels > 1:

            waveform = waveform.reshape(
                -1,
                channels,
            ).T

        else:

            waveform = waveform[
                np.newaxis,
                :
            ]

        #
        # Make sure values are valid.
        #

        waveform = np.clip(
            waveform,
            -1.0,
            1.0,
        )

        #
        # IMPORTANT:
        #
        # ComfyUI AUDIO requires a torch.Tensor.
        #
        # Shape:
        #
        # [batch, channels, samples]
        #
        # NOT a numpy.ndarray.
        #

        waveform = torch.from_numpy(
            waveform.copy()
        ).float()

        waveform = waveform.unsqueeze(
            0
        )

        #
        # Human-readable response.
        #

        response_text = (
            f"Generated roleplay audio for "
            f"'{character}' "
            f"({frame_count:,} frames, "
            f"{sample_rate} Hz)."
        )

        print(
            response_text
        )

        return (
            {
                "waveform": waveform,
                "sample_rate": sample_rate,
            },
            response_text,
        )


############################################################
#
# Node Mappings
#
############################################################

NODE_CLASS_MAPPINGS = {
    "MimicTTSListCharacters":
        MimicTTSListCharacters,

    "MimicTTSCreateCharacter":
        MimicTTSCreateCharacter,

    "MimicTTSUpdateCharacter":
        MimicTTSUpdateCharacter,

    "MimicTTSRoleplay":
        MimicTTSRoleplay,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "MimicTTSListCharacters":
        "Mimic TTS - List Characters",

    "MimicTTSCreateCharacter":
        "Mimic TTS - Create Character",

    "MimicTTSUpdateCharacter":
        "Mimic TTS - Update Character",

    "MimicTTSRoleplay":
        "Mimic TTS - Roleplay",
}