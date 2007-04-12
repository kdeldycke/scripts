#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2007 Kevin Deldycke <kev@coolcavemen.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

"""
  Last update: 2007 apr 12

  Requirements:
    * python
    * python iCalendar

  Features:
    *
    *

  TODO:
    *
    *
    *
"""

################### Start of user config ###################

# Maildir to browse
MAIL_DIR = "/home/kevin/Maildir"

# Name of the iCalendar file
ICAL_FILE = "kev-mails.ics"

# Number of minutes before the mail (= time when the iCal event will start)
TIME_SLOT = 5

# Do not include details like mail body and mail receiver. Just keep the author and the date.
CONFIDENTIAL = False

#################### End of user config ####################
################ Do not modify code below ! ################

import mailbox, email, random, sys
from os        import getcwdu
from os.path   import abspath, exists, isdir
from datetime  import datetime, timedelta
from icalendar import Calendar, Event, UTC



# Global variable that contain the calendar and statistics
global cal, mail_count



def decodeHeader(h):
  """
    Parse and decode header data (try to).
  """
  parts = email.Header.decode_header(h)
  try:
    new_header = email.Header.make_header(parts)
  except UnicodeDecodeError:
    # Force UTF-8 header
    for part_index in range(len(parts)):
      (string, enc) = parts[part_index]
      if enc == None:
        parts[part_index] = (string, 'utf-8')
    try:
      new_header = email.Header.make_header(parts)
    except:
      return h
  return unicode(new_header)



def browseMailDir(maildir):
  """
    This recursive method browse each folder and convert each mail that match criterion to an event
  """
  global mail_count

  # Analyse each mail in the maildir
  for maildir_mail in maildir:
    # parse the message:
    mail = email.message_from_string(str(maildir_mail))

    # Reject all mails by default
    reject = True

    # Filter emails to find mails that came from me
    author = decodeHeader(mail['From'])
    if author.find("kevin@deldycke.com") != -1:

      # Mail come from me, keep it
      reject = False

      # Eliminate false-positive now.
      # Ignore automatic unit tests mail reports sent by the dev server (aka 10.1.0.33)
      # XXX Is a replied mail feature this IP adress ??
      for v in (mail.get_all("Received") or []):
        if decodeHeader(v).find("10.1.0.33") != -1:
          reject = True
          break

    # Get a one-line subject
    if not CONFIDENTIAL:
      subject = decodeHeader(mail['Subject']).replace('\t', ' ').replace('\n', '')
    else:
      subject = "Mail"

    # Proceed to next mail if email was not detected as mine
    if reject:
      #print " SKIP - %s -by- %s" % (subject, author)
      continue
    else:
      print " KEEP - %s -by- %s" % (subject, author)

    # Convert mail date to python datetime object
    mail_date = email.Utils.parsedate(decodeHeader(mail['Date']))
    py_datetime = datetime( mail_date[0]
                          , mail_date[1]
                          , mail_date[2]
                          , mail_date[3]
                          , mail_date[4]
                          , mail_date[5]
                          , 0
                          , tzinfo=UTC
                          )

    # iCalendar events must be defined by a time slot with a start and a stop date/time.
    # There is no such equivalent for mail: a mail has just a date.
    # I choose to use the mail date as the end of the iCal event. The start of the event will be set as the mail date minus 5 minutes.
    event_start = py_datetime - timedelta(minutes=TIME_SLOT)

    # Get the destination email
    if not CONFIDENTIAL:
      dest = decodeHeader(mail['To'])
    else:
      dest = "XXXX XXXXXXXXX <xxxx@xxxx.xxx>"

    # Get the body of the mail
    mail_body = ""
    if not CONFIDENTIAL:
      for part in mail.walk():
        if part.get_content_type() == "text/plain":
          if part.get_content_charset() == None:
            mail_body += unicode(part.get_payload(decode=True))
          else:
            mail_body += unicode(part.get_payload(decode=True), part.get_content_charset())

    # Create a new calendar event
    event = Event()
    event.add('summary', subject)
    event.add('description', "From: %s\nTo: %s\n\n%s" % (author, dest, mail_body))
    event.add('dtstart', event_start)
    event.add('dtend', py_datetime)
    event.add('dtstamp', event_start)
    event.add('priority', 5)

    # Generate message UID
    if mail.has_key("Message-Id"):
      event['uid'] = decodeHeader(mail["Message-Id"])
    else:
      event['uid'] = '%s-%s-%s@kev.coolcavemen.com' % (py_datetime, author, random.random())

    # Add the event to the calendar
    cal.add_component(event)

    # Compute statistics
    mail_count += 1

  # Browse each sub maildir
  for folder in maildir.list_folders():
    sub_maildir = maildir.get_folder(folder)
    browseMailDir(sub_maildir)



if __name__ == "__main__":

  # Use script folder as work folder and normalize path
  work_dir     = abspath(getcwdu())
  ical_file    = abspath("%s/%s" % (work_dir, ICAL_FILE))
  maildir_path = abspath(MAIL_DIR)

  # Check maildir
  if not exists(maildir_path):
    print "FATAL - '%s' maildir doesn't exist !" % maildir_path
    sys.exit(1)
  elif not isdir(maildir_path):
    print "FATAL - '%s' maildir is not a directory !" % maildir_path
    sys.exit(1)

  # Init statistics variables
  mail_count = 0

  # Create a brand new calendar
  cal = Calendar()
  cal.add('prodid', '-//MAILDIR2ICAL//kev.coolcavemen.com//')
  cal.add('version', '2.0')

  # Open and parse the top maildir
  maildir = mailbox.Maildir(MAIL_DIR, email.message_from_file)
  browseMailDir(maildir)

  # Write the iCal file
  f = open(ical_file, "w")
  f.write(cal.as_string())
  f.close()

  # Exit
  print " INFO - Calendar created as '%s' with %s mails." % (ical_file, mail_count)
  sys.exit(0)
