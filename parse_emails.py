#!/usr/bin/env python
# coding: utf-8

from exchangelib import Credentials, Configuration, Account, Folder, DELEGATE
from datetime import date, datetime, timedelta
from pathlib import Path
from getpass import getpass

def connect_to_owa(email, password):
    pac_email = email
    pac_password = password
    
    credentials = Credentials(pac_email, pac_password)    
    config = Configuration(
        server='outlook.office365.com', 
        credentials=credentials)
    
    return Account(
        primary_smtp_address=pac_email, 
        config=config,
        autodiscover=False, 
        access_type=DELEGATE)
    
    
def manage_reports_in_inbox(account):
    
    reports = account.inbox.filter(
        subject__contains = 'People Counting Report', 
        author = 'donotreply@pacific.edu',
        has_attachments = True
    )
    
    for email in reports.all():
    
        # Report emails are generally sent around midnight local time which means some emails might be sent
        # on the day of the report while others sent the day after. If the report is sent before 
        # midnight (00:00:00), the hour value will be more than 20.
        #
        # We subtract one day only for emails that are sent after midnight
        if email.datetime_sent.astimezone(account.default_timezone).time().hour >= 20:
            email_datetime = email.datetime_sent.date()
        else:
            email_datetime = email.datetime_sent.date() - timedelta(days = 1)

        month_path = f'./attachments/{email_datetime.year}/{email_datetime.month}'

        if not Path(month_path).exists():
            Path(f'{month_path}/Main').mkdir(parents = True, exist_ok = True)
            Path(f'{month_path}/South').mkdir(parents = True, exist_ok = True)
            Path(f'{month_path}/Starbucks').mkdir(parents = True, exist_ok = True)

        for attachment in email.attachments:

            if 'Daily Report' not in attachment.name:
                continue

            file_name = str.replace(attachment.name, ' ', '_')

            if 'Starbucks' not in email.sender.name:
                folder_name = email.sender.name.split(' ')[1]
            else:
                folder_name = email.sender.name.split(' ')[0]

            file_path = Path(f'{month_path}/{folder_name}/{file_name}')
         
            with open(file_path, 'wb') as f:
                f.write(attachment.content)

        email.is_read = True
        email.save()
        email.move(counter_folder)
        print('Successfully parsed report email. Email moved to "Inbox/People Counter"')
        
    print('No reports left in Inbox.')


# Getting user info and connect to Office365 server
my_email = input("Please type in your email address:\n")
my_pass = getpass("Please type in your password:\n")

account = connect_to_owa(my_email, my_pass)

# Check if the People Counter folder exists in the inbox folder
try:
    counter_folder = account.inbox / 'People Counter'
except:
    counter_folder = Folder(parent = account.inbox, name='People Counter')
    counter_folder.save()
    
manage_reports_in_inbox(account)
