#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2004-2006 Kevin Deldycke <kevin@deldycke.com>
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
  Last update : 2006 mar 09
"""


from commands import getstatusoutput
from os import system, path
import sys


def main():

  # Get the list of working NICs
  up_eth_list = []
  result = getstatusoutput("/sbin/ifconfig | /bin/grep 'eth'")
  for nic in result[1].splitlines():
    up_eth_list.append(nic.split(' ')[0])
  up_eth_list.sort()

  # Restart the network service if not all NICs are up
  nic_list = ['eth0'] #, 'eth1']
  if str(up_eth_list) != str(nic_list):
    system("/etc/init.d/network restart")
    # Get the script name to help sysadmin identify which script write informations via the logger
    script_name = path.basename(sys.argv[0])
    system("logger -t '%s' network service restarted, because [%s] were up instead of [%s]" %
                   ( script_name
                   , ', '.join(up_eth_list)
                   , ', '.join(nic_list)
                   )
          )


if __name__ == "__main__":
  main()
