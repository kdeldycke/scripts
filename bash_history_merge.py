# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kevin Deldycke <kevin@deldycke.com>
# All Rights Reserved.
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

""" Merge multiple `.bash_history` files and deduplicate their content.

Produces a consolidated output on STDOUT with all entries sorted by timestamps.

During the deduplication process, historized command lines are normalized by
stripping their leading and trailing blank charaters.

Are considered duplicate entries those sharing the exact same timestamp and
normalized command line.

Requires the `boltons` python module, installable via `pip`:

  $ pip install boltons

Usage example:

  $ python bash_history_merge.py "~/.bash_history" ".histcopy" > .merged_hist

"""

from __future__ import print_function

from itertools import chain, imap
from os import path
import sys

from boltons.iterutils import pairwise_iter


def parse_history(filepath):
    """ Parse an history file, normalize its timestamp and command lines. """
    assert path.isfile(filepath)
    with open(filepath, 'r') as f:
        for timestamp, cmd in pairwise_iter(f):
            if not timestamp.startswith('#'):
                continue
            timestamp = timestamp[1:].strip()
            try:
                assert timestamp == str(int(timestamp))
            except ValueError:
                continue
            cmd = cmd.strip()
            if cmd and timestamp:
                yield (timestamp, cmd)


def main(*args):
    # Normalize and deduplicate input files.
    input_files = {path.normpath(path.expanduser(f)) for f in args}
    # Parse and merge all files entries.
    results = chain.from_iterable(imap(parse_history, input_files))
    # Deduplicate and sort entries.
    for timestamp, cmd in sorted(set(results)):
        print("#{}\n{}".format(timestamp, cmd))


if __name__ == "__main__":
    main(*sys.argv[1:])
