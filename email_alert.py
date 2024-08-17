import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = os.environ.get('email')
sender_password = os.environ.get('email_pw')
recipient_email = os.environ.get('email_recipient')
email_ip = os.environ.get('email_ip')


def send_alert(alert, db, table, exception):
    subject = f'Pipeline Alert: {alert}'
    message = (f'Pipeline {alert} on database: {db} ' +
               f'for table: {table} ' +
               f'with exception: {exception}')

    try:
        smtp_server = smtplib.SMTP(email_ip)
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        smtp_server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        print('SMTP Authentication Error:', e)
    except Exception as e:
        print('Error sending email:', e)
    finally:
        if smtp_server:
            smtp_server.quit()
