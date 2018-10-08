import os
from configparser import ConfigParser

config_file = 'config/config.ini'
config = ConfigParser(os.environ, interpolation=None)
config.read(config_file)


if __name__ == '__main__':
    pass
