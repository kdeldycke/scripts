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
  Last update : 20O6 feb 14
  TODO:
    * manage years
    * sort output by months
"""

from commands import getstatusoutput
from os import system, path
import sys


def main():
  # Do the shell command
  result1 = getstatusoutput("cat /var/log/syslog          | grep ': Connect time'")
  result2 = getstatusoutput("gunzip -cd /var/log/syslog.* | grep ': Connect time'")
  raw_lines = []
  raw_lines += result1[1].splitlines()
  raw_lines += result2[1].splitlines()

  connect_datas = {}
  for connect_time_line in raw_lines:
    elements = connect_time_line.split(' ')
    time = elements[::-1][1]
    month = elements[0]
    if month in connect_datas.keys():
      connect_datas[month] = float(connect_datas[month]) + float(time)
    else:
      connect_datas[month] = float(time)

  print "-- Total connect time by months:"
  for (month, total_time) in connect_datas.items():
    hours_f = total_time / 60
    hours = int(str(hours_f).split('.')[0])
    minutes_f = total_time - (hours * 60.0)
    minutes = int(str(minutes_f).split('.')[0])
    seconds_f = (minutes_f - minutes) * 60
    seconds = int(str(seconds_f).split('.')[0])
    print "      * %s -> %sh%sm%ss" % (month, hours, minutes, seconds)
  print ""


if __name__ == "__main__":
  main()
