import smtplib
from email import message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

class EmailNotification():
    def __init__(self, smtp_host, smtp_port, username, passowrd):
        self.from_email = username
        self.server = smtplib.SMTP(smtp_host, smtp_port)
        self.server.starttls()
        self.server.login(username, passowrd)
    
    def send_message(self, to_emails, subject, body_html, cc_emails=None, bcc_emails=None, attach_filepath=None):
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = to_emails
        msg["Cc"] = cc_emails
        msg["Bcc"] = bcc_emails
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        # ファイルを添付する
        if attach_filepath:
            with open(attach_filepath, "rb") as f:
                mb = MIMEApplication(f.read())
                filename = os.path.basename(attach_filepath)
                mb.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(mb)

        self.server.send_message(msg)
