#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'A simple bug checker that sends email notifications.'

__author__ = 'Oreki47'
import sys
import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation'))
from src.utilities import ConfigData

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'  # add absolute path
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        # manual validation, not needed after first use
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        # print ('Storing credentials to ' + credential_path)
    return credentials

def get_credentials_custom():
    credentails_dir = "/home/ethan/.credentials/gmail-python-email-send.json"
    store = oauth2client.file.Storage(credentails_dir)
    credentials = store.get()
    return credentials

def SendMessage(sender, to, subject, msgPlain):
    credentials = get_credentials_custom()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message = CreateMessage(sender, to, subject, msgPlain)
    result = SendMessageInternal(service, "me", message)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)
        return "Error"

def CreateMessage(sender, to, subject, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}

def check_logs(log_path):
    with open (log_path, 'r') as f:
        logs = f.readlines()

    logs = logs[::-1]
    for i in range(1, len(logs)):
        if logs[i].split('|')[-1].strip() == "":
            break
    logs = logs[1:i]
       
    time_end = datetime.strptime(logs[0].split('|')[0].split(',')[0], '%Y-%m-%d %H:%M:%S')
    time_str = datetime.strptime(logs[-1].split('|')[0].split(',')[0], '%Y-%m-%d %H:%M:%S')
    time_elapsed = time_end - time_str

    msg = ""
    logs = logs[::-1] 
    for log in logs:
        msg += (":").join(log.split('|')[2:]).strip()
        msg += "\n"

    msg += "Time elapsed: "
    msg += str(time_elapsed)
    msg += "."

    status = [log.split('|')[2].strip() for log in logs]
    if 'ERROR' in status:  # something is wroing
        return True, msg
    else:
        return False, msg
    

def main():

    # Run several checkers and sendout the email notifications
    CRALWER_LOG_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/steam_crawl_log.txt'
    APPDATA_LOG_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/app_data_etl_log.txt'
    STEAM_SPY_LOG_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/steam_spy_crawler_log.txt'

    crawler_state, crawler_msg = check_logs(CRALWER_LOG_PATH)
    appdata_state, appdata_msg = check_logs(APPDATA_LOG_PATH)
    steamspy_state, steamspy_msg = check_logs(STEAM_SPY_LOG_PATH)

    config = ConfigData('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/config.ini')

    if crawler_state == True:
        # send out email to notify developer.
        routine_to = config.mail_route_to
        sender = config.mail_sender
        subject = config.mail_crawler_failure_subject
        SendMessage(sender, routine_to, subject, crawler_msg)

    if appdata_state == True:
        routine_to = config.mail_route_to
        sender = config.mail_sender
        subject = config.mail_appdata_failure_subject
        SendMessage(sender, routine_to, subject, appdata_msg)

    if steamspy_state == True:
        routine_to = config.mail_route_to
        sender = config.mail_sender
        subject = config.mail_steam_spy_failure_subject
        SendMessage(sender, routine_to, subject, steamspy_msg)

if __name__ == '__main__':
    main()