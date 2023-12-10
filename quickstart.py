from __future__ import print_function

import os.path
import datetime
import logging as log
import base64
from urllib.parse import urlencode, urlunparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import json


from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# LABEL ID's
# These were queried from service.users().labels().list(userId='me).execute()
# and iterated `label in labels`, printing label['name'] and label['id']
BILL_REQUESTED_LABEL = 'Label_6866626699238219716'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secrets/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        days_30_ago = (datetime.datetime.now() - datetime.timedelta(120)).strftime('%Y/%m/%d')
        natgrid_subject = 'Your paperless gas bill is attached'

        query = f'subject:"{natgrid_subject}"'

        response = service.users().messages().list(userId='me', q=query).execute()
        messages = response.get('messages', [])
        for msg in messages:
            data = service.users().messages().get(userId='me', id=msg['id']).execute()
            if BILL_REQUESTED_LABEL in data['labelIds']:
                print('requested')
                continue
            
            content = base64.urlsafe_b64decode(data['payload']['body']['data']).decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            spans = soup.find_all('span')
            found_dollar = False
            try:
                text =  [s.get_text(strip=True) for s in spans]
            except ValueError:
                print('ERROR! Could not find the $ in the body. Unable to determine bill amount')
                return

            start = text.index('$')
            [dollar, cents] = text[start+1:start+3]
            bill_date = text[start+4]
            bill_amount = f'{dollar}{cents}'
            request_amount = (str(float(bill_amount) / 2) + '00')[:5]
            print(request_amount)
            print(bill_date)

            query_params = {
                'txn': 'pay',
                'audience': 'private',
                'recipients': 'palencharizard',
                'amount': request_amount,
                'note': f'con ed {bill_date}',
            }

            link = urlunparse(('https', 'venmo.com', '/', '', urlencode(query_params), ''))
            print(link)
            email = make_email(link)
            sent_message = service.users().messages().send(userId='me', body={'raw': email}).execute()
            print(sent_message)
            return


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        log.error(f'An error occurred: {error}')


def make_email(pay_link, recipient=None):
    with open('./secrets/email.json', 'r') as fh:
        email_values = json.loads(fh.read())
    if recipient:
        email_values['to'] = recipient
    
    message = MIMEMultipart()
    message['to'] = email_values['to']
    message['subject'] = email_values['subject']
    body = MIMEText(email_values['body'].replace('{link}', pay_link))
    message.attach(body)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return raw_message

if __name__ == '__main__':
    main()
