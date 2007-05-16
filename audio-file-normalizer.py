#!/usr/bin/python

##############################################################################
#
# Copyright (C) 2007 Kevin Deldycke <kev@coolcavemen.com>
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
  Last update : 20O7 may 16

  Description:
    This script parse a m3u playlist and copy all audio tracks in a given folder.
    This script can also convert files to a given format if needed.
"""



import sys
from os       import remove
from os.path  import abspath, exists, splitext, split as splitpath
from commands import getstatusoutput as run


PLAYLIST_PATH = "/home/kevin/Desktop/aac/road-music.m3u"

# Commands template to decode audio file of a particular type to a pure wave format
AUDIO_TO_WAVE = { 'flac':
                , 'ogg' :
                }

if __name__ == "__main__":

  # Normalize path
  playlist_path = abspath(PLAYLIST_PATH)

  # Parse the m3u playlist
  if not exists(playlist_path):
    print " FATAL - '%s' playlist doesn't exist" % playlist_path
    sys.exit(1)
  playlist = open(playlist_path, 'r')
  lines = playlist.readlines()
  track_list = []
  for l in lines:
    l = l.strip()
    # Ignore comments and empty lines
    if not l.startswith('#') and len(l) > 0:
      # Check that the file is real
      track_list.append(l)
  playlist.close()

  # Proceed each track
  for track in track_list:
    file_type = splitext(track)[1].lower()
    (file_path, file_name) = splitpath(track)
    file_name = file_name.split(file_type)[0]
    file_type = file_type[1:]

    # MP3s are just copied as is
    if file_type == 'mp3':
      # Download (copy) the track
      run(""" cp "%s" ./""" % track)
      print " DOWNLOADED - %s" % track

    # FLACs are re-encoded as AAC
    elif file_type == 'flac':
      wave_file = abspath("./%s.wav" % file_name)
      run("""flac --output-name="%s" --decode "%s" """ % (wave_file, track))
      print "    DECODED - %s" % track
      run("""faac -q 80 "%s" """ % wave_file)
      print "AAC ENCODED - %s" % wave_file
      #alt: encode to mp3
      #run("""lame --preset standard "%s" """ % wave_file)
      #print "MP3 ENCODED - %s" % wave_file
      remove(wave_file)
      print "WAV REMOVED - %s" % wave_file

    # OGGs are re-encoded as AAC
    elif file_type == 'ogg':
      wave_file = abspath("./%s.wav" % file_name)
      run("""oggdec --quiet --output "%s" "%s" """ % (wave_file, track))
      print "    DECODED - %s" % track
      run("""faac -q 80 "%s" """ % wave_file)
      print "AAC ENCODED - %s" % wave_file
      #alt: encode to mp3
      #run("""lame --preset standard "%s" """ % wave_file)
      #print "MP3 ENCODED - %s" % wave_file
      remove(wave_file)
      print "WAV REMOVED - %s" % wave_file


    #TODO: rename file to have clean filename like Red-Hot-Chili-Peppers-One-Big-Mob.aac
    #TODO: abfuscate and randomize file names
    #TODO: take care of metadatas