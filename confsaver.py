#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2004-2005 Kevin Deldycke <kevin@deldycke.com>
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
Improvements :

  * Use a --force -f option to automatically erase the user files

  * Make a --verbose -v option to reduce the printing

  * tar c dir/ | gzip | gpg -c | ssh user@remote 'dd of=dir.tar.gz.gpg'
    make encrypted archive of dir/ on remote machine

  * Take care of special encoded char in url like ", ', ?, [space], accents, /, \, and so on

  * Take care of owner/group/rights

  * Save the config_files list as a serialized object in a file with a special name
    --> this allow us to erase the entire directory if it already exist
    --> this is a good way to exclude a mess if the directory already exist
"""



import getopt, sys, os, tempfile, datetime
from commands import getstatusoutput
from os import system


# Get some environment variables
home_dir = os.path.abspath(os.getenv('HOME'))
temp_dir = home_dir
user_name = os.getenv('USER')

# Set default values of user parameters
complete_group_required = False
silent = False

# The structure of the list of elements to save in the archive look like this :
# congig_file = { 'First group name' : [('item type', 'item path')
#                                      ,('item type', 'item path')
#                                      ,('item type', 'item path')
#                                      ]
#               , 'Second group name' : [('item type', 'item path')
#                                       ,('item type', 'item path')
#                                       ,('item type', 'item path')
#                                       ]
#               }
# Directories and files path are given as relative, starting from the user home folder
# Types of items to save for a given group can be of 2 types :
#     'd' -> indicate an entire directory to save
#     'f' -> indicate a single file to save

config_files = { 'Kopete'             : [('f', '.kde/share/config/kopeterc')
                                        ,('d', '.kde/share/apps/kopete')
                                        ]
               , 'Kmail'              : [('f', '.kde/share/config/emailidentities')
                                        ,('f', '.kde/share/config/kmail.eventsrc')
                                        ,('f', '.kde/share/config/emaildefaults')
                                        ,('f', '.kde/share/config/kmailrc')
                                        ,('d', '.kde/share/apps/kmail/')
                                        ]
               , 'Mail boxes'         : [('d', '.Mail/')
                                        ]
               #, 'Knewsticker'        : [('f', '.kde/share/config/knewsticker_panelappletrc')
               #                         ,('f', '.kde/share/config/knewsticker.eventsrc')
               #                         ,('f', '.kde/share/config/knewsticker_appletrc')
               #                         ,('f', '.kde/share/config/knewstickerappletrc')
               #                         ,('f', '.kde/share/config/knewstickerrc')
               #                         ]
               , 'Skype'              : [('d', '.Skype/')
                                        ]
               , 'Gftp'               : [('d', '.gftp/')
                                        ]
               , 'Konqueror bookmark' : [('f', '.kde/share/apps/konqueror/bookmarks.xml')
                                        ]
               , 'Konqueror cookies'  : [('f', '.kde/share/config/kcookiejarrc')
                                        ,('d', '.kde/share/apps/kcookiejar/')
                                        ]
               , 'Akregator'          : [('f', '.kde/share/config/akregator.eventsrc')
                                        ,('f', '.kde/share/config/akregatorrc')
                                        ,('d', '.kde/share/apps/akregator/')
                                        ]
               }



def usage():
  print """Usage : confsaver [options]

** Saving options
    -s, --save
            Save the current desktop configuration to a file.
    -c, --complete
            Only save a group if all items exists.
    --nodate
            Don't include the current date to the archive name while saving.
    --nouser
            Don't include the current user login to the archive name while saving.

** Restoring options
    -r  file, --restore=FILE
            Restore the desktop configuration of the current user from the given file.
            WARNING : restoring will erase existing files without asking.

** General options
    --silent
            No informations will be printed on the standard output.
    -h, --help
            Show this screen.
