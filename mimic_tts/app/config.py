"""
Application configuration manager.

Responsibilities:
- Load default.ini
- Provide typed accessors
- Hide ConfigParser usage from the rest of the application

Other modules should use:
    settings.some_property

instead of:
    settings.get("section", "key")
"""


from configparser import ConfigParser
from pathlib import Path
import os


class Settings:
    """
    Global application settings.

    Reads configuration once during startup.
    """


    def __init__(self):

        config_path = os.getenv(
            "MIMIC_CONFIG",
            "/app/config/default.ini"
        )

        self.path = Path(config_path)


        if not self.path.exists():

            raise FileNotFoundError(
                f"Config file missing: {self.path}"
            )


        self.config = ConfigParser()

        self.config.read(
            self.path
        )


        print(
            f"Loaded configuration: {self.path}"
        )


    ############################################################
    #
    # Raw access helpers
    #
    ############################################################


    def get(
        self,
        section: str,
        key: str,
    ):
        """
        Retrieve a string configuration value.
        """

        return self.config[section][key]


    def get_int(
        self,
        section: str,
        key: str,
    ):
        """
        Retrieve an integer configuration value.
        """

        return self.config.getint(
            section,
            key,
        )


    def get_float(
        self,
        section: str,
        key: str,
    ):
        """
        Retrieve a float configuration value.
        """

        return self.config.getfloat(
            section,
            key,
        )


    def get_bool(
        self,
        section: str,
        key: str,
    ):
        """
        Retrieve a boolean configuration value.
        """

        return self.config.getboolean(
            section,
            key,
        )


    ############################################################
    #
    # Model paths
    #
    ############################################################


    @property
    def default_model(self) -> str:
        """
        Returns the default Qwen model type.

        Example:
            clone
            custom
            design
        """

        return self.get(
            "models",
            "default",
        )


    @property
    def clone_model_path(self) -> Path:
        """
        Qwen Base model.

        Used for:
        - voice cloning
        - character creation
        - cloned roleplay voices
        """

        return Path(
            self.get(
                "models",
                "clone_path",
            )
        )


    @property
    def custom_model_path(self) -> Path:
        """
        Qwen CustomVoice model.

        Used for:
        - built-in speakers
        - speaker + instruction generation
        """

        return Path(
            self.get(
                "models",
                "custom_path",
            )
        )


    @property
    def design_model_path(self) -> Path:
        """
        Qwen VoiceDesign model.

        Used for:
        - creating new voices
        - experimental voice generation
        """

        return Path(
            self.get(
                "models",
                "design_path",
            )
        )


    ############################################################
    #
    # Runtime
    #
    ############################################################


    @property
    def device(self) -> str:
        """
        Compute device.

        Usually:
            cuda
            cpu
        """

        return self.get(
            "runtime",
            "device",
        )


    @property
    def dtype(self):
        """
        Torch precision mode.

        Example:
            bfloat16
            float16
            float32
        """

        return self.get(
            "runtime",
            "dtype",
        )


    ############################################################
    #
    # Application paths
    #
    ############################################################


    @property
    def characters_dir(self) -> Path:
        """
        Root directory containing character profiles.
        """

        return Path(
            self.get(
                "paths",
                "characters",
            )
        )


    @property
    def input_directory(self) -> Path:
        """
        Input audio directory.
        """

        return Path(
            self.get(
                "paths",
                "input",
            )
        )


    @property
    def output_directory(self) -> Path:
        """
        Generated audio output directory.
        """

        return Path(
            self.get(
                "paths",
                "output",
            )
        )


    ############################################################
    #
    # Transcription
    #
    ############################################################
    @property
    def transcription_model(self) -> str:
        """
        Whisper model name.
        Example:
            large-v3
        """
        return self.get(
            "transcription",
            "model",
        )


    @property
    def transcription_device(self) -> str:
        """
        Device used by Whisper.
        Example:
            cuda
            cpu
        """
        return self.get(
            "transcription",
            "device",
        )


    @property
    def transcription_compute_type(self) -> str:
        """
        Whisper precision mode.

        Examples:
            float16
            int8
        """
        return self.get(
            "transcription",
            "compute_type",
        )


    @property
    def transcription_language(self) -> str:
        """
        Default transcription language.
        """
        return self.get(
            "transcription",
            "language",
        )

    ############################################################
    #
    # Audio
    #
    ############################################################


    @property
    def sample_rate(self) -> int:
        """
        Output audio sample rate.
        """

        return self.get_int(
            "audio",
            "sample_rate",
        )


    @property
    def output_format(self) -> str:
        """
        Output audio format.
        """

        return self.get(
            "audio",
            "output_format",
        )


settings = Settings()