#!/usr/bin/python

"""
Last update : 2004 dec 05

Improvements :

  * tar c dir/ | gzip | gpg -c | ssh user@remote 'dd of=dir.tar.gz.gpg'
    make encrypted archive of dir/ on remote machine

  * Take care of special encoded char in url like ", ', ?, [space], accents, /, \, and so on
    
  * Take care of owner/group/rights

  * Save the config_files list as a serialized object in a file with a special name
    --> this allow us to erase the entire directory if it already exist
    --> this is a good way to exclude a mess if the directory already exist
"""



import getopt, sys, os, tempfile, random, datetime
from commands import getstatusoutput
from os import system


# Get some environment variables
home_dir = os.path.abspath(os.getenv('HOME'))
temp_dir = home_dir
user_name = os.getenv('USER')


# 'd' indicate an entire directory to save, 'f' just a file to save
config_files = { 'Kopete': [('d', '.kde/share/apps/kopete')
                           ,('f', '.kde/share/config/kopeterc')
                           ]
               , 'Kmail' : [('d', '.kde/share/apps/kmail/')
                           ,('f', '.kde/share/config/kmailrc')
                           ]
               , 'Mail boxes'  : [('d', '.Mail/')
                           ]
               , 'Konqueror bookmark': [('f', '.kde/share/apps/konqueror/bookmarks.xml')
                                 ]
               }



def usage():
  print """Usage : confsaver [options]
Options :
    -r  file, --restore=FILE
            Restore the desktop configuration of the current user from the given file.
            WARNING : restoring will erase existing files without asking.
    -s, --save
            Save the current desktop configuration to a file.
    --nodate
            Don't include the current date to the archive name while saving.
    -h, --help
            Show this screen.
"""
  return



def create_temp_folder():

  print "* Create a temporary folder..."
  temp_folder_path = tempfile.mkdtemp(prefix="confsaver-")
  print "    Created : " + temp_folder_path + "/"
  return temp_folder_path



def remove_temp_folder(temp_folder_path):
  return
  # Remove temp files
  print "* Remove the temporary folder..."
  system("rm -rf " + temp_folder_path)
  print "    Removed : " + temp_folder_path + "/"



def save_config(use_date, use_user):

  # Create a temp folder
  temp_folder_path = create_temp_folder()

  # Save config
  for item in config_files.keys():
    print "* Save configuration of " + item + "..."
    for element in config_files[item]:
      if element[0] == 'd':
        path = element[1]
      else:
        path = '/'.join(element[1].split('/')[:-1])
      system("mkdir -p " + temp_folder_path + '/' + path)
      reduced_path = element[1].split('/')
      if reduced_path[-1] == '':
        reduced_path = reduced_path[:-1]
      reduced_path = '/'.join(reduced_path[:-1])
      if len(reduced_path) > 0:
        reduced_path += '/'
      source_path = home_dir + '/' + element[1]
      # TODO: manage the case of inexisting source_path
      system("cp -r " + source_path + ' ' + temp_folder_path + '/' + reduced_path)
      print "    Saved : " + source_path

  # Make an archive
  archive_name = "confsave"
  if use_user == True:
    archive_name += "-" + user_name
  if use_date == True:
    date_element = datetime.date.today().timetuple()
    # TODO: set month and day to 2-digit format
    archive_name += "-" + str(date_element[0]) + "_" + str(date_element[1]) + "_" + str(date_element[2])
  archive_name += ".tar.bz2"
  # TODO: make sure the file "archive_name" doesn't exist
  print "* Create the archive " + archive_name + "..."
  archive_abs_path = os.path.abspath("./" + archive_name)
  system("tar c -C " + temp_folder_path + " ./ | bzip2 > " + archive_abs_path)
  print "    Created : " + archive_abs_path

  # Remove temp files
  remove_temp_folder(temp_folder_path)



def restore_config(archive):

  # Get the absolute path
  archive_abs_path = os.path.abspath(archive)

  # Create a temp folder
  temp_folder_path = create_temp_folder()

  # Extract files to temp folder
  archive_name = os.path.split(archive)[1]
  print "* Unpack configuration to temp folder..."
  system("bzip2 -dc " + archive_abs_path + " | tar x -C " + temp_folder_path + "/")
  print "    Unpacked : " + archive_name

  # TODO : get here the serialized object and save it to config_files

  # Restoring all the configuration files
  for item in config_files.keys():
    print "* Restore current user's files and folders of " + item + " configuration..."
    for element in config_files[item]:

      # Erase the every destination file or directory to prevent conflict
      to_remove = home_dir + '/' + element[1]
      system("rm -rf " + to_remove)
      print "    Removed : " + to_remove

      # Copy all configuration file to the home dir
      # TODO: before copying, make sure that 'intermediate' folders exists
      relative_path = element[1].split('/')[:-1]
      if element[0] == 'd':
        relative_path = relative_path[:-1]
      relative_path = '/'.join(relative_path)
      system("mv " + temp_folder_path + '/' + element[1] + ' ' + home_dir + '/' + relative_path + '/')
      print "    Restored : " + element[1]

  # Remove temp files
  remove_temp_folder(temp_folder_path)



if __name__ == "__main__":

  # Get all parameters
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hsr:", ["help", "save", "nodate", "nouser", "restore="])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)

  # Set the output file
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
    if o in ("-r", "--restore"):
      restore_file = a
    if o in ("--nodate"):
      use_date = False
    if o in ("--nouser"):
      use_user = False

  # Check args number
  if len(opts) == 0:
    usage()
    sys.exit(2)

  # Format urls
  for item in config_files.keys():
    for element in config_files[item]:
      if element[0] == 'd' and element[1][-1] != '/':
        old_tuple = config_files[item][config_files[item].index(element)]
        new_tuple = (old_tuple[0], old_tuple[1] + '/')
        config_files[item].remove(old_tuple)
        config_files[item].append(new_tuple)
      elif element[0] == 'f' and element[1][-1] == '/':
        old_tuple = config_files[item][config_files[item].index(element)]
        new_tuple = (old_tuple[0], old_tuple[1][:-1])
        config_files[item].remove(old_tuple)
        config_files[item].append(new_tuple)

  # Do the right action
  if save_action == True:
    save_config(use_date, use_user)
  elif restore_file != None:
    restore_config(restore_file)
