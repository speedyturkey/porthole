import os
from configparser import ConfigParser
from collections import OrderedDict
from .app import config
from .connections import ConnectionManager
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

Email = OrderedDict([('username', NONE),
                        ('password', NONE),
                        ('host', NONE),
                        ('disabled', "FALSE"),
                        ('signature', NONE)])

Logging = OrderedDict([('server', "FALSE"),
                        ('log_to_file', "FALSE"),
                        ('logfile', NONE),
                        ('logging_db', NONE)])

Debug = OrderedDict([('debug_mode', "FALSE"),
                        ('debug_recipients', NONE)])

Admin = OrderedDict([('admin_email', NONE)])

def new_config():
    "Writes a blank config file. Use during new project setup or reference example.ini."
    parser = ConfigParser()

    parser['Default'] = Default
    parser['ConnectionName'] = ConnectionName
    parser['Email'] = Email
    parser['Logging'] = Logging
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
    "Executes table creation statements for core tables in user-defined default database."
    db = config['Default']['database']
    try:
        cm = ConnectionManager(db)
        cm.connect()
        metadata.create_all(cm.engine)
        print("Tables successfully created.")
    except Exception as e:
        print("Failed to create tables. Encountered the following error(s): {}.".format(e))
