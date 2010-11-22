#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2006 Kevin Deldycke <kevin@deldycke.com>
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
  Info:
    This script get agent all possible agent list from a directory that contain apache log file, and count the frequency.
"""

import sys, os
SEP = os.path.sep

# List of string to identify user-agent of spiders, bot and other non-regular browsers
bot_list =[
  'Nutch'
, 'lucene'
, 'StackRambler'
, 'DTS Agent'
, 'looksmart'
, 'Wget'
, 'UniversalFeedParser'
, 'WinampMPEG'
, 'Slurp'
, 'yahoo!'
, 'PerlRSSReader'
, 'ichiro'
, 'Inktomi'
, 'cfetch'
, 'crawler'
, 'Teoma'
, 'Ask Jeeves'
, 'GetRight'
, 'NSPlayer'
, 'petitsage'
, 'Bot'
, 'Mediapartners'
, 'contype'
, 'iTunes'
, 'xine'
, 'findlinks'
, 'CacheabilityEngine'
, 'curl'
, 'CFNetwork'
, 'QuickTimeWinInet'
, 'findlinks'
, 'Feedfetcher'
, 'Download Master'
, 'larbin'
, 'Python-urllib'
, 'Lynx'
, 'Java/1.'
, 'aLaide.com'
, 'httpd-checker'
, 'DA '
, 'LinkWalker'
, 'asterias'
, 'NG/2'
, 'RealMedia'
, 'SBIder'
, 'spider'
, 'Windows-Media-Player'
, 'libwww-perl'
, 'Microsoft URL Control'
, 'Avant Browser'
, 'ia_archiver-web.archive.org'
, 'WebVulnCrawl'
, 'RSS_READER'
, 'NetSprint'
, 'Mimetype Getinfo'
, 'voyager'
, 'xmms'
]




def usage():
  print """Usage : getAgentList source

** [source]
      File or folder that contain apache log.
      Default: current folder.
"""



def getFileContent(file_path):
  """
    This function get the content of a file
  """
  # Verify that the file exist
  if not os.path.isfile(file_path):
    output("ERROR: " + file_path + " doesn't exist.")
    return None

  # Get file content
  file_path = os.path.abspath(file_path)
  file_object = open(file_path, 'r')

  return file_object.read()



if __name__ == "__main__":

  # Get the place where apache log files should be searched
  param_list = sys.argv[1:]
  log_path = None
  if len(param_list) != 1:
    # No source defined, use current folder
    log_path = os.path.abspath('./')
  else:
    log_path = os.path.abspath(param_list[0])

  # Create the list of log file's path
  file_list = []
  if os.path.isfile(log_path):
    file_list.append(log_path)
  elif os.path.isdir(log_path):
    for entry in os.listdir(log_path):
      entry_path = ''.join([log_path, SEP, entry])
      if os.path.isfile(entry_path):
        file_list.append(entry_path)
  else:
    print "'%s' doesn't exist or is not a file nor directory." % log_path
    sys.exit()

  # Initialize user-agent dict
  agent_list = {}

  # Analyse each log file
  for log_file in file_list:
    log = getFileContent(log_file)
    # Can't open file: proceed to next one
    if log == None:
      continue
    # Read each line
    line_list = log.split('\n')
    # Assume the last double-quoted string is the user-agent
    for line in line_list:
      splitted_line = line.split('"')
      # Get index of the last element of the 'splitted_line' list
      ua_string_index = len(splitted_line) - 1
      # If the last quoted string is empty, assume the ua string is the previous
      if len(splitted_line[ua_string_index].strip()) == 0:
        ua_string_index -= 1
      last_quoted_string = splitted_line[ua_string_index]

      # Exclude bots and non-regular user-agent
      good_ua = True
      if last_quoted_string in ('', '-', None):
        good_ua = False

      if good_ua:
        for bot_word in bot_list:
          if last_quoted_string.lower().find(bot_word.lower()) != -1:
            good_ua = False
            break

      if good_ua:
        # Store the User-Agent string in the dict and increase frenquency
        if last_quoted_string not in agent_list.keys():
          agent_list[last_quoted_string] = 1
        else:
          agent_list[last_quoted_string] = agent_list[last_quoted_string] + 1


  # Sort before printing
  au_list = []
  for (ua, freq) in agent_list.items():
    au_list.append([freq, ua])
  au_list.sort(lambda a, b: cmp(b[0], a[0]))

  # Print list
  for (freq, ua) in au_list:
    print "%8i || %s" % (freq, ua)
