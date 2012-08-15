#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This script browse a folder and its subfolders, looking for plain-text file which looks like mails.
It then ingest the found files and stores them in a single mbox file.

The non-mail files founds are considered as attachments and included in the ingested mails.

All ingested files are removed, only leaving files the script was not able to decide their fate.

In case of indecision, the script open a PDB prompt.

This script is full of cases hard-coded for my special needs. These are easy to spot and feel free to remove them to fit your needs.
"""

import os
import time
import shutil
import stat
import re
import mailbox
import subprocess
import mimetypes
from datetime import datetime

import email.utils
from email.parser import Parser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.MIMEText import MIMEText


## Configuration

ARCHIVE_FOLDER = './Mail'
MBOX_FILE = './export.mbox'

FORCED_ATTACHMENT = [
    './Mail/friend1/in/content.fla',
    './Mail/friend2/in/sources/Makefile',
    ]

## End of configuration


mbox = mailbox.mbox(MBOX_FILE)

def get_date(s):
    """
    Transform a string to a mail-ready date
    """
    date = None
    try:
        date = datetime.strptime(s, '%d/%m/%y %H:%M:%S')
    except ValueError:
        try:
            date = datetime.strptime(s, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            try:
                date = datetime.strptime(s, '%d/%m/%Y %H:%M')
            except ValueError:
                pass
    if date:
        date = email.utils.formatdate(time.mktime(date.timetuple()), True)
    return date


# I was too lazy to code a proper loop, so I used this qhick and dirty loop.
# The right condition to stop iterating is having no mails left to ingest.
for i in range(10):

    for path, dirs, files in os.walk(ARCHIVE_FOLDER):
        print "Processing folder %s" % path
        if len(dirs):
            print "This folder has sub folders, skip it..."
            continue
        # Count the number of non-mail files
        mail_files = []
        non_mail_files = []

        for file_name in files:
            filepath = os.path.join(path, file_name)
            if filepath in FORCED_ATTACHMENT:
                non_mail_files.append(filepath)
                continue
            file_content = open(filepath, 'r').read()
            mail = Parser().parsestr(file_content)

            # Detect french-translated headers and translate them
            if len(mail.keys()) == 1 and mail.get('De', None) is not None:
                replace_str = [
                    ("De:\r\n", "From: "),
                    ("Sujet: ", "Subject: "),
                    ("A: ", "To: "),
                    ("\r\n", "\n"),
                    ]
                for (s, r) in replace_str:
                    file_content = file_content.replace(s, r)
                date = None
                fc = ""
                for l in file_content.split('\n'):
                    if l.startswith("Date: "):
                        date = get_date(l.split('Date: ')[1])
                        fc += 'Date: %s\n' % (date)
                    else:
                        fc += l + '\n'
                mail = Parser().parsestr(fc)

            # General purpose fixes
            else:
                for d in mail.defects:
                    if isinstance(d, email.errors.StartBoundaryNotFoundDefect):
                        mail.del_param('boundary')
                        mail_body = mail.get_payload()
                        # Strip redundant HTML part
                        mail_body = re.sub('(?is)<!DOCTYPE (.*)>', '', mail_body)
                        mail_body = re.sub('(?is)<html>(.*)</html>', '', mail_body)
                        mail_body = re.sub('(?is)<p>(.*)>', '', mail_body)  # Yahoo! mail footer is not enclosed by proper <html> tags, but always starts with a <p>
                        if mail_body != mail.get_payload():
                            mail.set_payload(mail_body.strip())
                    elif isinstance(d, email.errors.MultipartInvariantViolationDefect):
                        mail.set_type('text/plain', requote=False)
                    else:
                        # Unknown mail parsing defect
                        import pdb; pdb.set_trace()
                # Messages from voila seems to have messy encoding
                if mail.get('Message-Id', '').find('@voila.fr') != -1:
                    del mail['Content-Transfer-Encoding']

            # If we found headers then it means the file was being parsed well as an email.
            if len(mail.keys()):
                mail_files.append((filepath, mail))
            else:
                mime_type = mimetypes.guess_type(filepath)[0]
                if mime_type == 'text/plain':
                    print "Consider %s as a mail." % filepath
                    mail = MIMEText(open(filepath, 'r').read())
                    mail_files.append((filepath, mail))
                elif not mime_type:
                    import pdb; pdb.set_trace()
                else:
                    non_mail_files.append(filepath)

        # Bundle attachements to their mails
        if len(non_mail_files):
            if len(mail_files) == 1:
                # Attach all non-mail files to the only mail found here
                print "Add to %s these attachements: %r" % (mail_files[0][0], non_mail_files)
                mail = mail_files[0][1]

                # Transform our simple mail to a multipart one
                if not mail.is_multipart():
                    new_mail = MIMEMultipart()
                    new_mail.attach(MIMEText(mail.get_payload()))
                    # Transfer all headers
                    headers_to_transfer = set([h.lower() for h in mail.keys()]) - set([h.lower() for h in new_mail.keys()])
                    for h in headers_to_transfer:
                        h_value = mail.get_all(h)
                        print repr(h)
                        print repr(h_value)
                        if type(h_value) == type([]):
                            for v in h_value:
                                new_mail.add_header(h, v)
                        else:
                            new_mail.add_header(h, h_value)
                    mail = new_mail

                for f in non_mail_files:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(open(f, "rb").read())
                    Encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
                    mail.attach(part)
                    os.remove(f)

                mail_files[0] = (mail_files[0][0], mail)
            else:
                print "Can't decide how to bundle the %s non-mail files among the %s mails. Skip the folder..." % (len(non_mail_files), len(mail_files))
                continue

        parent_folder_name = os.path.split(path)[-1]
        parent_folders = path.split(os.sep)[::-1]

        for (filepath, mail) in mail_files:

            # The mail was saved from an IMP account
            if mail.get('X-Mailer-Version', None) == 'v3.57 (r)' and not mail.get('From', None) and not mail.get('Date', None):
                mail.add_header('From', 'me@example.com')
                # Get the main body of the mail
                mail_body = None
                if mail.is_multipart():
                    for payload in mail.get_payload():
                        if isinstance(payload, email.mime.text.MIMEText):
                            mail_body = payload.get_payload()
                            break
                else:
                    mail_body = mail.get_payload()
                assert type(mail_body) == type('')
                # Find the hard coded date
                date = None
                # Normalize line endings
                mail_body = mail_body.replace('\r\n', '\n')
                cleaned_body = ''
                for l in mail_body.split('\n'):
                    # Exclude body content until we find the date
                    if not date:
                        if l:
                            date = get_date(l)
                            if not date:
                                # We have failed to convert the first non-empty line of the payload, which means the mail doesn't looks like what we expect:
                                # We probably found a new species that we must analyze
                                import pdb; pdb.set_trace
                                break
                    else:
                        cleaned_body += l + '\n'
                # If we haven't found the date, then restore the body to its original state
                if date:
                    mail.add_header('Date', date)
                    cleaned_body = cleaned_body.strip()
                    if mail.is_multipart():
                        payload.set_payload(cleaned_body)
                    else:
                        mail.set_payload(cleaned_body)

            # If there is no subject, then use the file name
            if not mail.get('Subject', None):
                subject = os.path.splitext(os.path.split(filepath)[-1])[0]
                print "Transform filepath %s to subject %r" % (filepath, subject)
                mail.add_header('Subject', subject)

            # If no date found: use the date of the file
            if not mail.get('Date', None):
                mail.add_header('Date', email.utils.formatdate(os.path.getmtime(filepath)))

            # Adjust some mails before saving
            folder_from_map = {
                './Mail/friend1/out/': ['me@example.com'],
                './Mail/friend2/out/': ['me@example.com'],
                './Mail/friend1/in/': ['friend1@example.com'],
                './Mail/friend2/in/': ['friend2@example.com'],
                }
            if not mail.get('From', None):
                for p in folder_from_map:
                    if filepath.startswith(p):
                        for m in folder_from_map[p]:
                            mail.add_header('From', m)
                        break

            # Adjust some mails before saving
            folder_to_map = {
                './Mail/friend1/out/': ['friend1@example.com'],
                './Mail/friend2/out/': ['friend2@example.com'],
                './Mail/friend1/in/': ['me@example.com'],
                './Mail/friend2/in/': ['me@example.com'],
                }
            if not mail.get('To', None):
                del mail["To"]
                for p in folder_to_map:
                    if filepath.startswith(p):
                        for m in folder_to_map[p]:
                            mail.add_header('To', m)
                        break

            try:
                assert mail.get('From', None) is not None
                assert mail.get('To', None)
                assert mail.get('Subject', None) is not None
                assert mail.get('Date', None) is not None
            except:
                import pdb; pdb.set_trace()

            mbox.add(mailbox.mboxMessage(mail))
            # The mail was successfuly migrated, remove its source
            os.remove(filepath)

    # Remove empty folders
    for root, dirs, files in os.walk(ARCHIVE_FOLDER, topdown=False):
        for name in dirs:
            fname = os.path.join(root, name)
            if os.path.exists(fname) and not os.listdir(fname):
                print 'Remove %s ...' % fname
                os.removedirs(fname)
