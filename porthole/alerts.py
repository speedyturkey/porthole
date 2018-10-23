from functools import wraps
from .app import config
from .logger import PortholeLogger
from .mailer import Mailer

logger = PortholeLogger("Alerts")


class Alert(object):
    def __init__(self, subject, message, recipients=None):
        project_name = config['Default'].get('project', '<Unspecified Project>')
        mailer = Mailer()
        mailer.recipients = recipients or [config['Admin']['admin_email']]
        mailer.subject = "{} ALERT: ".format(project_name.upper()) + subject
        mailer.message = message
        self.mailer = mailer

    def send(self):
        self.mailer.send_email()

    def send_email(self):
        self.send()


class DebugAlert(Alert):
    def __init__(self, recipients=None):
        subject = 'Debug Mode Active'
        message = 'Debug mode is currently active - please disable it.'
        super().__init__(subject, message, recipients)
        debug_mode = config.getboolean('Debug', 'debug_mode')
        if debug_mode:
            self.send()


def send_alert_on_exception(function_to_be_decorated):
    """Use as a decorator to ensure that an alert is sent for any unhandled exceptions."""
    @wraps(function_to_be_decorated)
    def decorated_function():
        project_name = config['Default'].get('project', '<Unspecified Project>')
        calling_module = getattr(function_to_be_decorated, '__module__', '<Unspecified Module>')
        try:
            function_to_be_decorated()
        except Exception as error:
            alert = Alert(
                subject="{} Unhandled Exception Notification: ".format(project_name) + calling_module,
                message=str(error)
            )
            logger.error("Unhandled exception in {} - sending alert message.".format(calling_module))
            alert.send()
    return decorated_function
