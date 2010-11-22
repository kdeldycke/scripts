#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2004-2005 Kevin Deldycke <kev@funky-storm.com>
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
  Last update : 2005 jul 20
"""



from commands import getstatusoutput
from os import system, path
import sys



MATCH_STRING    = 'openvpn'
RESTART_COMMAND = 'modprobe tun && /etc/init.d/openvpn restart'



def main():

  # Do the shell command
  result = getstatusoutput("ps ax | grep '%s'" % (MATCH_STRING))

  # Create a list of found processes
  process_list = result[1].splitlines()

  # Search the running process
  process_down = True
  for process in process_list:
    if process.find(MATCH_STRING) != -1 and process.find('grep') == -1:
      process_down = False

  # Restart the process if necessary
  if process_down:
    system(RESTART_COMMAND)

  # Get the script name to help sysadmin identify which script write informations via the logger
  script_name = path.basename(sys.argv[0])

  # Check if our process is running
  if process_down:
    system("logger -t '" + script_name + "' " + MATCH_STRING + " is not running")
    # Restart the process
    system(RESTART_COMMAND)
    system("logger -t '" + script_name + "' " + MATCH_STRING + " restarted")
  else:
    system("logger -t '" + script_name + "' " + MATCH_STRING + " is running")



if __name__ == "__main__":
  main()
