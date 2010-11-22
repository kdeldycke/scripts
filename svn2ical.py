#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2007 Brian Ray - http://kazavoo.com/blog/index.php?/archives/28-SVN-to-ICAL.html
#                    Kevin Deldycke <kevin@deldycke.com>
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
  Requirements:
    * python
    * python iCalendar
    * python cElementTree
    * svn

  Features:
    *
    *

  TODO:
    *
    *
    *
"""

################### Start of user config ###################

# Name of the iCalendar file
ICAL_FILE = "kev-commits.ics"

# SVN repository URL. Can be local or distant
SVN_REP = "file:///home/kevin/.svk/local"

# SVN revision range to consider.
COMMIT_RANGE = "0:HEAD"

# List of author id to take care of (leave blank to get all commits). Great if one person commit under multiple identities.
AUTHORS = ['kevin', 'kev']

# Number of minutes before the commit (= time when the iCal event will start)
TIME_SLOT = 5

#################### End of user config ####################
################ Do not modify code below ! ################

# TODO: delete unrequired dependencies
import random, sys
import cElementTree    as et
import mx.DateTime.ISO as mxdate
from os        import getcwdu, remove, system as run
from os.path   import abspath, exists
from commands  import getstatusoutput
from datetime  import datetime, timedelta
from icalendar import Calendar, Event, UTC


# Global variable store the list of found commands
global found_commands
found_commands = []

def checkCommand(command_list=None):
  """
    This method check that the command list are available on the system.
    Came from website-backup.py script: do not forget to update !
  """
  global found_commands
  # This method accept as parameter a string (to check only one command) or a list/tuple (to check several commands)
  if type(command_list) == type('a'):
    command_list = [command_list]
  if command_list != None and len(command_list) > 0:
    # Check that "which" command exist first
    command_list = ["which"] + command_list
    for command in command_list:
      # It is not required to check a found command twice
      if command not in found_commands:
        result = getstatusoutput("which %s" % command)
        if result[0] == 0:
          # The command to check exist
          found_commands.append(command)
          print " INFO - '%s' found at '%s'" % (command, result[1])
        else:
          print "FATAL - '%s' command not found on this system: it is required by this script !" % command
          sys.exit(1)


# Main part of the script
if __name__ == "__main__":

  # Stats variables
  commit_count = 0

  # Use script folder as temp folder
  work_dir = abspath(getcwdu())

  # Normalize path
  tmp_log_file = abspath("%s/full-log.xml" % work_dir)  # Temporary file to store the XML log
  ical_file = abspath("%s/%s" % (work_dir, ICAL_FILE))

  # Check that all commands are there
  checkCommand(['svn'])

  # Dump SVN full XML log
  svn_dump = """svn log --xml -r%s %s > "%s" """ % (COMMIT_RANGE, SVN_REP, tmp_log_file)
  print " INFO - Start SVN log dump (`%s`)" % svn_dump
  run(svn_dump)
  if not exists(tmp_log_file):
    print "FATAL - Log dump failed."
    sys.exit(1)

  # Parse XML log and get each commit
  log_entries = et.parse(tmp_log_file).getroot().getiterator("logentry")

  # Create a brand new calendar
  cal = Calendar()
  cal.add('prodid', '-//SVN2ICAL//kev.coolcavemen.com//')
  cal.add('version', '2.0')

  # Create a brand new iCal event for each commit
  for log_entry in log_entries:
    # Get some commit data
    revision = log_entry.attrib["revision"]
    author   = log_entry.findtext("author")

    # Filter commit by authors
    if len(AUTHORS) > 0 and author not in AUTHORS:
      print " INFO - Skip SVN r%s: author '%s' ignored." % (revision, author)
      continue

    # Get commit details
    date = mxdate.ParseAny(log_entry.findtext("date"))
    msg  = log_entry.findtext("msg")

    # Convert ISO date to python datetime object
    py_datetime = datetime( date.year
                          , date.month
                          , date.day
                          , date.hour
                          , date.minute
                          , date.second
                          , 0
                          , tzinfo=UTC
                          )
    # iCalendar events must be defined by a time slot with a start and a stop date/time.
    # There is no such equivalent in SVN: a commit has just a date.
    # I choose to use the commit date as the end of the iCal event. The start of the event will be set as the commit date minus 5 minutes.
    event_start = py_datetime - timedelta(minutes=TIME_SLOT)

    # Create a new calendar event
    event = Event()
    event.add('summary','SVN REV %s' % revision)
    event.add('description','%s:\n\n%s' % (author,msg))
    event.add('dtstart', event_start)
    event.add('dtend', py_datetime)
    event.add('dtstamp', event_start)
    event['uid'] = '%s-%s-%s-%s@kev.coolcavemen.com' % (revision, py_datetime, author, random.random())
    event.add('priority', 5)
    cal.add_component(event)
    commit_count += 1

  # Write the iCal file
  f = open(ical_file, "w")
  f.write(cal.as_string())
  f.close()

  # Clean-up and exit
  remove(tmp_log_file)
  print " INFO - Calendar created as '%s' with %s commits." % (ical_file, commit_count)
  sys.exit(0)

