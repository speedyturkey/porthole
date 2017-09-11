# This script makes assumptions about the existing sections and option names
# in the associated config.ini file.  If the provided config.ini file is directly
# edited, then this file should be reviewed for breaking changes.
# For the relative filepaths to work, this script must be run from the outer porthole directory.


from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, SelectField
from wtforms.validators import InputRequired
from configparser import ConfigParser
from flask_bootstrap import Bootstrap
from .connections import ConnectionManager
# from . import gui_app

gui_app = Flask('porthole')
gui_app.config['SECRET_KEY'] = 'flarp'

#flask_bootstrap fills in some boilerplate in the template
Bootstrap(gui_app)

#ConfigParser helps with manipulating config files
parser = ConfigParser()
config_file = 'config/config.ini'


# This function takes a dictionary and updates the config file in the base directory.
# This function checks for specific keys and only updates when key exists and value is not an empty string.
def edit_config(dict):
    parser.read(config_file)
    if 'default_base_file_path' in dict and dict['default_base_file_path'] != '':
        parser.set('Default', 'base_file_path', dict['default_base_file_path'])
    if 'default_query_path' in dict and dict['default_query_path'] != '':
        parser.set('Default', 'query_path', dict['default_query_path'])
    if 'default_database' in dict and dict['default_database'] != '':
        parser.set('Default', 'database', dict['default_database'])
    if 'default_notification_recipient' in dict and dict['default_notification_recipient'] != '':
        parser.set('Default', 'notification_recipient', dict['default_notification_recipient'])
    if 'email_username' in dict and dict['email_username'] != '':
        parser.set('Email', 'username', dict['email_username'])
    if 'email_password' in dict and dict['email_password'] != '':
        parser.set('Email', 'password', dict['email_password'])
    if 'email_host' in dict and dict['email_host'] != '':
        parser.set('Email', 'host', dict['email_host'])
    if 'email_disabled' in dict and str(dict['email_disabled']) != '':
        parser.set('Email', 'disabled', str(dict['email_disabled']))
    if 'email_signature' in dict and dict['email_signature'] != '':
        parser.set('Email', 'signature', dict['email_signature'])
    if 'logging_server' in dict and dict['logging_server'] != '':
        parser.set('Logging', 'server', dict['logging_server'])
    if 'logging_to_file' in dict and dict['logging_to_file'] != '':
        parser.set('Logging', 'log_to_file', dict['logging_to_file'])
    if 'logging_file' in dict and dict['logging_file'] != '':
        parser.set('Logging', 'logfile', dict['logging_file'])
    if 'logging_db' in dict and dict['logging_db'] != '':
        parser.set('Logging', 'db', dict['logging_db'])
    if 'debug_mode' in dict and dict['debug_mode'] != '':
        parser.set('Debug', 'debug_mode', dict['debug_mode'])
    if 'debug_recipients' in dict and dict['debug_recipients'] != '':
        parser.set('Debug', 'debug_recipients', dict['debug_recipients'])
    if 'admin_email' in dict and dict['admin_email'] != '':
        parser.set('Admin', 'admin_email', dict['admin_email'])
    with open(config_file, 'w') as configfile:
        parser.write(configfile)

# This function takes a dictionary and updates the config file in the base directory.
# This function will add a new section to the config file if the provided section name (connection_name)
# is unique.  Otherwise it will update the section with the options provided.  If the section is new
# the connection_name will be appended to the connections option in the Default section (this assists
# in iteration over the connection sections).  Blank, extra, and missing options are ignored.
def add_connection(dict):
    parser.read(config_file)
    if 'connection_name' in dict and dict['connection_name'] != '':
        connection_name = dict['connection_name']
        connections = parser.get('Default', 'connections')
        if connection_name not in connections.split(", "):
            parser.add_section(connection_name)
            parser.set('Default', 'connections', connections + ', ' + connection_name)
    if 'rdbms' in dict and dict['rdbms'] != '':
        parser.set(connection_name, 'rdbms', dict['rdbms'])
    if 'connection_host' in dict and dict['connection_host'] != '':
        parser.set(connection_name, 'host', dict['connection_host'])
    if 'connection_port' in dict and dict['connection_port'] != '':
        parser.set(connection_name, 'port', dict['connection_port'])
    if 'connection_user' in dict and dict['connection_user'] != '':
        parser.set(connection_name, 'user', dict['connection_user'])
    if 'connection_password' in dict and dict['connection_password'] != '':
        parser.set(connection_name, 'password', dict['connection_password'])
    if 'schema' in dict and dict['schema'] != '':
        parser.set(connection_name, 'schema', dict['schema'])
    with open(config_file, 'w') as configfile:
        parser.write(configfile)

