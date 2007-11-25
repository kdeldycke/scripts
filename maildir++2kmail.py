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
  Last update:
    2007 nov 25

  Description:
    This script import a Maildir++ folder and its subfolders to Kmail local folder.
"""


#== User config ===============================================================

MAILDIR_SOURCE = "/home/kevin/Maildir"
KMAILDIR_DEST  = "/home/kevin/.kde/share/apps/kmail/mail"



#== Script core ===============================================================
from os import listdir
from shutil import copytree
from os.path import abspath, isdir

# Clean-up source and destination path
maildir_path  = abspath(MAILDIR_SOURCE)
kmaildir_path = abspath(KMAILDIR_DEST)

# Define folders that are part of maildir strandard structure
STD_MAILDIR = ['cur', 'new', 'tmp']

# Create the top folder where everything will be imported
IMPORT_FOLDER_NAME = "Maildir++ import"
import_folder      = kmaildir_path + "/"  + IMPORT_FOLDER_NAME
import_subfolder   = kmaildir_path + "/." + IMPORT_FOLDER_NAME + '.directory'

# Scan the maildir++ source folder
folders = listdir(maildir_path)
folders.sort()
folders.reverse()
for folder in folders:
  # Fix exotic filename encoding
  folder = folder.replace("&-", "&")
  # Calculate some folder properties
  folder_path = maildir_path + '/' + folder
  is_dir = isdir(folder_path)

  # The directory is part of the standard maildir structure, import it to kmail
  if folder in STD_MAILDIR and is_dir:
    f_dest = import_folder + "/" + folder
    print "IMPORT: %s -> %s" % (folder_path, f_dest)
    copytree(folder_path, f_dest)

  # The item is a valid maildir subfolder
  elif folder.startswith('.') and is_dir:
    # TODO: Should we check the existence of the "maildirfolder" file ?

    # Calculte the new kmail location of the subfolder
    new_path = []
    sub_folders = folder.split(".")
    for sub_folder in sub_folders[1:-1]:
      new_path.append("." + sub_folder + ".directory")
    new_path.append(sub_folders[-1])
    new_path = "/".join(new_path)

    # From each maildir++ subfolder, only import standard maildir folders, ignore everything else
    for f in listdir(folder_path):
      f_src = folder_path + "/" + f
      if f in STD_MAILDIR:
        f_dest = import_subfolder + '/' + new_path + '/' + f
        print "IMPORT: %s -> %s" % (f_src, f_dest)
        copytree(f_src, f_dest)
      else:
        print "SKIP: %s" % f_src

  # The item is not a mail subfolder, ignore it
  # This will catch files like "maildirfolder", "courierimap*"...
  else:
    print "SKIP: %s" % folder_path
