#!/bin/sh

# Path of the temporary repository where people upload their torrents file
P="/mnt/bigdisk/torrent_to_download"

# Be sure mldonkey will be able to process files
chown -R mldonkey:root $P

# Get the list of all files in the repository
files=`ls $P`

# Send each file to mldonkey
for torrent_name in $files; do
    tor=$P/$torrent_name
    # TODO: do url encoding here
    wget -q -O /dev/null "http://localhost:4080/submit?q=dllink+$tor"
    # TODO: do not remove if mldonkey doesn't accept the torrent
    rm -f $tor
  done

# Let everybody upload new torrent files to the repository
chmod -R 666 $P
