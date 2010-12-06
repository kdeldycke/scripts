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
  print """Usage : findDuplicates folder

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
    output("ERROR: " + file_path + " doesn't exist.")
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
  if file_content != None:
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
    print "'%s' doesn't exist or is not a directory." % folder_path
    sys.exit()

  # Create the list of file's path to compare
  file_list = []
  for parent, dirs, files in os.walk(folder_path):
    for filename in files:
      file_list.append(os.path.join(parent, filename))

  # This dict will contain the list of files indexed by their md5 checksum
  checksum_dict = {}
  # Analyse each file
  for file_to_hash in file_list:
    # Get the checksum of the file
    file_checksum = getMD5(file_to_hash)
    # Proceed to next file if md5sum fail
    if file_checksum == None:
      continue
    # Save the file in the right place in the dict
    if checksum_dict.has_key(file_checksum):
      checksum_dict[file_checksum] = checksum_dict[file_checksum] + [file_to_hash]
    else:
      checksum_dict[file_checksum] = [file_to_hash]
  # Show results
  no_duplicates = True
  for (checksum, files) in checksum_dict.items():
    if len(files) > 1:
      if no_duplicates == True:
        print "Duplicate files found in %r." % folder_path
      no_duplicates = False
      file_name_list = []
      for file_path in files:
        file_name_list.append("%r" % os.path.basename(os.path.abspath(file_path)))
      print "Duplicate files: %s" % ' '.join(file_name_list)
  if no_duplicates:
    print "No duplicate files found in %r." % folder_path
