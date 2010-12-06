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

"""
  TODO: Add recursivity
"""

import sys, os, md5
from commands import getstatusoutput
SEP = os.path.sep



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
  result = getstatusoutput("md5sum %s" % file_path)
  if result[0] == 0:
    file_checksum = result[1].split(' ')[0]
  # Proceed to next file if md5sum fail
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

  # Create the list of file's path to compare
  file_list = []
  if os.path.isdir(folder_path):
    for entry in os.listdir(folder_path):
      entry_path = ''.join([folder_path, SEP, entry])
      if os.path.isfile(entry_path):
        file_list.append(entry_path)
  else:
    print "'%s' doesn't exist or is not a directory." % folder_path
    sys.exit()

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

  # PURE PYTHON VERSION of MD5 calculation. This method is not used because it doesn't work on big files.
  ## Analyse each file
  #for file_to_hash in file_list:
    #file_content = getFileContent(file_to_hash)
    ## Can't open file: proceed to next one
    #if file_content == None:
      #continue
    ## Calculate the MD5 of the file
    #file_checksum = md5.new(file_content).digest()
    ## Save the file in the right place in the dict
    #if checksum_dict.has_key(file_checksum):
      #checksum_dict[file_checksum] = checksum_dict[file_checksum] + [file_to_hash]
    #else:
      #checksum_dict[file_checksum] = [file_to_hash]

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
