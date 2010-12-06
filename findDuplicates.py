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


import sys, os, hashlib
from commands import getstatusoutput


def usage():
  print """Usage : findDuplicates.py folder

** [folder]
      Folder that contain files to check.
      Default: current folder.
"""


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


if __name__ == "__main__":
  # Get the folder where files to compare are located
  param_list = sys.argv[1:]
  folder_path = None
  if len(param_list) != 1:
    # No folder defined, use current folder
    folder_path = os.path.abspath(os.getcwd())
  else:
    folder_path = os.path.abspath(param_list[0])
  if not os.path.isdir(folder_path):
    print "%s doesn't exist or is not a directory." % folder_path
    sys.exit()

  # Browse folder sub-structure and compute checksums of all files
  checksum_dict = {}
  for parent, dirs, files in os.walk(folder_path):
    for filename in files:
      filepath = os.path.join(parent, filename)
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
    print "No duplicate files found in %r." % folder_path
  sys.exit(0)

