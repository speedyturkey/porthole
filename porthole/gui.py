# This script makes assumptions about the existing sections and option names
# in the associated config.ini file.  If the provided config.ini file is directly
# edited, then this file should be reviewed for breaking changes.
# For the relative filepaths to work, this script must be run from the outer porthole directory.


from flask import Flask, render_template, flash, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, SelectField
from wtforms.validators import InputRequired
from configparser import ConfigParser
from flask_bootstrap import Bootstrap
from .connections import ConnectionManager
from .queries import QueryReader, QueryGenerator
import os


gui_app = Flask(__name__)
gui_app.config['SECRET_KEY'] = 'flarp'

#flask_bootstrap fills in some boilerplate in the template
Bootstrap(gui_app)

#ConfigParser helps with manipulating config files
parser = ConfigParser()
config_file = 'config/config.ini'


# This function takes a dictionary and updates the config file in the base directory.
# This function checks for specific keys and only updates when key exists and value is not an empty string.
def edit_config(settings_dict):
    parser.read(config_file)
    if 'default_base_file_path' in settings_dict and settings_dict['default_base_file_path'] != '':
        parser.set('Default', 'base_file_path', settings_dict['default_base_file_path'])
    if 'default_query_path' in settings_dict and settings_dict['default_query_path'] != '':
        parser.set('Default', 'query_path', settings_dict['default_query_path'])
    if 'default_database' in settings_dict and settings_dict['default_database'] != '':
        parser.set('Default', 'database', settings_dict['default_database'])
    if 'default_notification_recipient' in settings_dict and settings_dict['default_notification_recipient'] != '':
        parser.set('Default', 'notification_recipient', settings_dict['default_notification_recipient'])
    if 'email_username' in settings_dict and settings_dict['email_username'] != '':
        parser.set('Email', 'username', settings_dict['email_username'])
    if 'email_password' in settings_dict and settings_dict['email_password'] != '':
        parser.set('Email', 'password', settings_dict['email_password'])
    if 'email_host' in settings_dict and settings_dict['email_host'] != '':
        parser.set('Email', 'host', settings_dict['email_host'])
    if 'email_disabled' in settings_dict and str(settings_dict['email_disabled']) != '':
        parser.set('Email', 'disabled', str(settings_dict['email_disabled']))
    if 'email_signature' in settings_dict and settings_dict['email_signature'] != '':
        parser.set('Email', 'signature', settings_dict['email_signature'])
    if 'logging_server' in settings_dict and settings_dict['logging_server'] != '':
        parser.set('Logging', 'server', settings_dict['logging_server'])
    if 'logging_to_file' in settings_dict and settings_dict['logging_to_file'] != '':
        parser.set('Logging', 'log_to_file', settings_dict['logging_to_file'])
    if 'logging_file' in settings_dict and settings_dict['logging_file'] != '':
        parser.set('Logging', 'logfile', settings_dict['logging_file'])
    if 'logging_db' in settings_dict and settings_dict['logging_db'] != '':
        parser.set('Logging', 'db', settings_dict['logging_db'])
    if 'debug_mode' in settings_dict and settings_dict['debug_mode'] != '':
        parser.set('Debug', 'debug_mode', settings_dict['debug_mode'])
    if 'debug_recipients' in settings_dict and settings_dict['debug_recipients'] != '':
        parser.set('Debug', 'debug_recipients', settings_dict['debug_recipients'])
    if 'admin_email' in settings_dict and settings_dict['admin_email'] != '':
        parser.set('Admin', 'admin_email', settings_dict['admin_email'])
    with open(config_file, 'w') as configfile:
        parser.write(configfile)

