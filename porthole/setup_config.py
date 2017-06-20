from pathlib import Path
from configparser import ConfigParser
from collections import OrderedDict

NONE = ""
configfile = 'config.ini'

Default =  OrderedDict([('base_file_path', NONE),
                        ('query_path', NONE),
                        ('database', NONE),
                        ('notification_recipient', NONE)])

ConnectionName = OrderedDict([('rdbms', NONE),
                            ('host', NONE),
                            ('port', 0),
                            ('user', NONE),
                            ('password', NONE),
                            ('schema', NONE)])

Exchange = OrderedDict([('exchange_user', NONE),
                        ('exchange_password', NONE),
                        ('host', NONE)])

Logging = OrderedDict([('server', "FALSE"),
                        ('logging_db', NONE)])

Email = OrderedDict([('disabled', "FALSE"),
                        ('signature', NONE)])

Debug = OrderedDict([('debug_mode', "FALSE"),
                        ('debug_email', NONE)])

Admin = OrderedDict([('admin_email', NONE)])

def write_default_config():
    parser = ConfigParser()

    parser['Default'] = Default
    parser['ConnectionName'] = ConnectionName
    parser['Exchange'] = Exchange
    parser['Logging'] = Logging
    parser['Email'] = Email
    parser['Debug'] = Debug
    parser['Admin'] = Admin

    config_path = Path(configfile)
    if config_path.is_file():
        print("Config template already exists.")
    else:
        with open (configfile, 'w') as f:
            parser.write(f)
        print("New config template written as {}.".format(configfile))
