#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2006-2010 Kevin Deldycke <kevin@deldycke.com>
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

"""Usage : findDuplicates.py folder1 folder2 ...

** [folder1 folder2 ...]
      List of folders to check for duplicate files.
      Default: current folder.

** -h, --help
      Print this screen.
"""


import os
import sys
import getopt
import hashlib
from commands import getstatusoutput


def getFileContent(file_path):
  """
    This function get the content of a file
  """
  # Verify that the file exist
  if not os.path.isfile(file_path):
    print "ERROR: %s doesn't exist." % file_path
    return None
  # Get file content
  file_path = os.path.abspath(file_path)
  file_object = open(file_path, 'r')
  return file_object.read()


def getMD5(file_path):
  """
    Return the MD5 of a file 
  """
  file_checksum = None
  file_content = getFileContent(file_path)
  if file_content:
    try:
      file_checksum = hashlib.md5(file_content).hexdigest()
    except:
      # Use the system command line if Python's library fails, as sometimes it fails on big files.
      result = getstatusoutput("md5sum %s" % file_path)
      if result[0] == 0:
        file_checksum = result[1].split(' ')[0]
  return file_checksum


def main(argv=None):
  if argv is None:
    argv = sys.argv
  # Parse command line options
  try:
    opts, args = getopt.getopt(argv[1:], "h", ["help"])
  except getopt.error, msg:
    print msg
    print "For help use --help"
    return 2
  # Process options
  for o, a in opts:
    if o in ("-h", "--help"):
      print __doc__
      return 0
  # Process arguments
  folder_list = []
  for folder in args:
    folder_path = os.path.abspath(folder)
    if not os.path.isdir(folder_path):
      print "%s doesn't exist or is not a directory." % folder_path
      return 1
    folder_list.append(folder_path)
  # No folder defined, use current folder
  if not folder_list:
    folder_list.append(os.path.abspath(os.getcwd()))

  # Browse all folders and set the list of files to check
  files_to_check = []
  for folder_path in folder_list:
    for parent, dirs, files in os.walk(folder_path):
      for filename in files:
        filepath = os.path.join(parent, filename)
        if filepath not in files_to_check:
          files_to_check.append(filepath)

  # Compute checksums of all files
  checksum_dict = {}
  for filepath in files_to_check:
    checksum = getMD5(filepath)
    if not checksum:
      print "Can't compute checksum of %s" % filepath
      continue
    if checksum not in checksum_dict:
      checksum_dict[checksum] = []
    checksum_dict[checksum] = checksum_dict[checksum] + [filepath]

  # Show results
  no_duplicates = True
  for (checksum, files) in checksum_dict.items():
    if len(files) > 1:
      no_duplicates = False
      files.sort()
      print "Duplicate files:%s\n" % '\n  * '.join([''] + files)
  if no_duplicates:
    print "No duplicate files found in %r." % folder_list
  return 0


if __name__ == "__main__":
  sys.exit(main())