# This function takes a settings_dictionary and updates the config file in the base directory.
# This function will add a new section to the config file if the provided section name (connection_name)
# is unique.  Otherwise it will update the section with the options provided.  If the section is new
# the connection_name will be appended to the connections option in the Default section (this assists
# in iteration over the connection sections).  Blank, extra, and missing options are ignored.
def add_connection(settings_dict):
    parser.read(config_file)
    if 'connection_name' in settings_dict and settings_dict['connection_name'] != '':
        connection_name = settings_dict['connection_name']
        connections = parser.get('Default', 'connections')
        if connection_name in ['Default', 'Email', 'Debug', 'Logging', 'Admin']:
            return 'Invalid connection name.'
        if connection_name not in connections.split(", "):
            parser.add_section(connection_name)
            parser.set('Default', 'connections', connections + ', ' + connection_name)
    if 'rdbms' in settings_dict and settings_dict['rdbms'] != '':
        parser.set(connection_name, 'rdbms', settings_dict['rdbms'])
    if 'connection_host' in settings_dict and settings_dict['connection_host'] != '':
        parser.set(connection_name, 'host', settings_dict['connection_host'])
    if 'connection_port' in settings_dict and settings_dict['connection_port'] != '':
        parser.set(connection_name, 'port', settings_dict['connection_port'])
    if 'connection_user' in settings_dict and settings_dict['connection_user'] != '':
        parser.set(connection_name, 'user', settings_dict['connection_user'])
    if 'connection_password' in settings_dict and settings_dict['connection_password'] != '':
        parser.set(connection_name, 'password', settings_dict['connection_password'])
    if 'schema' in settings_dict and settings_dict['schema'] != '':
        parser.set(connection_name, 'schema', settings_dict['schema'])
    with open(config_file, 'w') as configfile:
        parser.write(configfile)

# This function takes a string and updates the config file in the base directory.
# If a section name matches the provided string, then that section and all its options are removed.
# It is removed from the connections option in the Default section, if present.
def delete_connection(connection_name):
    # print(connection_name)
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

def get_queries():
    parser.read(config_file)
    query_path = parser.get('Default', 'query_path')
    all_queries = []
    for file_name in os.listdir(query_path):
        if file_name.endswith('.sql'):
            no_extension = os.path.splitext(file_name)[0]
            all_queries.append(no_extension)
    return all_queries

def save_query(query_name, sql):
    parser.read(config_file)
    query_path = parser.get('Default', 'query_path')
    file_path = os.path.join(query_path, query_name + '.sql')
    with open(file_path, 'w') as f:
        f.write(sql)

def delete_query(query_name):
    parser.read(config_file)
    query_path = parser.get('Default', 'query_path')
    file_path = os.path.join(query_path, query_name + '.sql')
    os.remove(file_path)

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
    config_form.default_database.choices = connection_choices + connection_choice_additions
    config_form.logging_server.choices = connection_choices + connection_choice_additions
    rdbms_options = ['mysql', 'sqlite']
    rdbms_choices = [(i,i) for i in rdbms_options]
    connection_form.rdbms.choices = rdbms_choices

    if config_form.config_submit.data and config_form.validate():
        edit_config(config_form.data)
        flash('Settings Updated')
        all_config_options=read_config()
        connections = all_config_options["Default"]["connections"].split(", ")
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

@gui_app.route('/api/test_connection/<connection_name>', methods=['GET'])
def test_connection(connection_name):
    conn = ConnectionManager(db = connection_name)
    try:
        conn.connect()
        conn.close()
        return 'Connected Successfully'
    except:
        return 'Failed to Connect'

@gui_app.route('/api/schema_info/<connection_name>', methods=['GET'])
def schema_info(connection_name):
    conn = ConnectionManager(db = connection_name)
    try:
        conn.connect()
        sql = """SELECT table_name, table_schema, column_name
                FROM information_schema.columns
                WHERE table_schema <> 'information_schema'
                ORDER BY table_schema, table_name, column_name;"""
        results = conn.conn.execute(sql)
        resultset = [dict(row) for row in results]
        conn.close()
        return jsonify(resultset)
    except:
        return 'Failed to Connect'

@gui_app.route('/api/queries/<query_name>', methods=['GET', 'POST'])
def get_query_sql(query_name):
    if request.method == 'GET':
        query = QueryReader(filename=query_name)
        query.read()
        return query.sql
    elif request.method == 'POST':
        query_name = request.form['query_name']
        if request.form['delete_query'] == 'Yes':
            delete_query(query_name)
        else:
            sql = request.form['raw_sql']
            save_query(query_name=query_name, sql=sql)
        all_queries = get_queries()
        return jsonify(all_queries)

@gui_app.route('/api/execute_sql', methods=['POST'])
def execute_sql():
    sql = request.form['sql']
    connection_name = request.form['connection_name']
    cm = ConnectionManager(db = connection_name, read_only = True)
    cm.connect()
    query = QueryGenerator(cm=cm, sql=sql)
    results = query.execute()
    result_set = [dict(row) for row in results.result_data]
    return jsonify(result_set)


@gui_app.route('/queries', methods=['GET'])
def queries():
    all_config_options=read_config()
    all_queries = get_queries()
    connections = all_config_options["Default"]["connections"].split(", ")
    return render_template('queries.html', connections=connections, all_queries=all_queries)


if __name__ == '__main__':
    gui_app.run(debug = True)
