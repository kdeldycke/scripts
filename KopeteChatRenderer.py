#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2005-2007 Kevin Deldycke <kev@coolcavemen.com>
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
  Last update: 2007 may 03
"""


import getopt, sys, os
from datetime import datetime
from xml.dom import Node
from xml.dom.ext.reader import PyExpat



def usage():
  print """Usage : kopete_log [options]

** Input/Output options
    -i [input_file], --input=[input_file]
            The XML kopete log file where the chat is extracted.
            Default location: ~/.kde/share/apps/kopete/logs/XXXProtocol/ID/ID.YYYYMM.xml

** Sorting options [default: --ascending]
    -a, --ascending
            Ascending sorting of messages.
    -d, --descending
            Descending sorting of messages.

** General options
    --silent
            No informations will be printed on the standard output.
    -h, --help
            Show this screen.
"""



def output(string):
  if not silent:
    print string



def getFileContent(file_path):
  # Verify that the file exist
  if not os.path.isfile(file_path):
    output("ERROR: " + file_path + " doesn't exist.")
    return None

  # Get file content
  file_path = os.path.abspath(file_path)
  file_object = open(file_path, 'r')

  return file_object.read()


def getKopeteHistory(xml_string):
  # Create the PyExpat reader
  reader = PyExpat.Reader()

  # Create DOM tree from the xml string
  dom_tree = reader.fromString(xml_string)

  # Check the type of the file
  if dom_tree.doctype.name != 'kopete-history':
    output("ERROR: " + file_path + " is not a kopete chat history file.")
    return None

  dom_root = dom_tree.documentElement

  # Get month and year
  year = None
  month = None
  headers = dom_root.getElementsByTagName("head")
  for header_item in headers[0].childNodes:
    if header_item.nodeName == 'date':
      for attribute in header_item.attributes:
        if attribute.nodeName == 'year':
          year = int(attribute.nodeValue)
        if attribute.nodeName == 'month':
          month = int(attribute.nodeValue)

  # Get all the messages
  history = []
  message_list = dom_root.getElementsByTagName("msg")
  for message in message_list:
    msg_item = {}
    for attribute in message.attributes:
      if attribute.nodeName == 'from':
        msg_item['user'] = attribute.nodeValue
      if attribute.nodeName == 'time':
        raw_str = attribute.nodeValue.split(' ')
        day     = int(raw_str[0])
        time    = raw_str[1].split(':')
        hour    = int(time[0])
        minute  = int(time[1])
        second  = int(time[2])
        msg_item['date'] = datetime(year, month, day, hour, minute, second)
    for k in range(message.childNodes.length):
      text = message.childNodes[k]
      if text.nodeType == Node.TEXT_NODE:
        msg_item['text'] = text.nodeValue
    history.append(msg_item)

  return history



def sortHistory(dict, sort='ASC'):
  def datetimeCmp(a, b):
    datetime_a = a['date']
    datetime_b = b['date']
    if datetime_a > datetime_b:
      return 1
    if datetime_a < datetime_b:
      return -1
    else:
      return 0
  if sort == 'DESC':
    history.sort(lambda a, b: datetimeCmp(b, a))
  else:
    history.sort(lambda a, b: datetimeCmp(a, b))
  return history



def renderHistory(history, sep='|'):

  string = ''

  # Get the lenght of the longuest user name
  max_lenght = 0
  for message in history:
    name_len = len(message['user'])
    if name_len > max_lenght:
      max_lenght = name_len

  # Render the chat
  sep = ' ' + sep + ' '
  for message in history:
    string += sep.join([ str(message['date'])
                       , message['user'].ljust(max_lenght)
                       , message['text']
                       ]) + '\n'

  return string



if __name__ == "__main__":

  # Get all parameters
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hadi:", ["help", "ascending", "descending", "input=", "silent"])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)

  # Get all user's options and define internal variables
  global silent
  input_file = None
  silent     = False
  sort       = 'ASC'
  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    if o in ("-d", "--descending"):
      sort = 'DESC'
    if o == "--silent":
      silent = True
    if o in ("-i", "--input"):
      input_file = a

  if input_file == None:
    print "No input file found."
    # TODO : Try to get the file automatically
    usage()
    sys.exit()

  xml_string = getFileContent(input_file)
  if xml_string == None:
    sys.exit()

  history = getKopeteHistory(xml_string)
  history = sortHistory(history, sort)

  output_string = renderHistory(history)

  print output_string.encode('latin-1')