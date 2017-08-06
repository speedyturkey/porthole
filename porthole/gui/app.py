from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from configparser import ConfigParser
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flarp'
Bootstrap(app)
parser = ConfigParser()

# function takes a dictionary of config values and updates config is the vallues are not blank
def edit_config(dict):
    parser.read('config.ini')
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
    if 'email_disabled' in dict and dict['email_disabled'] != '':
        parser.set('Email', 'disabled', dict['email_disabled'])
    if 'email_signature' in dict and dict['email_signature'] != '':
        parser.set('Email', 'signature', dict['email_signature'])
    if 'logging_server' in dict and dict['logging_server'] != '':
        parser.set('Logging', 'server', dict['logging_server'])
    if 'logging_db' in dict and dict['logging_db'] != '':
        parser.set('Logging', 'db', dict['logging_db'])
    if 'debug_mode' in dict and dict['debug_mode'] != '':
        parser.set('Debug', 'debug_mode', dict['debug_mode'])
    if 'debug_recipients' in dict and dict['debug_recipients'] != '':
        parser.set('Debug', 'debug_recipients', dict['debug_recipients'])
    if 'admin_email' in dict and dict['admin_email'] != '':
        parser.set('Admin', 'admin_email', dict['admin_email'])

    with open('config.ini', 'w') as configfile:
        parser.write(configfile)

def add_connection(dict):
    parser.read('config.ini')
    if 'connection_name' in dict and dict['connection_name'] != '':
        parser.add_section(dict['connection_name'])
        connection_list = parser.get('Default', 'connection_list')
        parser.set('Default', 'connection_list', connection_list.append(dict['connection_name']))
    if 'rdbms' in dict and dict['rdbms'] != '':
        parser.set(connection_name, 'rdbms', dict['rdbms'])
    if 'host' in dict and dict['host'] != '':
        parser.set(connection_name, 'host', dict['connection_host'])
    if 'port' in dict and dict['port'] != '':
        parser.set(connection_name, 'port', dict['connection_port'])
    if 'user' in dict and dict['user'] != '':
        parser.set(connection_name, 'user', dict['connection_user'])
    if 'password' in dict and dict['password'] != '':
        parser.set(connection_name, 'password', dict['connection_password'])
    if 'schema' in dict and dict['schema'] != '':
        parser.set(connection_name, 'schema', dict['schema'])

def read_config():
    parser.read('config.ini')
    all_config_options = {}
    sections = parser.sections()
    for section in sections:
        all_config_options.update({section : {}})
        options = parser.options(section)
        for option in options:
            all_config_options[section].update({option : parser.get(section, option)})
    return all_config_options


class ConnectionForm(FlaskForm):
    connection_name = StringField('connection_name')
    rdbms = StringField('rdbms')
    connection_host = StringField('connection_host')
    connection_port = StringField('connection_port')
    connection_user = StringField('connection_user')
    connection_password = StringField('connection_password')
    schema = StringField('schema')
    connection_submit = SubmitField('submit')

class ConfigForm(FlaskForm):
    default_base_file_path = StringField('default_base_file_path')#, validators=[InputRequired()])
    default_query_path = StringField('default_query_path')
    default_database = StringField('default_database')
    default_notification_recipient = StringField('default_notification_recipient')
    email_username = StringField('email_username')
    email_password = StringField('email_password')
    email_host = StringField('email_host')
    email_disabled = StringField('email_disabled')
    email_signature = StringField('email_signature')
    logging_server = StringField('logging_server')
    logging_db = StringField('logging_db')
    debug_mode = StringField('debug_mode')
    debug_recipients = StringField('debug_recipients')
    admin_email = StringField('admin_email')
    config_submit = SubmitField('Save Settings')
    config_cancel = SubmitField('Cancel')


@app.route('/config', methods=['GET', 'POST'])
def config():
    all_config_options=read_config()
    config_form = ConfigForm(default_base_file_path=all_config_options["Default"]["base_file_path"]
                            , default_query_path = all_config_options["Default"]["query_path"]
                            , default_database = all_config_options["Default"]["database"]
                            , default_notification_recipient = all_config_options["Default"]["notification_recipient"]
                            , email_username = all_config_options["Email"]["username"]
                            , email_password = all_config_options["Email"]["password"]
                            , email_host = all_config_options["Email"]["host"]
                            , email_disabled = all_config_options["Email"]["disabled"]
                            , email_signature = all_config_options["Email"]["signature"]
                            , logging_server = all_config_options["Logging"]["server"]
                            , logging_db = all_config_options["Logging"]["db"]
                            , debug_mode = all_config_options["Debug"]["debug_mode"]
                            , debug_recipients = all_config_options["Debug"]["debug_recipients"]
                            , admin_email = all_config_options["Admin"]["admin_email"])

    connection_form = ConnectionForm()

    if config_form.config_submit.data and config_form.validate():
        edit_config(config_form.data)
        flash('Settings Updated')
        return render_template("forms.html", config_form=config_form, connection_form=connection_form, all_config_options=all_config_options)


    if connection_form.connection_submit.data and connection_form.validate():
        return 'Form submitted. All the data look like {}.'.format(connection_form.data)

    return render_template("forms.html", config_form=config_form, connection_form=connection_form, all_config_options=all_config_options)



if __name__ == '__main__':
    app.run(debug = True)
