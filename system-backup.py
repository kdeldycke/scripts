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
  Description:
    This script automate system backups thanks to rdiff-backup and rsync. It
    is based on an idea from the "Backup up on unreliable link" article
    ( http://wiki.rdiff-backup.org/wiki/index.php/BackupUpOnUnreliableLink )
    from the official rdiff-backup wiki ( http://wiki.rdiff-backup.org ).

  Last update: 2007 apr 27

  Requirements:
    * linux
    * python
    * rdiff-backup
    * rsync
    * ssh

  Features:
    * Keep last 20 backups.
    * Use rsync to make a local mirror of the remote machine (to speed-up backups and make them working over unreliable connection).

  TODO:
    * --preserve-numerical-ids (for rdiff-backup)
    * Do not create new increment if rsync didn't reached the remote host
    * nice -n 19 (do not take all ressources) ?
"""

################### Start of user config ###################


BACKUP_DIR = '/mnt/backup-disk'

backup_list = [
  { 'local_dir' : 'laptop-home'
  , 'remote_dir': '-z -e ssh root@192.168.1.2:/home/'
  },
  { 'local_dir' : 'laptop-main'
  , 'remote_dir': '-z -e ssh root@192.168.1.2:/'
  },
  { 'local_dir' : 'server-backup'
  , 'remote_dir': '/'
  },
]


#################### End of user config ####################
################ Do not modify code below ! ################

import sys
from os       import makedirs, remove, system, getpid
from os.path  import abspath, exists
from commands import getstatusoutput



def main():

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "FATAL - Main backup folder '%s' does't exist !" % BACKUP_DIR
    sys.exit(1)

  # Create a lock file to not run the script twice
  lock_file = abspath("%s/system-backup.lock" % BACKUP_DIR)
  if exists(lock_file):
    print "FATAL - Lock file found ! Another instance of this script is running or previous backup failed. Please investigate before removing '%s'." % lock_file
    sys.exit(1)
  # Write current pid as lock file
  f = open(lock_file, 'w')
  f.write(str(getpid()))
  f.close()

  # Strategy: mirror all machine first then make incremental storage.
  # This is mandatory because rdiff-backup operations take lots of time and we want to make the time slot during which all remote machines are accessed as short as possible.
  # That's why we create a list of system commands to run mirroring operations first.
  mirroring_commands = []
  increments_commands = []

  # Proceed each backup set
  for backup_item in backup_list:

    # Create local folder tree
    local_dir     = abspath("%s/%s" % (BACKUP_DIR, backup_item['local_dir']))
    mirror_dir    = abspath("%s/mirror" % local_dir)
    increment_dir = abspath("%s/incremental" % local_dir)
    for folder in [local_dir, mirror_dir, increment_dir]:
      if not exists(folder):
        makedirs(folder)

    # Mirror the remote directory
    mirror_cmd = """rsync -axHv --numeric-ids --partial --stats --delete --delete-excluded %s %s""" % (backup_item['remote_dir'], mirror_dir)
    mirroring_commands.append(mirror_cmd)

    # Check rdiff-backup consistency: if the previous rdiff-backup transaction fail (power failure, or reboot), rdiff-backup folder must be cleaned else we will not be able to add new increments
    result = getstatusoutput("""rdiff-backup -l "%s" """ % increment_dir)
    if result[1].find("--check-destination-dir") != -1:
      # Revert to previous increment
      roll_back = """rdiff-backup --check-destination-dir --force -v5 "%s" """ % increment_dir
      increments_commands.append(roll_back)

    # Add an increments
    increment_cmd = """rdiff-backup --exclude-device-files --force -v5 --restrict-read-only --print-statistics --exclude-sockets "%s" "%s" """ % (mirror_dir, increment_dir)
    increments_commands.append(increment_cmd)

    # Purge old increments
    purge_cmd = """rdiff-backup --force --remove-older-than 20B "%s" """ % increment_dir
    increments_commands.append(purge_cmd)

  # Run all system commands
  command_list = mirroring_commands + increments_commands
  for cmd in command_list:
    #print cmd
    system(cmd)

  # Backup successfull ! Remove lock file.
  remove(lock_file)


if __name__ == "__main__":
  main()
