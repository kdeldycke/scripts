#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2006 Kevin Deldycke <kev@coolcavemen.com>
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
  Last update: 2006 dec 05

  Requirements:
    * linux
    * python
    * lftp
    * tar
    * bzip2
    * rdiff-backup

  TODO:
    * support pre-command (use case: de-tar mysql remote backups)
    * output verbosier logs
    * send bakcup reports by mail
    * send error by mail
"""


################### Start of user config ###################


FTP_USER = 'kevin'
FTP_PASS = '<password>'
FTP_SITE = 'ftp.website.com'
FTP_PORT = '21'
BACKUP_DIR = '/mnt/external_enclosure/backup'

ftpsite_list = [
  { 'title'     : "Web site 1"
  , 'user'      : FTP_USER
  , 'password'  : FTP_PASS
  , 'site'      : FTP_SITE
  , 'port'      : FTP_PORT
  , 'remote_dir': '/var/www/html'
  , 'local_dir' : 'website'
  },
  { 'title'     : "Kevin's website"
  , 'user'      : FTP_USER
  , 'password'  : FTP_PASS
  , 'site'      : FTP_SITE
  , 'port'      : FTP_PORT
  , 'remote_dir': '/kevin/htdocs'
  , 'local_dir' : 'kevin'
  },
]


#################### End of user config ####################
################ Do not modify code below ! ################

import sys, datetime, getopt
from urllib   import quote      as q
from urllib   import quote_plus as qp
from os       import mkdir, remove, system, rmdir
from os.path  import abspath, exists, isfile, sep

# Define constants
SEP = sep



def run(cmd, debug=False):
  """
    Run system command and print debug message if require.
  """
  if debug:
    print "Trying to execute following command:"
    print "  `%s`" % cmd
  system(cmd)
  if debug:
    print "  Done."
    print ""



def main(d=False):
  """
    Core of the backup script which implement the backup strategy.
  """

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "'%s' does't exist !" % (BACKUP_DIR)
    sys.exit(1)

  # Proceed each backup set
  for ftp_site in ftpsite_list:

    # Annonce the backup set
    title = ftp_site['title']
    print '=' * 40
    print "%s backup" % (title)
    print '=' * 40

    # Create backup folder structure if needed
    backup_folders = {}
    backup_folders['main']     = abspath(BACKUP_DIR + SEP + ftp_site['local_dir'])
    backup_folders['archives'] = abspath(backup_folders['main'] + SEP + "monthly-archives")  # Contain monthly archives
    backup_folders['rdiff']    = abspath(backup_folders['main'] + SEP + "rdiff-repository")  # Contain current month diferential backup
    backup_folders['ftp']      = abspath(backup_folders['main'] + SEP + "ftp-mirror")        # Contain a mirror of the distant web site get through FTP
    for (folder_type, folder_path) in backup_folders.items():
      if not exists(folder_path):
        mkdir(folder_path)

    # Generate remote url
    remote_url = "ftp://%s:%s@%s:%s/%s" % ( qp(ftp_site['user'])
                                          , qp(ftp_site['password'])
                                          , qp(ftp_site['site'])
                                          , ftp_site['port']
                                          , q(ftp_site['remote_dir'])
                                          )

    # Get a copy of the remote directory
    mirror_cmd = """lftp -c 'open -e "mirror -e --parallel=2 . %s" %s'""" % (backup_folders['ftp'], remote_url)
    run(mirror_cmd, d)

    # Make a backup to rdiff repository
    rdiff_cmd = """rdiff-backup "%s" "%s" """ % (backup_folders['ftp'], backup_folders['rdiff'])
    run(rdiff_cmd, d)

    # Generate monthly archive name
    today_items   = datetime.date.today().timetuple()
    current_year  = today_items[0]
    current_month = today_items[1]
    monthly_archive = abspath("%s%s%04d-%02d.tar.bz2" % (backup_folders['archives'], SEP, current_year, current_month))

    # If month started, make a bzip2 archive
    if not exists(monthly_archive):
      tmp_archives_path = abspath(backup_folders['archives'] + SEP + "tmp")
      if exists(tmp_archives_path):
        run("""rm -rf "%s" """ % tmp_archives_path, d)
      mkdir(tmp_archives_path)
      rdiff_cmd = """rdiff-backup -r "%04d-%02d-01" "%s" "%s" """ % ( current_year
                                                                    , current_month
                                                                    , backup_folders['rdiff']
                                                                    , tmp_archives_path
                                                                    )
      run(rdiff_cmd, d)
      run("tar c -C %s ./ | bzip2 > %s" % (tmp_archives_path, monthly_archive), d)
      # Delete the tmp folder
      run("""rm -rf "%s" """ % tmp_archives_path, d)

    # Delete diff older than 32 days (31 days = 1 month + 1 day of security backup)
    rdiff_cmd = """rdiff-backup --remove-older-than 32D "%s" """ % backup_folders['rdiff']
    run(rdiff_cmd, d)



def usage():
  print """Usage: %s [options]
  -d, --debug
      Run in debug mode (show command lines).
  -h, --help
      Show this screen.
""" % sys.argv[0]



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
  sys.exit(0)