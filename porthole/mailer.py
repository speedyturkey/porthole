"""
Mailer.py

"""

import sys
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .app import config
from .logger import PortholeLogger

logger = PortholeLogger(name=__name__)

COMMASPACE = ', '


class Mailer:
    def __init__(self, recipients=[], cc_recipients=[], **kwargs):
        self.recipients = recipients
        self.cc_recipients = cc_recipients
        self.properties = kwargs
        self.debug_mode = config.getboolean('Debug', 'debug_mode')
        debug_recipients = config['Debug']['debug_recipients']
        self.debug_recipients = [recip.strip() for recip in debug_recipients.split(';')]
        self.username = config['Email']['username']
        self.send_from = config['Email'].get('send_from', self.username)
        self.password = config['Email']['password']
        self.host = config['Email'].get('host', 'smtp.office365.com')
        self.signature = config['Email']['signature']
        self.admin_email = config['Admin']['admin_email']
        self.attachments = None
        self.all_sent_to_recipients = None

    def send_email(self):
        if config['Email']['disabled'] == 'True':
            logger.info("Email disabled - exiting mailer.")
            exit()

        # Create the enclosing (outer) message
        outer = MIMEMultipart('alternative')
        outer['Subject'] = self.subject
        outer['From'] = self.send_from
        if self.debug_mode:
            outer['To'] = COMMASPACE.join(self.debug_recipients)
        else:
            outer['To'] = COMMASPACE.join(self.recipients)
            outer['CC'] = COMMASPACE.join(self.cc_recipients)

        msg = MIMEBase('application', "octet-stream")

        # Add the text of the email
        email_body = MIMEText(self.message, 'plain')
        outer.attach(email_body)

        # Add the attachments
        if self.attachments:
            for file in self.attachments:
                try:
                    with open(file, 'rb') as fp:
                        msg.set_payload(fp.read())
                    encoders.encode_base64(msg)
                    msg.add_header('Content-Disposition',
                                   'attachment',
                                   filename=os.path.basename(file))
                    outer.attach(msg)
                except:
                    logger.exception("Unable to add the attachment to the email")
                    raise

        composed = outer.as_string()

        if self.debug_mode:
            logger.info("""Debug mode active. Sending only to designated debug recipient(s).

Active report would have been sent to:
            "To" Recipients: {}
            "CC" Recipients: {}""".format(self.recipients, self.cc_recipients))
            all_recipients = self.debug_recipients
        else:
            all_recipients = set(self.recipients + self.cc_recipients)
            all_recipients = list(filter(None, all_recipients))
            all_recipients.append(self.admin_email)

        try:
            with smtplib.SMTP(host=self.host, port='587') as s:
                s.ehlo()
                s.starttls()
                s.login(self.username, self.password)
                s.sendmail(self.send_from,
                           all_recipients,
                           composed)
                self.all_sent_to_recipients = all_recipients
                s.close()
                logger.info("Email with subject '{}...' sent to {} recipients".format(self.subject, len(all_recipients)))
        except smtplib.SMTPConnectError as err:
            logger.error("Unable to connect to the SMTP server to send email: {}".format(err))
            raise
        except:
            logger.exception("Unable to send email")
            raise

if __name__ == '__main__':
    pass
