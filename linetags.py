#!/usr/bin/python
#
# Find out how many lines were introduced in each major release.
#
# linetags <directory>
#
# This code is part of the LWN git data miner.
#
# Copyright 2007-11 Eklektix, Inc.
# Copyright 2007-11 Jonathan Corbet <corbet@lwn.net>
#
# This file may be distributed under the terms of the GNU General
# Public License, version 2.
#
import sys, re, os, pickle

CommitLines = { }

commitpat = re.compile(r'^([\da-f][\da-f]+) ')

def GetCommitLines(file):
    print file
    blame = os.popen('git blame -p ' + file, 'r')
    for line in blame.readlines():
        m = commitpat.search(line)
        #
        # All-zero commits mean we got fed a file that git doesn't
        # know about.  We could throw an exception and abort processing
        # now, or we can just silently ignore it...
        #
        if not m or m.group(1) == '0000000000000000000000000000000000000000':
            continue
        try:
            CommitLines[m.group(1)] += 1
        except KeyError:
            CommitLines[m.group(1)] = 1
    blame.close()

#
# Try to figure out which tag is the first to contain each commit.
#
refpat = re.compile(r'^(v2\.6\.\d\d).*$')
def CommitToTag(commit):
    try:
        return DB[commit]
    except KeyError:
        print 'Missing commit %s' % (commit)
        return 'WTF?'

TagLines = { }
def MapCommits():
    print 'Mapping tags...'
    for commit in CommitLines.keys():
        tag = CommitToTag(commit)
        try:
            TagLines[tag] += CommitLines[commit]
        except KeyError:
            TagLines[tag] = CommitLines[commit]

#
# Here we just plow through all the files.
#
if len(sys.argv) != 2:
    sys.stderr.write('Usage: linetags directory\n')
    sys.exit(1)
#
# Grab the tags/version database.
#
dbf = open('committags.db', 'r')
DB = pickle.load(dbf)
dbf.close()

out = open('linetags.out', 'w')
os.chdir(sys.argv[1])
files = os.popen('/usr/bin/find . -type f', 'r')
for file in files.readlines():
    if file.find('.git/') < 0:
        GetCommitLines(file[:-1])
MapCommits()
# print TagLines
tags = TagLines.keys()
tags.sort()
for tag in tags:
    out.write('%s %d\n' % (tag, TagLines[tag]))
out.close()