# This function takes a string and updates the config file in the base directory.
# If a section name matches the provided string, then that section and all its options are removed.
# It is removed from the connections option in the Default section, if present.
def delete_connection(connection_name):
    print(connection_name)
    parser.read(config_file)
    connections = parser.get('Default', 'connections')
    connections_list = connections.split(", ")
    if connection_name in connections_list:
        parser.remove_section(connection_name)
        connections_list.remove(connection_name)
        parser.set('Default', 'connections',', '.join(connections_list))
    with open(config_file, 'w') as configfile:
        parser.write(configfile)

# This function takes no arguments and returns a dictionary of dictionaries.
# The outer dictionary has each section in the config file as keys. The inner dictionary
# (i.e. the values of the outer dictionary keys) contains a dictionary where the option names
# are the keys, and the option values are the values.
# e.g. to get the query_path in the Default section: all_config_options['Default']['query_path']
def read_config():
    parser.read(config_file)
    all_config_options = {}
    sections = parser.sections()
    for section in sections:
        all_config_options.update({section : {}})
        options = parser.options(section)
        for option in options:
            all_config_options[section].update({option : parser.get(section, option)})
    return all_config_options

# This class defines the form used to add and edit connection sections to the config file.
class ConnectionForm(FlaskForm):
    connection_name = StringField('connection_name')
    rdbms = StringField('rdbms')
    connection_host = StringField('connection_host')
    connection_port = StringField('connection_port')
    connection_user = StringField('connection_user')
    connection_password = StringField('connection_password')
    schema = StringField('schema')
    delete_connection = StringField('Delete?')
    connection_submit = SubmitField('Save Connection')

# This class defines the form used to edit config sections other than connections.
class ConfigForm(FlaskForm):
    default_base_file_path = StringField('default_base_file_path')#, validators=[InputRequired()])
    default_query_path = StringField('default_query_path')
    default_database = SelectField('default_database')
    default_notification_recipient = StringField('default_notification_recipient')
    email_username = StringField('email_username')
    email_password = PasswordField('email_password')
    email_host = StringField('email_host')
    email_disabled = RadioField('email_disabled', choices=[('True','True'),('False','False')])
    email_signature = StringField('email_signature')
    logging_server = SelectField('logging_server')
    logging_to_file = RadioField('Log to File', choices=[('True', 'True'),('False', 'False')])
    logging_file = StringField('Log File Name')
    logging_db = StringField('logging_db')
    debug_mode = RadioField('debug_mode', choices=[('True', 'True'),('False', 'False')])
    debug_recipients = StringField('debug_recipients')
    admin_email = StringField('admin_email')
    config_submit = SubmitField('Save Settings')

# This is the endpoint for displaying and editing the application settings.
# All of the config sections and options are passed to the front end, along with options for
# select inputs in the rendered form.
# This endpoint renders two forms.  If either form is submitted and validated, it will update
# the config file and refresh the page showing the updated values.
@gui_app.route('/config', methods=['GET', 'POST'])
def config():
    all_config_options=read_config()
    connections = all_config_options["Default"]["connections"].split(", ")
    config_form = ConfigForm()
    connection_form = ConnectionForm()
    connection_choices = [(c,c) for c in connections]
    connection_choice_additions = [('None Selected','None Selected')]
    print(connection_choices + connection_choice_additions)
    config_form.default_database.choices = connection_choices + connection_choice_additions
    config_form.logging_server.choices = connection_choices + connection_choice_additions
    rdbms_options = ['MySQL', 'SQLite']
    rdbms_choices = [(i,i) for i in rdbms_options]
    connection_form.rdbms.choices = rdbms_choices

    if config_form.config_submit.data and config_form.validate():
        edit_config(config_form.data)
        flash('Settings Updated')
        all_config_options=read_config()
        connections = all_config_options["Default"]["connections"].split(", ")
        print(config_form.data)
        return render_template("settings.html", config_form=config_form
                                            , connection_form=connection_form
                                            , all_config_options=all_config_options
                                            , connections=connections
                                            , rdbms_options=rdbms_options)

    if connection_form.connection_submit.data and connection_form.validate():
        if connection_form.data['delete_connection'] == 'True':
            delete_connection(connection_form.data['connection_name'])
        else:
            add_connection(connection_form.data)
        print(connection_form.data)
        all_config_options=read_config()
        connections = all_config_options["Default"]["connections"].split(", ")
        return render_template("settings.html", config_form=config_form
                                            , connection_form=connection_form
                                            , all_config_options=all_config_options
                                            , connections=connections
                                            , rdbms_options=rdbms_options)

    return render_template("settings.html", config_form=config_form
                                        , connection_form=connection_form
                                        , all_config_options=all_config_options
                                        , connections=connections
                                        , rdbms_options=rdbms_options)

@gui_app.route('/api/test_connection/<connection_name>', methods=['GET', 'POST'])
def test_connection(connection_name):
    conn = ConnectionManager(db = connection_name)
    try:
        conn.connect()
        conn.close()
        return 'Connected Successfully'
    except:
        return 'Failed to Connect'


if __name__ == '__main__':
    gui_app.run(debug=False)
