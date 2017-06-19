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

COMMASPACE = ', '


class Mailer:
    def __init__(self, **kwargs):
        self.properties = kwargs
        self.debug_mode = config.getboolean('Debug', 'debug_mode')
        self.debug_email = [config['Debug']['debug_email']]
        self.send_from = config['Exchange']['exchange_user']
        self.exchange_user = config['Exchange']['exchange_user']
        self.exchange_password = config['Exchange']['exchange_password']
        self.host = config['Exchange'].get('host', 'smtp.office365.com')
        self.signature = config['Email']['signature']
        self.admin_email = config['Admin']['admin_email']

    def send_email(self):
        if config['Email']['disabled'] == 'True':
            print("Email disabled - exiting mailer.")
            exit()

        # Create the enclosing (outer) message
        outer = MIMEMultipart('alternative')
        outer['Subject'] = self.subject
        outer['To'] = COMMASPACE.join(self.recipients)
        outer['CC'] = COMMASPACE.join(self.cc_recipients)
        outer['From'] = self.send_from

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
                    print("Unable to add the attachment to the email")
                    raise

        composed = outer.as_string()

        all_recipients = set(self.recipients + self.cc_recipients)
        all_recipients = list(filter(None, all_recipients))

        try:
            with smtplib.SMTP(host='smtp.office365.com', port='587') as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(self.exchange_user, self.exchange_password)
                s.sendmail(self.exchange_user,
                           all_recipients,
                           composed)
                s.close()
                print("Email sent")
        except smtplib.SMTPConnectError as err:
            print("Unable to connect to the SMTP server to send email: {}".format(err))
            raise
        except:
            print("Unable to send email: {}".format(sys.exc_info()[0]))
            raise

if __name__ == '__main__':
    pass
