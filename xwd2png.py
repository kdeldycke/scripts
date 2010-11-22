#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2005 Kevin Deldycke <kevin@deldycke.com>
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
  Last update : 2005 oct 12
"""



import os, sys, glob, getopt
from commands import getstatusoutput



INPUT_FILE_PATTERN = '*.xwd'
OUTPUT_FILE_EXTENSION = '.png'
OUTPUT_PREFIX = 'img'
SHELL_COMMAND = 'convert'



def usage():
  print """Usage : batch.py [options]

** General options
    --dry
            Don't execute commands, but print them.
    --silent
            Don't output status messages on screen.
    -h, --help
            Show this screen.
"""



def main():
  # Get all parameters
  try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "dry", "silent"])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)

  # Get all user's options and define internal variables
  dry_run = False
  silent = False
  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    if o == "--dry":
      dry_run = True
    if o == "--silent":
      silent = True

  # Get the list of files
  current_folder_path = os.path.abspath('./')
  files = glob.glob(("%s/%s") % (current_folder_path, INPUT_FILE_PATTERN))
  if not files:
    sys.exit("No file to process.")
  input_file_list = []
  for file in files:
    if os.path.isfile(file):
      input_file_list.append(os.path.basename(file))

  # Sort the list of files
  input_file_list.sort()

  # Do the command for each file
  i = 0
  for input_file in input_file_list:
    # Create the shell command string
    command = "%s %s %s%s%s" % ( SHELL_COMMAND
                               , input_file
                               , OUTPUT_PREFIX
                               , str(i).zfill(4)
                               , OUTPUT_FILE_EXTENSION
                               )
    if not silent:
      print """Do "%s"...""" % (command)
    # Do the shell command
    if not dry_run:
      getstatusoutput(command)
    i += 1
    if not silent:
      print "Done."



if __name__ == "__main__":
  main()
