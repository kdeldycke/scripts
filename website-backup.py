#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2006-2007 Kevin Deldycke <kev@coolcavemen.com>
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
  Last update: 2007 mar 25

  Requirements:
    * linux
    * python (+ pexpect lib)
    * lftp
    * tar
    * bzip2
    * rdiff-backup
    * rsync
    * ssh

  Features:
    * Port number are optional if you use default one (22 for SSH; 21 for FTP).
    * Auto detection of password-less SSH instance. This let you store password in SSH.

  Backup Type:
    * FTP
    * FTPs
    * SSH
    * MySQLdump
    * MySQLdump+ssh

  TODO:
    * Rewrite code with classes, exceptions and object-oriented approach (this should lead to more pluggable code).
    * Use a generic multi-level log mechanism.
    * Send backup reports and errors by mail.
    * Clean-up the code. It's too messy !
"""

################### Start of user config ###################

BACKUP_DIR = '/mnt/external_enclosure/backup'

backup_list = [
### FTP examples
  { 'title'     : 'Simple FTP backup'
  , 'type'      : 'FTP'
  , 'host'      : 'ftp.website.com'
  , 'remote_dir': '/var/www/html'
  , 'user'      : '<user>'
  , 'password'  : '<password>'
  , 'local_dir' : 'website'
  },
  { 'title'     : 'Simple FTP backup with exotic port'
  , 'type'      : 'FTP'
  , 'host'      : 'ftp2.website.com'
  , 'port'      : '2100'  # Example with exotic FTP port
  , 'remote_dir': '/kevin/htdocs'
  , 'user'      : '<user>'
  , 'password'  : '<password>'
  , 'local_dir' : 'kevin'
  },

### FTPs examples
  { 'title'     : 'Simple FTPs (aka FTP over SSL) backup'
  , 'type'      : 'FTPs'
  , 'host'      : 'ftp.example.com'
  , 'remote_dir': '/kevin/htdocs'
  , 'user'      : '<user>'
  , 'password'  : '<password>'
  , 'local_dir' : 'ftps-test'
  },

### SSH examples
  { 'title'     : 'Simple SSH backup with password and exotic port'
  , 'type'      : 'ssh'
  , 'host'      : 'test.com'
  , 'port'      : '2200'
  , 'remote_dir': '~/public_html'
  , 'user'      : '<user>'
  , 'password'  : '<password>'
  , 'local_dir' : 'ssh+password-test'
  },
  { 'title'     : 'Password-less SSH backup'
  , 'type'      : 'SSH'
  , 'host'      : 'test.com'
  , 'remote_dir': '/var/lib/www/test'
  , 'user'      : '<user>'
  , 'local_dir' : 'ssh-nopassord-test'
  },

### MySQL examples
  { 'title'     : 'MySQL dump over SSH of a particular database with password'
  , 'type'      : 'mysqldump+ssh'
  , 'host'      : 'example.com'
  , 'user'      : '<user>'
  , 'password'  : '<ssh-password>'
  , 'db_user'   : 'mysqlxxxx'
  , 'db_pass'   : '<mysql-password>'
  , 'db_host'   : 'localhost'
  , 'db_name'   : 'mysqlxxxx'
  , 'local_dir' : 'mysqldump+ssh-test'
  },
  { 'title'     : 'MySQL dump over password-less SSH of all databases'
  , 'type'      : 'mysqldump+ssh'
  , 'host'      : 'example.com'
  , 'user'      : '<user>'
  , 'db_user'   : 'mysqlxxxx'
  , 'db_pass'   : '<mysql-password>'
  , 'db_host'   : 'localhost'
  , 'local_dir' : 'mysqldump+ssh-test'
  },
  { 'title'     : 'Direct MySQL dump with exotic MySQL server port'
  , 'type'      : 'mysqldump'
  , 'db_user'   : 'root'
  , 'db_pass'   : '<mysql-password>'
  , 'db_host'   : 'sql.machine.com'
  , 'db_port'   : 9999
  , 'local_dir' : 'mysqldump-test'
  },
]



#################### End of user config ####################
################ Do not modify code below ! ################

import sys, datetime, getopt, time
from commands import getstatusoutput
from urllib   import quote      as q
from urllib   import quote_plus as qp
from os       import makedirs, mkdir, remove, system, rmdir
from os.path  import abspath, exists, isfile, sep
from os.path  import split as pathsplit

# Define constants
SEP              = sep
TIMEOUT          = 15
SQL_FILENAME     = 'mysql-backup.sql'
BACKUP_TYPE_LIST = [ 'FTP'
                   , 'FTPS'
                   , 'SSH'
                   , 'MYSQLDUMP'
                   , 'MYSQLDUMP+SSH'
                   ]



def run(cmd, debug=False):
  """
    Run system command and print debug message if require.
  """
  LANGUAGE = "en"
  # Show "live" command output in debug mode
  command_name = pathsplit(abspath(cmd.strip().split(' ')[0]))[1]
  command = "env LANGUAGE=%s %s" % (LANGUAGE, cmd)
  if debug:
    print "DEBUG - Run `%s`..." % command
  # Debug mode or not, we print a nice formatted output of the command
  result = getstatusoutput(command)
  nice_log(log=result[1], cmd_name=command_name)


def nice_log(log, cmd_name, level="INFO"):
  """
    This method print nicely formatted command output.
  """
  PREFIX   = "%5s - " % level
  PREFIX_2 = ' ' * len(PREFIX)
  print "%s%s output:\n%s%s" % (PREFIX, cmd_name, PREFIX_2, log.replace('\n', "\n%s" % PREFIX_2))


# Global variable store the list of found commands
global found_commands
found_commands = []

def checkCommand(command_list=None):
  """
    This method check that the command list are available on the system.
  """
  global found_commands
  # This method accept as parameter a string (to check only one command) or a list/tuple (to check several commands)
  if type(command_list) == type('a'):
    command_list = [command_list]
  if command_list != None and len(command_list) > 0:
    # Check that "which" command exist first
    command_list = ["which"] + command_list
    for command in command_list:
      # It is not required to check a found command twice
      if command not in found_commands:
        result = getstatusoutput("which %s" % command)
        if result[0] == 0:
          # The command to check exist
          found_commands.append(command)
          print " INFO - '%s' found at '%s'" % (command, result[1])
        else:
          print "FATAL - '%s' command not found on this system: it is required by this script !" % command
          sys.exit(1)



def main(d=False):
  """
    Core of the backup script which implement the backup strategy.
  """

  def isSSHPasswordLess(host, user=None):
    """
      This method test if a ssh authentification on a remote machine can be done via a
      rsa-key/certificate or require a password.
    """
    # If no user given try "user-less" connection
    user_string = ''
    if user not in (None, '') and len(user) > 0:
      user_string = "%s@" % user
    TEST_STRING = "SSH KEY AUTH OK"
    test_cmd = """ssh %s%s "echo '%s'" """ % (user_string, host, TEST_STRING)
    if d:
      print "DEBUG - run `%s`..." % test_cmd
    ssh = pexpect.spawn(test_cmd, timeout=TIMEOUT)
    time.sleep(1)
    if d:
      import StringIO
      ssh_log = StringIO.StringIO()
      ssh.setlog(ssh_log)
    ret_code = ssh.expect([TEST_STRING, '.ssword:*', pexpect.EOF, pexpect.TIMEOUT])
    time.sleep(1)
    password_less = None
    if ret_code == 0:
      password_less = True
    elif ret_code == 1:
      password_less = False
    else:
      print "ERROR - SSH server '%s' is unreachable" % host
    if d:
      nice_log(ssh_log.getvalue(), 'ssh', level="DEBUG")
      ssh_log.close()
    ssh.close()
    if password_less:
      print " INFO - SSH connection to '%s' is password-less" % host
    else:
      print " INFO - SSH connection to '%s' require password" % host

    return password_less


  ######################
  # Self checking phase
  ######################

  # Announce the first phase
  print "=" * 40
  print "Backup script self-checking phase"
  print "=" * 40

  # Check that we are running this script on a UNIX system
  from os import name as os_name
  if os_name != 'posix':
    print "FATAL - This script can be run on POSIX systems only"
    sys.exit(1)

  # Check that every command is installed
  checkCommand(['rdiff-backup', 'rm', 'tar', 'bzip2'])

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "FATAL - Main backup folder '%s' does't exist !" % BACKUP_DIR
    sys.exit(1)

  # This variable indicate if pexpect module is required or not
  is_pexpect_required = False

  # Check datas and requirement for each backup
  # Doing this right now is nicer to the user: thanks to this he doesn't need to wait the end of the (X)th backup to get the error about the (X+1)th
  for backup in backup_list:
    # Calculate backup type
    backup_type = backup['type'].lower().strip()
    if backup_type.find('ftps') != -1:
      backup_type = 'FTPS'
    elif backup_type.find('ftp') != -1:
      backup_type = 'FTP'
    elif backup_type == 'ssh':
      backup_type = 'SSH'
    elif backup_type.find('mysql') != -1:
      if backup_type.find('ssh') != -1:
        backup_type = 'MYSQLDUMP+SSH'
      else:
        backup_type = 'MYSQLDUMP'
    else:
      print "ERROR - Backup type '%s' for '%s' is unrecognized." % (backup['type'], title)
      # Reset backup type
      backup['type'] = ''
      continue
    backup['type'] = backup_type
    # Check if pexpect is required
    if backup_type.find('SSH') != -1:
      is_pexpect_required = True
    # Check requirements
    REQUIRED_COMMANDS = { 'FTP'          : 'lftp'
                        , 'FTPS'         : 'lftp'
                        , 'SSH'          : ['rsync', 'ssh']
                        , 'MYSQLDUMP'    : 'mysqldump'
                        , 'MYSQLDUMP+SSH': 'ssh' # TODO: How to check that 'mysqldump' is present on the distant machine ???
                        }
    checkCommand(REQUIRED_COMMANDS[backup_type])
    # Add default port if missing
    DEFAULT_PORT = { 'FTP'          : {'port': 21}
                   , 'FTPS'         : {'port': 21}
                   , 'SSH'          : {'port': 22}
                   , 'MYSQLDUMP'    : {'db_port': 3306}
                   , 'MYSQLDUMP+SSH': {'port': 22, 'db_port': 3306}
                   }
    if backup_type in DEFAULT_PORT.keys():
      for (port_type, port_number) in DEFAULT_PORT[backup_type].items():
        if (not backup.has_key(port_type)) or len(backup[port_type]) == 0:
          backup[port_type] = port_number

  # Import pexpect if necessary
  if is_pexpect_required:
    try:
      import pexpect
    except ImportError:
      print "FATAL - pexpect python module not found: It is required to make backup over SSH !"
      sys.exit(1)


  ######################
  # Proceed each backup
  ######################

  for backup in backup_list:

    # Announce the backup item
    title = backup['title']
    print ""
    print "=" * 40
    print "Backup item: %s" % title
    print "=" * 40

    # Create backup folder structure if needed
    main_folder = abspath(SEP.join([BACKUP_DIR, backup['local_dir']]))
    backup_folders = {
        'main'    : main_folder
      , 'archives': abspath(SEP.join([main_folder, 'monthly-archives']))  # Contain monthly archives
      , 'diff'    : abspath(SEP.join([main_folder, 'rdiff-repository']))  # Contain current month diferential backup
      , 'mirror'  : abspath(SEP.join([main_folder, 'mirror']))            # Contain a mirror of the remote folder
      }
    for (folder_type, folder_path) in backup_folders.items():
      if not exists(folder_path):
        makedirs(folder_path)
        print " INFO - '%s' folder created" % folder_path


    ##########
    # Step 1 - Mirror data with the right tool
    ##########

    ### Start of this step
    backup_type = backup['type']
    print " INFO - Start mirroring via %s method" % backup_type

    ### Mirror remote data via FTP or FTPS
    if backup_type in ['FTP', 'FTPS']:
      # Generate FTP url
      remote_url = "ftp://%s:%s@%s:%s/%s" % ( qp(backup['user'])
                                            , qp(backup['password'])
                                            , qp(backup['host'])
                                            , backup['port']
                                            , q(backup['remote_dir'])
                                            )
      # Force SSL layer for secure FTP
      secure_options = ''
      if backup_type == 'FTPS':
        secure_options = 'set ftp:ssl-force true && set ftp:ssl-protect-data true && '
      # Get a copy of the remote directory
      ftp_backup = """lftp -c '%sset ftp:list-options -a && open -e "mirror -e --verbose=3 --parallel=2 . %s" %s'""" % (secure_options, backup_folders['mirror'], remote_url)
      run(ftp_backup, d)


    ### Mirror remote data via SSH
    elif backup_type == 'SSH':

      ## Test SSH password-less connection
      password_less = isSSHPasswordLess(backup['host'], backup['user'])
      if password_less == None:
        print "ERROR - Can't guess authentication method of '%s'" % backup['host']
        continue
      if not password_less and not (backup.has_key('password') and len(backup['password']) > 0):
        print "ERROR - No password provided !"
        continue
      # Use rsync + ssh to make a mirror of the distant folder
      user_string = ''
      if backup['user'] != None and len(backup['user']) > 0:
        user_string = "%s@" % backup['user']
      remote_url = "%s%s:%s" % (user_string, backup['host'], backup['remote_dir'])
      rsync_backup = """rsync -axHvz --numeric-ids --progress --stats --delete --partial --delete-excluded -e 'ssh -2 -p %s' %s %s""" % (backup['port'], remote_url, backup_folders['mirror'])

      # If it is passwordless, don't use pexpect but run() method instead
      if password_less:
        run(rsync_backup, d)
      else:
        # In this case we use pexpect to send the password
        if d:
          print "DEBUG - Run `%s`..." % rsync_backup  # XXX Duplicate with 'run()' method
        p = pexpect.spawn(rsync_backup)   # TODO: create a method similar to run() but that take a password as parameter to handle pexpect nicely
        import StringIO
        p_log = StringIO.StringIO()
        p.setlog(p_log)
        i = p.expect(['.ssword:*', pexpect.EOF, pexpect.TIMEOUT], timeout=TIMEOUT)
        time.sleep(1)
        # Password required
        if i == 0:
          # rsync ask for a password. Send it.
          p.sendline(backup['password'])
          print " INFO - SSH password sent"
          j = p.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=TIMEOUT)
          time.sleep(1)
          if j == 1:
            print "ERROR - Backup via SSH reached timeout"
            continue
        elif i == 1:
          print "ERROR - Backup via SSH didn't end correctly"
          continue
        elif i == 2:
          print "ERROR - Backup via SSH reached timeout"
          continue
        # Terminate child process
        nice_log(p_log.getvalue(), 'rsync')
        p_log.close()
        p.close()


    ### Mirror remote mysql database
    elif backup_type in ['MYSQLDUMP', 'MYSQLDUMP+SSH']:
      # Build mysqldump command
      mysqldump = """mysqldump --host=%s --port=%s --user=%s --password=%s --opt""" % (backup['db_host'], backup['db_port'], backup['db_user'], backup['db_pass'])
      # if no database name provided, dump all databases
      db_to_dump = '--all-databases'
      if backup.has_key('db_name') and len(backup['db_name']) > 0:
        db_to_dump = '--databases %s' % backup['db_name']
      mysqldump += ' %s' % db_to_dump
      # Build final command
      sql_file = abspath(SEP.join([backup_folders['mirror'], SQL_FILENAME]))
      if backup_type == 'MYSQLDUMP+SSH':
        # Test SSH password-less connection
        password_less = isSSHPasswordLess(backup['host'], backup['user'])
        if password_less == None:
          print "FATAL - Can't guess authentication method of '%s'" % backup['host']
          continue
        cmd = """ssh -C -2 -p %s %s@%s "%s" > %s""" % (backup['port'], backup['user'], backup['host'], mysqldump, sql_file)
      else:
        cmd = "%s > %s" % (mysqldump, sql_file)
      run(cmd, d)


    ### Mirroring is successful
    print " INFO - %s mirroring succeed" % backup_type


    ##########
    # Step 2 - Update incremental backup
    ##########

    print " INFO - Add the mirror as increment"

    # Use rdiff-backup to do efficient incremental backups
    rdiff_cmd = """rdiff-backup "%s" "%s" """ % (backup_folders['mirror'], backup_folders['diff'])
    run(rdiff_cmd, d)

    print " INFO - Increment added"


    ##########
    # Step 3 - Generate monthly archives
    ##########

    # Generate monthly archive name
    today_items   = datetime.date.today().timetuple()
    current_year  = today_items[0]
    current_month = today_items[1]
    monthly_archive = abspath("%s%s%04d-%02d.tar.bz2" % (backup_folders['archives'], SEP, current_year, current_month))
    snapshot_date = "%04d-%02d-01" % (current_year, current_month)

    # If month started, make a bzip2 archive
    if not exists(monthly_archive):
      print " INFO - Generate archive of previous month (= %s 00:00 snapshot)" % snapshot_date
      tmp_archives_path = abspath(backup_folders['archives'] + SEP + "tmp")
      if exists(tmp_archives_path):
        run("""rm -rf "%s" """ % tmp_archives_path, d)
        print " INFO - Previous temporary folder '%s' removed" % tmp_archives_path
      mkdir(tmp_archives_path)
      print " INFO - Temporary folder '%s' created" % tmp_archives_path
      rdiff_cmd = """rdiff-backup -r "%s" "%s" "%s" """ % ( snapshot_date
                                                          , backup_folders['diff']
                                                          , tmp_archives_path
                                                          )
      run(rdiff_cmd, d)
      run("tar c -C %s ./ | bzip2 > %s" % (tmp_archives_path, monthly_archive), d)
      # Delete the tmp folder
      run("""rm -vrf "%s" """ % tmp_archives_path, d)
    else:
      print " INFO - No need to generate archive: previous month already archived"

    # Keep last 32 increments (31 days = 1 month + 1 day)
    print " INFO - Remove increments older than 32 days"
    rdiff_cmd = """rdiff-backup --force --remove-older-than 32B "%s" """ % backup_folders['diff']
    run(rdiff_cmd, d)

    # Final message before next backup item
    print " INFO - Backup successful"



def usage():
  print """Usage: %s [options]

Options:
  -d, --debug
      Run in debug mode (show command lines).
  -h, --help
      Show this screen.

Supported backup type:""" % sys.argv[0]
  LIST_MARK = "  * "
  print LIST_MARK + ('\n' + LIST_MARK).join(BACKUP_TYPE_LIST)


if __name__ == "__main__":
  try:
    opts, args = getopt.getopt( sys.argv[1:]
                              , "hd"
                              , ["help", "debug"]
                              )
  except getopt.GetoptError:
    # exit on command line error
    sys.exit(2)

  # Start action according parameters
  debug = False
  for o, a in opts:
    if o in ("-d", "--debug"):
      debug = True
    elif o in ("-h", "--help"):
      usage()
      sys.exit(0)

  main(debug)
  print ''
  print " INFO - All backup items processed"
  sys.exit(0)
