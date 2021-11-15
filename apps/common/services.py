from django.conf import settings
import hashlib
from random import randint

import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_mail(to_email,subject,html_content):
    message = Mail(
        from_email=settings.EMAIL_FROM_ADDRESS,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(api_key=settings.EMAIL_API_KEY)
        response = sg.send(message)
        print(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def generate_token(token_length):
    range_start = 10**(token_length-1)
    range_end = (10**token_length)-1
    return randint(range_start, range_end)

def generate_hash_token(prefix=""):
    token = generate_token(25)
    m = hashlib.md5()
    m.update((prefix+str(token)).encode())
    return m.hexdigest()
