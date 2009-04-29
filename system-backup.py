#!/usr/bin/python
# -*- coding: UTF-8 -*-

##############################################################################
#
# Copyright (C) 2007-2009 Kevin Deldycke <kevin@deldycke.com>
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
    published on the official rdiff-backup wiki ( http://wiki.rdiff-backup.org ).

  Last update: 2009 apr 29

  Requirements:
    * linux
    * python >= 2.4
    * rdiff-backup >= 1.1.0
    * rsync >= 2.6.7
    * ssh
    * ps

  Features:
    * Use rsync to make a local mirror of the remote machine (to speed-up backups and make them working over unreliable connection)
    * Auto-clean rdiff-backup repository
    * Lock mechanism to not run this script twice
    * Auto-kill the script if the backup process take to much time
    * New increment will not be created if rsync didn't reached the remote host

  Advices:
    * Run this script regularly via to a cron entry, e.g.: `0 13 * * * root /root/system-backup.py >> /mnt/backup-disk/backup.log`
    * Modify BACKUP_TIMEOUT constant according your cron job frequency
    * Use rsa-key/certificate-based authentication to access remote machine via SSH

  TODO:
    * nice -n 19 (do not take all ressources) ?
    * use logger module instead of printing in the wild...
    * How can I do to not run command in shell ? is it make sense ?
    * auto kill after XX hours of running (use a timer).
"""


################### Start of user config ###################


# Main backup folder where all backups defined in the 'backup_list' are stored
BACKUP_DIR = '/mnt/backup-disk'

# Number of increments to keep
INCREMENTS_TO_KEEP = 15

# 47 hours = 2 days minus one hour
BACKUP_TIMEOUT = 47 * 60 * 60

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

import atexit
import pickle
import signal
from os         import makedirs, remove, getpid, kill, waitpid
from os.path    import abspath, exists
from sys        import exit
from time       import time as now
from commands   import getstatusoutput
from subprocess import STDOUT, PIPE, Popen

# Global constant
LOCK_FILE = abspath("%s/system-backup.lock" % BACKUP_DIR)


def run(cmd, quiet=False, update_lock_file=True):
  """
    Generic method to run a linux command and register all its child processes in the lock file.
    Lock file updates can be bypassed using the update_lock_file flag.
  """
  if not quiet:
    print "DEBUG - Run `%s`..." % cmd
  # Run command as a child in a shell environment, else rdiff-backup and rsync will fail
  child = Popen( cmd
               , shell     = True
               , env       = {"LANGUAGE": "en"}
               , stdin     = PIPE
               , stdout    = PIPE
               , stderr    = STDOUT
               , close_fds = True
               )
  (child_input, child_output) = (child.stdin, child.stdout)
  # Register child in the lock file
  if update_lock_file:
    updateLockFile()
  # Wait for the child end
  exit_code = waitpid(child.pid, 0)[1]
  if not quiet and exit_code != 0:
    print "ERROR - Command `%s` failed !" % cmd
  # Unregister child from the lock file
  if update_lock_file:
    updateLockFile()
  # Return something similar to commands.getstatusoutput() method
  return (exit_code, child_output.read())


def updateLockFile():
  """
    Generic method to update and save lock file content with start time, process
      list and related info.
    By default the current list of child processes is updated and the start time
      info from the current lock file is not modifed. But if this method is called
      and no lock file is found, this method automaticaly swith from an "update"
      mode to a "create" mode and use current time to init the start time value.
  """
  # Detect in which mode this method must operate (create or update)
  create_mode = True
  if exists(LOCK_FILE):
    create_mode = False
  # Initialize the dict which will be pickled and which contain all infos
  lock_data = { 'start_time'  : 0
              , 'process_list': {}
              }
  # Init start time value to now in "create" mode
  if create_mode:
    lock_data['start_time'] = now()
    # XXX isn't it better to use "ps" and output format option "etime" to know for how long the script is running ?
    # As said in the manual: etime = elapsed time since the process was started, in the form [[dd-]hh:]mm:ss."
  # Keep the previous start time value in "update" mode
  else:
    lock_data['start_time'] = getDataFromLockFile()['start_time']
  # Get the detailed list of running child
  lock_data['process_list'] = getProcessList()
  # Update the lock file content
  try:
    f = open(LOCK_FILE, 'w')
    pickle.dump(lock_data, f)
    f.close()
  except IOError:
    print "FATAL - Can't create lock file !"
    exit(1)
  # Print end message
  if create_mode:
    print "INFO  - Lock file created as '%s'." % LOCK_FILE
  else:
    print "INFO  - Lock file updated."


def getDataFromLockFile():
  """
    Generic method to get start time and pid list from lock file.
  """
  try:
    f = open(LOCK_FILE, 'r')
    lock_data = pickle.load(f)
    f.close()
  except IOError:
    print "FATAL - Can't open lock file !"
    exit(1)
  except IndexError:
    print "FATAL - Can't read lock file content !"
    exit(1)
  return lock_data


def removeLockFile():
  """
    Generic method to remove the lock file.
  """
  try:
    remove(LOCK_FILE)
  except IOError:
    print "FATAL - Can't remove lock file !"
    exit(1)
  print "INFO  - Lock file removed."


def getProcessChildren(parent_pid):
  """
    This function use the "ps" linux command to get children info
      (pid and command) of a given process.
  """
  children = {}
  get_children_cmd = "ps --no-headers --ppid %d -o pid,command" % parent_pid  # Get pid and command info only
  (exit_code, cmd_output) = run(get_children_cmd, quiet=True, update_lock_file=False) # No lock file update else we will face infinite recursion...
  if exit_code not in (0, 256):  # 0 mean that "ps" return something, 256 mean "ps" didn't find any child
    # Command fail for unknown reason
    print "FATAL - Command `%s` failed with %d exit code !" % (get_children_cmd, exit_code)
    exit(1)
  # Parse "ps" output to extract child pids and commands
  for child_info in cmd_output.split('\n'):
    child_info_list = child_info.strip().split(' ', 1)
    if len(child_info_list) == 2:
      child_pid = int(child_info_list[0])
      child_cmd = child_info_list[1]
      children[child_pid] = child_cmd
  return children


def getRecursiveProcessChildren(parent_pid):
  """
    This method get all children, grand-children and all other sub-children
      of a given process and return a flat list of all the "sub-family".
  """
  children = getProcessChildren(parent_pid)
  for (child_pid, child_cmd) in children.items():
    children.update(getRecursiveProcessChildren(child_pid))
  return children


def getProcessList():
   """
     This method is the same as getRecursiveProcessChildren() but use current
       script as parent process and add it to the list.
   """
   # Get current script pid and its child processes
   script_pid = getpid()
   children = getRecursiveProcessChildren(parent_pid=script_pid)
   # Get the command used to launch current script
   get_script_cmd = "ps --no-headers --pid %d -o command" % script_pid
   (exit_code, cmd_output) = run(get_script_cmd, quiet=True, update_lock_file=False) # No lock file update else we will face infinite recursion...
   # Add current script process details to its child list
   script_cmd = cmd_output.split('\n')[0].strip().split(' ', 1)[1]
   children.update({script_pid: script_cmd})
   return children


def main():
  """
    Core of the backup script...
  """

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "FATAL - Main backup folder '%s' is not reachable ! Create it by hand or check access rights." % BACKUP_DIR
    exit(1)

  # Check existence of previous lock file
  if exists(LOCK_FILE):
    print "WARNING - Lock file found !"
    lock_data = getDataFromLockFile()
    start     = lock_data['start_time']
    pid_list  = lock_data['process_list']

    # Kill previous instance of the backup process if it's older than the backup timeout
    if (now() - float(start)) > BACKUP_TIMEOUT:
      print "INFO  - Timeout reached: previous instance of this script was started %s hours ago." % (float(BACKUP_TIMEOUT) / 3600)
      # Kill the parent process and all its remaining children
      old_instance_running = False
      for (pid, pcmd) in pid_list.items():
        try:
          # TODO: check here that the process is our (use "pcmd" to compare with current process')
          kill(int(pid), signal.SIGKILL)
          old_instance_running = True
        except:
          # If kill() failed it mean that the process is already dead
          pass
      if old_instance_running:
        print "INFO  - Previous running instance found and killed !"
      else:
        print "INFO  - No running instance found."

      # We can remove previous lock file safely
      removeLockFile()

    # No timeout reached: do not disturb running instance
    else:
      print "FATAL - Another instance seems to be running. Please investigate before considering the removal of '%s'." % LOCK_FILE
      exit(1)

  # Init and create the lock file
  updateLockFile()

  # Register signal handler to automatically remove the lock file if the script is stopped
  def atSIGTERM(signum, frame):
    removeLockFile()
    exit(0)
  atexit.register(lambda: exit(0))
  signal.signal(signal.SIGTERM, atSIGTERM)

  # Backup strategy: mirror all machines first then make incremental storage.
  # This strategy lower the "exposure" of external machines to this script, by running rsync operations first then rdiff-backup ones.
  command_list = []

  # Proceed each backup set
  for backup_item in backup_list:

    # Create local folder tree
    local_dir     = abspath("%s/%s" % (BACKUP_DIR, backup_item['local_dir']))
    mirror_dir    = abspath("%s/mirror" % local_dir)
    increment_dir = abspath("%s/incremental" % local_dir)
    for folder in [local_dir, mirror_dir, increment_dir]:
      if not exists(folder):
        makedirs(folder)

    # TODO: detect here if the parameter is a local or a remote directory. Then, if the things to backup is a directory and the path doesn't end with a "/" add one.

    # Mirror the remote directory
    mirror_cmd = """rsync -axHhhv --numeric-ids --partial --stats --delete --delete-before %s %s """ % (backup_item['remote_dir'], mirror_dir)
    command_list.append(mirror_cmd)

    # Check rdiff-backup consistency: if the previous rdiff-backup transaction has failed (power failure, or reboot), rdiff-backup folder must be cleaned up else new increments can't be added
    check_consistency_cmd = """rdiff-backup -l "%s" """ % increment_dir
    (exit_code, cmd_output) = run(check_consistency_cmd)
    # Auto clean the repository if necessary
    # Case 1: remove inconsistent last increment
    if cmd_output.find("--check-destination-dir") != -1:
      roll_back_cmd = """rdiff-backup --check-destination-dir --force -v5 "%s" """ % increment_dir
      command_list.append(roll_back_cmd)
    # Case 2: repository is in a very bad shape, the only solution is to delete the rdiff-backup-data directory
    elif cmd_output.find("Fatal Error: Bad rdiff-backup-data dir on destination side") != -1:
      reset_repository_cmd = """rm -rf "%s" """ % abspath("%s/rdiff-backup-data" % increment_dir)
      command_list.append(reset_repository_cmd)

    # Purge old increments first to free space
    purge_cmd = """rdiff-backup --force --remove-older-than %dB "%s" """ % (INCREMENTS_TO_KEEP, increment_dir)
    command_list.append(purge_cmd)

    # Add an increment
    add_increment_cmd = """rdiff-backup --exclude-device-files --force -v5 --preserve-numerical-ids --restrict-read-only --print-statistics --exclude-sockets "%s" "%s" """ % (mirror_dir, increment_dir)
    command_list.append(add_increment_cmd)

  # Run all system commands
  for cmd in command_list:
    run(cmd)

  # Backup successfull ! Remove lock file.
  removeLockFile()


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    exit(0)
