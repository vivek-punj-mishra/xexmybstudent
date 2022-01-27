"""
Created on 23-Nov-2021

@author: prakash singh
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from exmyb_app import app

def mailer(subject, from_addr, password, to_addrs, cc_addrs=[], html_body=None, text_body=None):
    is_send = False
    # Create message container
    message = MIMEMultipart()
    message['subject'] = subject
    message['To'] = ','.join(to_addrs)
    message['Cc'] = ','.join(cc_addrs)
    message['From'] = from_addr
    message.preamble = 'This is a multi-part message in MIME format.\n'

    if html_body is not None:
        # Create message sub-container for html
        msg_html = MIMEMultipart()
        # Record the MIME types of both part-text/html.
        html_body = MIMEText(html_body, 'html')
        msg_html.attach(html_body)
        message.attach(msg_html)

    if text_body is not None:
        # Create message sub-container for text
        msg_text = MIMEMultipart()
        # Record the MIME types of both part-text/plain.
        text_body = MIMEText(text_body, 'plain')
        msg_text.attach(text_body)
        message.attach(msg_text)

    try:
        # Send the email via gmail SMTP server.
        server = smtplib.SMTP(app.config['SMTP_SERVER_ADDRESS'], app.config['SMTP_SERVER_PORT'])
        try:
            server.starttls()
            # Credentials (if needed) for sending the mail
            server.login(from_addr, password)
            # send e-mail
            send_adrss = to_addrs + cc_addrs
            server.sendmail(from_addr, send_adrss, message.as_string())
            is_send = True
            return is_send , "Email Sent!"

        except Exception as e:
            return is_send, str(e)

        finally:
            server.quit()

    except Exception as e:
        app.logger.error("Error::Sending Email:: {}".format(str(e)))
        return is_send, str(e)