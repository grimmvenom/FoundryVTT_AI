from configparser import ConfigParser
from pathlib import Path
import os


class Settings:

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
        self.config.read(self.path)

        print(f"Loaded configuration: {self.path}")


    def get(self, section, key):
        return self.config[section][key]


    def get_int(self, section, key):
        return self.config.getint(section, key)


    def get_float(self, section, key):
        return self.config.getfloat(section, key)


    # Convenience properties
    # These prevent every other module from knowing config sections


    @property
    def model_path(self):
        return Path(
            self.get("model", "path")
        )


    @property
    def voice_directory(self):
        return Path(
            self.get("voice_clone", "profile_directory")
        )


    @property
    def input_directory(self):
        return Path(
            self.get("paths", "input")
        )


    @property
    def output_directory(self):
        return Path(
            self.get("paths", "output")
        )


    @property
    def sample_rate(self):
        return self.get_int(
            "audio",
            "sample_rate"
        )


settings = Settings()