"""



def output(string):
  if not silent:
    print string



def create_temp_folder():
  output("* Create a temporary folder...")
  temp_folder_path = tempfile.mkdtemp(prefix="confsaver-")
  temp_folder_path += '/'
  output("    Created : " + temp_folder_path)
  return temp_folder_path



def remove_temp_folder(temp_folder_path):
  # Remove temp files
  output("* Remove the temporary folder...")
  system("rm -rf " + temp_folder_path)
  output("    Removed : " + temp_folder_path)



def makeFolderReal(folder_path):
  # This function check that the path exist and create folders if needed
  if not os.path.exists(folder_path):
    os.makedirs(folder_path, 0755)



def save_config(use_date, use_user):

  # Create a temp folder
  temp_folder_path = create_temp_folder()

  # Save config
  for group in config_files.keys():
    output("* Save configuration of " + group + "...")

    # Check the existence of all items if it was asked by the user
    item_missing = False
    if complete_group_required:
      for item in config_files[group]:
        source_path = home_dir + '/' + item[1]
        if not os.path.exists(source_path):
          item_missing = True
          break

    # Copy the next item or skip the entire group according to user options
    if item_missing:
      output("    Skipped " + group + " group because of a missing item ("+ source_path +")")
    else:
      for item in config_files[group]:
        source_path = home_dir + '/' + item[1]
        if not os.path.exists(source_path):
          output("    Skipped (item not found) : " + source_path)
        else:
          if item[0] == 'd':
            path = item[1]
          else:
            path = '/'.join(item[1].split('/')[:-1])
          reduced_path = item[1].split('/')
          if reduced_path[-1] == '':
            reduced_path = reduced_path[:-1]
          reduced_path = '/'.join(reduced_path[:-1])
          if len(reduced_path) > 0:
            reduced_path += '/'
          system("mkdir -p " + temp_folder_path + path)
          system("cp -r " + source_path + ' ' + temp_folder_path + reduced_path)
          output("    Saved : " + source_path)

  # Make an archive
  archive_name = "confsave"
  if use_user == True:
    archive_name += "-" + user_name
  if use_date == True:
    date_element = datetime.date.today().timetuple()
    archive_name += "-%04d_%02d_%02d" % (date_element[0], date_element[1], date_element[2])
  archive_name += ".tar.bz2"
  # TODO: make sure the file "archive_name" doesn't exist
  output("* Create the archive " + archive_name + "...")
  archive_abs_path = os.path.abspath("./" + archive_name)
  system("tar c -C " + temp_folder_path[:-1] + " ./ | bzip2 > " + archive_abs_path)
  output("    Created : " + archive_abs_path)

  # Remove temp files
  remove_temp_folder(temp_folder_path)



def restore_config(archive):

  # Get the absolute path
  archive_abs_path = os.path.abspath(archive)

  # Create a temp folder
  temp_folder_path = create_temp_folder()

  # Extract files to temp folder
  archive_name = os.path.split(archive)[1]
  output("* Unpack configuration to temp folder...")
  system("bzip2 -dc " + archive_abs_path + " | tar x -C " + temp_folder_path)
  output("    Unpacked : " + archive_name)

  # TODO : get here the serialized object and save it to config_files

  # Restoring all groups
  for group in config_files.keys():
    output("* Restore files of " + group + " group...")

    # Check if the group is contain all suposed items
    group_is_complete = False
    items_number = 0
    for item in config_files[group]:
      source_path = temp_folder_path + item[1]
      if os.path.exists(source_path):
        items_number += 1

    # Skip the complete group or try to restore existing items
    if items_number == 0:
      output("    Skipped : no iems found")
    else:
      for item in config_files[group]:
        source_path = temp_folder_path + item[1]
        # Be sure the item exist in the archive
        if not os.path.exists(source_path):
          output("    Skipped (item not found) : " + source_path)
        else:
          # Erase the destination item to prevent conflicts
          item_full_path = home_dir + '/' + item[1]
          system("rm -rf " + item_full_path)
          output("    Removed : " + item_full_path)
          # Copy all files of the item to the home dir

          relative_path = item[1].split('/')[:-1]
          if item[0] == 'd':
            relative_path = relative_path[:-1]
          relative_path = '/'.join(relative_path)
          if len(relative_path) > 0:
            relative_path += '/'
          destination_folder = home_dir + '/' + relative_path
          # Before copying, make sure that intermediate folders exists
          makeFolderReal(destination_folder)
          system("mv " + source_path + ' ' + destination_folder)
          output("    Restored : " + item_full_path)

  # Remove temp files
  remove_temp_folder(temp_folder_path)



if __name__ == "__main__":

  # Get all parameters
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hscr:", ["help", "save", "complete", "silent", "nodate", "nouser", "restore="])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)

  # Get all user's options and define internal variables
  restore_file = None
  save_action = False
  use_date = True
  use_user = True
  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    if o in ("-s", "--save"):
      save_action = True
    if o in ("-c", "--complete"):
      complete_group_required = True
    if o in ("-r", "--restore"):
      restore_file = a
    if o == "--silent":
      silent = True
    if o == "--nodate":
      use_date = False
    if o == "--nouser":
      use_user = False

  # Check args number
  if len(opts) == 0:
    usage()
    sys.exit(2)

  # Format urls
  for group in config_files.keys():
    for item in config_files[group]:
      if item[0] == 'd' and item[1][-1] != '/':
        old_tuple = config_files[group][config_files[group].index(item)]
        new_tuple = (old_tuple[0], old_tuple[1] + '/')
        config_files[group].remove(old_tuple)
        config_files[group].append(new_tuple)
      elif item[0] == 'f' and item[1][-1] == '/':
        old_tuple = config_files[group][config_files[group].index(item)]
        new_tuple = (old_tuple[0], old_tuple[1][:-1])
        config_files[group].remove(old_tuple)
        config_files[group].append(new_tuple)

  # Do the right action
  if save_action == True:
    save_config(use_date, use_user)
  elif restore_file not in (None, ''):
    # TODO: verify here that the restore_file refer to a .tar.bz2 file type (use mime type python mudule ?)
    restore_config(restore_file)
