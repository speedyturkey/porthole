import os
from configparser import ConfigParser
from collections import OrderedDict
from .app import config
from .connection_manager import ConnectionManager
from .models import metadata


NONE = ""
configdir = 'config'
configfile = 'config.ini'
configpath = os.path.join(configdir, configfile)

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

def new_config():
    parser = ConfigParser()

    parser['Default'] = Default
    parser['ConnectionName'] = ConnectionName
    parser['Exchange'] = Exchange
    parser['Logging'] = Logging
    parser['Email'] = Email
    parser['Debug'] = Debug
    parser['Admin'] = Admin

    if not os.path.exists(configdir):
        os.makedirs(configdir)
        print("Created directory {}.".format(configdir))

    if not os.path.exists(configpath):
        with open (configpath, 'w') as f:
            parser.write(f)
        print("Created blank template {}.".format(configpath))

def setup_tables():
    db = config['Default']['database']
    try:
        cm = ConnectionManager(db)
        cm.connect()
        metadata.create_all(cm.engine)
        print("Tables successfully created.")
    except:
        print("Failed to create tables.")
