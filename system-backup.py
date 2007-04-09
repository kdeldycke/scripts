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
  Last update: 2007 apr 09
"""

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



import sys
from os       import makedirs, system
from os.path  import abspath, exists



def main():

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "'%s' does't exist !" % (BACKUP_DIR)
    sys.exit(0)

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
    #print mirror_cmd
    system(mirror_cmd)

    # Add an increments
    increment_cmd = """rdiff-backup --exclude-other-filesystems --force -v5 --restrict-read-only --print-statistics --exclude-sockets %s %s""" % (mirror_dir, increment_dir)
    #print increment_cmd
    system(increment_cmd)

    # Purge old increments
    purge_cmd = """rdiff-backup --force --remove-older-than 20B %s""" % increment_dir
    #print purge_cmd
    system(purge_cmd)


if __name__ == "__main__":
  main()
