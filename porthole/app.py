import os
from configparser import SafeConfigParser

config_file = 'config/config.ini'
config = SafeConfigParser(os.environ)
config.read(config_file)


if __name__ == '__main__':
    pass
