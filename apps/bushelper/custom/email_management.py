import smtplib, ssl, json
from email.mime.text import MIMEText

from django.contrib.staticfiles.templatetags.staticfiles import static
from urllib.request import urlopen
from email.mime.multipart import MIMEMultipart

def smtp_session(foo):
    def initialize_session(**kwargs):
        request = urlopen(static('json/credentials.json'))
        data = json.loads(request.read())['email']
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(data['host'], data['port'], context=context) as server:
            server.login(data['address'], data['password'])
            return foo(server=server, sender=data['address'], **kwargs)
    return initialize_session


@smtp_session
def send_email(server=None, sender=None, receiver=None, context=None):
    message = MIMEMultipart()
    try:
        message["Subject"] = context['subject']
    except KeyError:
        pass
    try:
        message['From'] = context['from']
    except KeyError:
        message["From"] = sender
    try:
        message['To'] = context['to']
    except KeyError:
        message["To"] = receiver

    body = MIMEText(context['body'], 'html')
    message.attach(body)
    server.sendmail(sender, receiver, message.as_string())