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
Last update : 20O5 jul 19
"""


from commands import getstatusoutput
from os import system



def getInternetUpStatus():
  # Do the shell command
  result = getstatusoutput("ping -c 3 google.com | grep packets")
  # Test the return code of the command
  if result[0] != 0:
    return False
  else:
    return True



def isRunningProcess(process):
  # Use the 'c' option in ps to avoid self-reference to grep process
  result = getstatusoutput("ps axc | grep " + process)
  # Create a list of found processes
  process_list = result[1].splitlines()
  # Count the number of found process to be sure that our program is running
  if len(process_list) == 0:
    return False
  else:
    return True



def checkDhcpd():
  if isRunningProcess("dhcpd"):
    system("logger -t reconnect dhcpd is working well")
  else:
    system("logger -t reconnect dhcpd do not work")
    system("/etc/init.d/dhcpd restart")
    system("logger -t reconnect dhcpd restarted")



def checkMldonkey():
  if isRunningProcess("mlnet"):
    system("logger -t reconnect Mldonkey is working well")
  else:
    system("logger -t reconnect Mldonkey do not work")
    result = getstatusoutput("/etc/init.d/mldonkey restart")
    if result[1].find("File ./file_sources.ini.tmp exists") != -1:
      system("rm -f /var/lib/mldonkey/file_sources.ini.tmp")
      system("logger -t reconnect File file_sources.ini.tmp removed")
      system("/etc/init.d/mldonkey restart")
    system("logger -t reconnect Mldonkey restarted")



def getPppId():
  # Get the line of ifconfig command where the ppp network interface is found
  result = getstatusoutput("/sbin/ifconfig | grep ppp")
  # Extract just the IP address
  if result[0] != 0:
    return None
  else:
    return str(result[1].strip().split(" ")[0])[3:]



def getPppIp():
  # Get the line of ifconfig command where the IP is displayed
  result = getstatusoutput("/sbin/ifconfig | grep -A 1 ppp | grep inet")
  # Extract just the IP address
  return str(result[1].strip().split(" ")[1])[5:]



def main():

  system("logger -t reconnect Start the reconnect script...")

  # Check that some important deamon running
  # checkDhcpd()
  # checkMldonkey()

  # Number of retry
  retry = 3

  # Try to reconnect if needed
  ppp_current_id = getPppId()
  net_status = getInternetUpStatus()
  while (net_status == False or ppp_current_id != '0') and retry > 0:
    # Print the good message corresponding to the true problem
    if net_status == False:
      system("logger -t reconnect Internet do not work !")
    else:
      system("logger -t reconnect ppp interface ID is not 0 !")
    # Restart the internet service
    system("logger -t reconnect Restart network service...")
    system("/etc/init.d/network restart")
    ppp_current_id = getPppId()
    net_status = getInternetUpStatus()
    retry -= 1

  # Keep a log message of the current script effect
  if retry == 0:
    system("logger -t reconnect Connection to internet failed after 3 restart")
    if ppp_current_id == '0':
      system("logger -t reconnect The computer has to be restarted to get the right ppp ID")
      system("shutdown -r now")
    else:
      pass
      # TODO : A problems can lead to this situation : the modem is "overheated";
      #        Find a solution !!! (modem remote off-power for x seconds ?)
  else:
    system("logger -t reconnect Internet is working, public IP is " + getPppIp())



if __name__ == "__main__":
  main()