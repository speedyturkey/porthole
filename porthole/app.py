import os
from configparser import ConfigParser


class PortholeConfig(ConfigParser):
    CONFIG_ENV_NAME = 'PORTHOLE_CONFIG'
    DEFAULT_CONFIG_FILE = 'porthole.ini'
    DEFAULT_CONFIG_DIRECTORY = 'config'
    OTHER_ALLOWED_CONFIG_PATHS = [
        os.path.join(DEFAULT_CONFIG_DIRECTORY, 'porthole.ini'),
        os.path.join(DEFAULT_CONFIG_DIRECTORY, 'config.ini')
    ]

    def __init__(self) -> None:
        super().__init__(os.environ, interpolation=None)
        config_file = self.determine_config()
        self.read(config_file)

    @staticmethod
    def determine_config() -> str:
        """
        Porthole needs to identify which config file should be used. A cascading approach is utilized that is flexible
        but has simple default options. Either set the environment variable PORTHOLE_CONFIG,
        or review the PortholeConfig docstrings.
        """
        if os.environ.get(PortholeConfig.CONFIG_ENV_NAME) is not None:
            return os.environ.get(PortholeConfig.CONFIG_ENV_NAME)
        if os.path.isfile(PortholeConfig.DEFAULT_CONFIG_FILE):
            return PortholeConfig.DEFAULT_CONFIG_FILE
        for file_path in PortholeConfig.OTHER_ALLOWED_CONFIG_PATHS:
            if os.path.isfile(file_path):
                return file_path
        raise FileNotFoundError(
            "Porthole is unable to locate a useable config file. "
            "Try setting the PORTHOLE_CONFIG environment variable, "
            "or creating a porthole.ini file in your main project directory."
        )


config = PortholeConfig()

if __name__ == '__main__':
    pass
