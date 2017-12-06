# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Deldycke <kevin@deldycke.com>
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
stripping their leading and trailing blank characters. Empty history entries
will be ignored.

Are considered duplicate entries those sharing the exact same timestamp and
normalized command line.

Timestamp-less entries will be set to epoch. And their natural order will be
preserved. On deduplication, only the last occurence will be kept.

Requires the `boltons` python module, installable via `pip`:
Timestamp-less entries will be set to epoch.

  $ pip install boltons

Usage example:

  $ python bash_history_merge.py "~/.bash_history" ".histcopy" > .merged_hist

TODO: Add option to deduplicate lines, whatever their timestamp, by only
keeping the lastest occurence.
"""

from __future__ import print_function

from itertools import chain, imap
from operator import itemgetter
from os import path
from StringIO import StringIO
import sys
from textwrap import dedent

from boltons.setutils import IndexedSet


def parse_history(fd):
    """ Parse an history file, normalize its timestamp and command lines. """

    # Timestamp value of the line immediately above. Default to epoch.
    timestamp_line_above = 0

    for line in fd:

        # Normalize line.
        line = line.strip()

        # Ignore empty entries.
        if not line:
            continue

        # Parse the line as a timestamp, keep it on the side and go to the next
        # entry in the history.
        if line.startswith('#'):
            timestamp = line[1:].strip()
            try:
                assert timestamp == str(int(timestamp))
            except ValueError:
                # This line is not an integer timestamps. Ignore it.
                continue
            timestamp_line_above = int(timestamp)
            continue

        # The line here is not empty nor a timestamp. It is a valid entry.
        yield (timestamp_line_above, line)


def dedupe(*input_files):
    """ Takes file descriptors and return deduplicated content. """

    # Parse and merge all files entries.
    results = chain.from_iterable(imap(parse_history, input_files))

    # Deduplicate entries sharing the same timestamp by removing all previous
    # occurences, only keeping the last one. A reverse IndexedSet let us keep
    # entries ordered by their encounter. This is important, especially to keep
    # together timestamp-less entries coming from the same file.
    results = IndexedSet(list(results)[::-1])
    results.reverse()

    # Sort entries by timestamps.
    entries = []
    for timestamp, cmd in sorted(results, key=itemgetter(0)):
        entries.append("#{}\n{}".format(timestamp, cmd))

    return '\n'.join(entries)


def test_timestampless_merging():

    history_1 = StringIO(dedent("""
        tail -Fn 1000 /var/log/syslog | grep "foo"
        tail -Fn 10000 /var/log/syslog | grep "foo"
        cat /etc/foo.yaml
        ll
        cat /etc/foo.yaml
        tail -Fn 10000 /var/log/syslog | grep "foo"
        ll
        """))

    history_2 = StringIO(dedent("""
        ll
        history | grep foo
        ll
        ll
        history | grep bar
        ll
        ll
        """))

    output = dedupe(history_1, history_2)

    assert output == dedent("""\
        #0
        tail -Fn 1000 /var/log/syslog | grep "foo"
        #0
        cat /etc/foo.yaml
        #0
        tail -Fn 10000 /var/log/syslog | grep "foo"
        #0
        history | grep foo
        #0
        history | grep bar
        #0
        ll""")


if __name__ == "__main__":

    args = sys.argv[1:]

    # Run the mini test suite.
    if args[0] == '--tests':
        test_timestampless_merging()
        print("Success! :)")
        exit()

    # Run the deduplication process for real.
    input_files = []
    for filepath in args:
        filepath = path.normpath(path.expanduser(filepath))
        assert path.isfile(filepath)
        input_files.append(open(filepath, 'r'))
    output = dedupe(*input_files)
    print(output)
