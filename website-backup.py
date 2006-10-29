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
  Last update: 20O6 oct 29
"""

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



import sys, datetime
from commands import getstatusoutput
from urllib   import quote      as q
from urllib   import quote_plus as qp
from os       import mkdir, remove, system
from os.path  import abspath, exists, isfile, sep

SEP         = sep
DATE_FORMAT = "%04d_%02d_%02d"



def main():

  # Get all dates at the very beginning because mirroring and archiving can be very long operations
  today       = datetime.date.today()
  today_items = today.timetuple()
  today_str   = DATE_FORMAT % (today_items[0], today_items[1], today_items[2])
  yesterday       = today - datetime.timedelta(1)
  yesterday_items = yesterday.timetuple()
  yesterday_str   = DATE_FORMAT % (yesterday_items[0], yesterday_items[1], yesterday_items[2])

  # Check existence of main backup folder
  if not exists(abspath(BACKUP_DIR)):
    print "'%s' does't exist !" % (BACKUP_DIR)
    sys.exit(0)

  # Proceed each backup set
  for ftp_site in ftpsite_list:

    # Annonce the backup set
    title = ftp_site['title']
    print '-' * 40
    print "    %s backup" % (title)
    print '-' * 40

    # Create local folder tree
    local_url = abspath(BACKUP_DIR + SEP + ftp_site['local_dir'])
    if not exists(local_url):
      mkdir(local_url)
    current_dir = abspath(local_url + SEP + 'current')
    if not exists(current_dir):
      mkdir(current_dir)

    # Generate remote url
    remote_url = "ftp://%s:%s@%s:%s/%s" % ( qp(ftp_site['user'])
                                          , qp(ftp_site['password'])
                                          , qp(ftp_site['site'])
                                          , ftp_site['port']
                                          , q(ftp_site['remote_dir'])
                                          )

    # Get the current copy of the remote directory
    mirror_cmd = """lftp -c 'open -e "mirror -e --parallel=2 . %s" %s'""" % (current_dir, remote_url)
    system(mirror_cmd)

    # Compress and archive backup
    today_archive_path = abspath("%s%s%s.tar.bz2" % (local_url, SEP, today_str))
    if exists(today_archive_path):
      remove(today_archive_path)
    system("tar c -C %s ./ | bzip2 > %s" % (current_dir, today_archive_path))

    # Delete the previous day backup if nothing has changed
    yesterday_archive_path = abspath("%s%s%s.tar.bz2" % (local_url, SEP, yesterday_str))
    if exists(yesterday_archive_path) and isfile(yesterday_archive_path):
      checksum_dict = { 'today'    : {'path': today_archive_path,     'checksum': None}
                      , 'yesterday': {'path': yesterday_archive_path, 'checksum': None}
                      }
      # Compare yesterday and today backup
      for (archive_date, file_details) in checksum_dict.items():
        file_to_hash = file_details['path']
        result = getstatusoutput("md5sum %s" % file_to_hash)
        # Check that the result returned by md5sum linux command is good
        file_checksum = None
        if result[0] == 0:
          file_checksum = result[1].split(' ')[0]
        # Stop the comparing process if md5sum fail
        if file_checksum == None:
          break
        # Update the checksum dict
        checksum_dict[archive_date]['checksum'] = file_checksum

      # Compare all checksums:
      if checksum_dict['today']['checksum'] != None and \
         checksum_dict['today']['checksum'] == checksum_dict['yesterday']['checksum']:
        # Yesterday archive is the same as today archive, delete it !
        remove(checksum_dict['yesterday']['path'])



if __name__ == "__main__":
  main()
