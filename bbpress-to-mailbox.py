#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
I created this script to generate a backup of a bbPress forum in the form of a mailbox.

This script parse CSV files of forum's topics and replies that was produced directly by these 2 MySQL queries:

    SELECT p.ID AS msg_id, p.ID AS topic_id, u.display_name AS realname, u.user_email AS from, p.post_date_gmt AS date, p.post_title AS subject, p.post_content AS body
        INTO OUTFILE '/tmp/forum-topic-export.csv'
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        ESCAPED BY '\\'
        LINES TERMINATED BY '\r\n'
    FROM wp_posts AS p
    LEFT JOIN wp_users AS u ON p.post_author = u.ID
    WHERE p.post_type = "topic" AND p.post_parent = 15894;

    SELECT p.ID AS msg_id, p.post_parent AS topic_id, u.display_name AS realname, u.user_email AS from, p.post_date_gmt AS date, p.post_title AS subject, p.post_content AS body
        INTO OUTFILE '/tmp/forum-reply-export.csv'
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        ESCAPED BY '\\'
        LINES TERMINATED BY '\r\n'
    FROM wp_posts AS p
    LEFT JOIN wp_users AS u ON p.post_author = u.ID
    WHERE p.post_type = "reply" AND p.post_parent IN (
        SELECT ID
        FROM wp_posts
        WHERE post_type = "topic" AND post_parent = 15894
    );
"""


## Configuration

TOPIC_CSV_FILE = '/tmp/forum-topic-export.csv'
REPLY_CSV_FILE = '/tmp/forum-reply-export.csv'
TO_ADDRESS = 'Private Forum <private@mailing-list.example.com>'
MBOX_FILE = './forum-export.mbox'

## End of configuration


import csv
import mailbox
import time
from datetime import datetime
import HTMLParser

import email.utils
import email.header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.MIMEText import MIMEText


TO_DOMAIN = email.utils.parseaddr(TO_ADDRESS)[1].split('@')[1]

body_cleaning = [
    # HTML normalization
    ('\r\n', '\n'),
    ('\n', '<br/>'),
    # Replace some emoticon shorcuts to ASCII
    ('!dodge', ':D'),
    ('!amazed', ':D'),
    ]

imported_topics = {}

html_parser = HTMLParser.HTMLParser()

mbox = mailbox.mbox(MBOX_FILE)


# Parse topic first to ger replies' default titles
for (file_path, is_topic) in [(TOPIC_CSV_FILE, True), (REPLY_CSV_FILE, False)]:

    print "Processing %r ..." % file_path

    for row in csv.reader(open(file_path, 'rb'), delimiter=',', quotechar='"', escapechar='\\', lineterminator='\r\n'):
        message_data = dict(zip(['msg_id', 'topic_id', 'realname', 'From', 'Date', 'Subject', 'body'], list(row)))
        mail = MIMEMultipart('alternative')

        for (header_name, header_value) in message_data.items():
            header_value = header_value.strip()

            if header_name == 'body':
                for (s1, s2) in body_cleaning:
                    header_value = header_value.replace(s1, s2)

                html_body = "<html><body>%s</body></html>" % header_value
                mail.attach(MIMEText(html_body, 'html', 'UTF-8'))

                # TODO: Transform the HTML to plain text
                #text_body = header_value
                #mail.attach(MIMEText(text_body, 'plain', 'UTF-8'))

            if header_name in ['msg_id', 'topic_id', 'realname', 'body']:
                continue

            if header_name == 'From':
                header_value = email.utils.formataddr((message_data['realname'], message_data['From']))

            if header_name == 'Date':
                # Expecting date of the form: 2005-01-30 08:40:25
                d = datetime.strptime(header_value, '%Y-%m-%d %H:%M:%S')
                header_value = email.utils.formatdate(time.mktime(d.timetuple()))

            if header_name == 'Subject':
                header_value = html_parser.unescape(header_value.decode('UTF-8'))
                header_value = email.header.Header(header_value, 'iso-8859-1').encode()

            if header_value:
                mail.add_header(header_name, header_value)

        mail.add_header('To', TO_ADDRESS)
        mail.add_header('Reply-to', TO_ADDRESS)
        mail.add_header('List-Id', TO_ADDRESS.replace('@', '.'))

        mail_id = email.utils.formataddr((None, '@'.join([email.utils.parseaddr(email.utils.make_msgid())[1].split('@')[0], TO_DOMAIN])))
        mail.add_header('Message-ID', mail_id)

        # Topic specific actions
        if is_topic:
            imported_topics[message_data['msg_id']] = mail

        # Reply specific actions
        else:
            topic_mail = imported_topics[message_data['topic_id']]
            topic_mail_id = topic_mail.get('Message-ID')
            mail.add_header('In-Reply-To', topic_mail_id)
            mail.add_header('References', topic_mail_id)
            if not mail.get('Subject'):
                mail.add_header('Subject', "Re: %s" % topic_mail.get('Subject'))

        mbox.add(mailbox.mboxMessage(mail))

        print "Added: %s, %s, %s" % (message_data.get('Date', None), mail.get('From'), mail.get('Subject'))
