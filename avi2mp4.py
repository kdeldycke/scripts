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
  Last update: 2006 apr 09
"""



import os, sys, glob, getopt
from commands import getstatusoutput



INPUT_FILE_PATTERN = '*.avi'
OUTPUT_FILE_EXTENSION = '.mp4'



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

  # Get the list of files to encode
  current_folder_path = os.path.abspath('./')
  files = glob.glob(("%s/%s") % (current_folder_path, INPUT_FILE_PATTERN))
  if not files:
    sys.exit("No file to process.")
  input_file_list = []
  for file in files:
    if os.path.isfile(file):
      input_file_list.append(os.path.basename(file))

  # Do the command for each file
  for input_file in input_file_list:
    input_file_elements = input_file.split('.')
    output_file = '.'.join(input_file_elements[:-1]) + OUTPUT_FILE_EXTENSION
    # Create the shell command string
    command = "vlc --sout-all \"%s\" :sout='#transcode{vcodec=h264,acodec=mp3,ab=32,channels=1,audio-sync}:std{access=file,mux=mp4,url=\"%s\"}' vlc:quit -I dummy" % (input_file, output_file)
    if not silent:
      print """Do "%s"...""" % (command)
    # Do the shell command
    if not dry_run:
      getstatusoutput(command)
    if not silent:
      print "Done."



if __name__ == "__main__":
  main()
