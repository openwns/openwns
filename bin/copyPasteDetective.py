#!/usr/bin/python
###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import optparse

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--file",
                  type = "string", dest = "filename", default = "",
                  help = "File inspect for copy paste stuff", metavar = "FILENAME")

parser.add_option("-l", "--length",
                  type = "int", dest = "length", default = "",
                  help = "Minimum length of the copy paste section", metavar = "LENGTH")

options, args = parser.parse_args()

f = file(options.filename)
fVec = []
for line in f:
    fVec.append(line)

sections = dict()

for i in xrange(len(fVec)-1):
    for j in xrange(i+1, len(fVec)-1):
        if fVec[i]==fVec[j] and fVec[i+1]==fVec[j+1]:
            if not sections.has_key(i):
                output = """
*******************************************************************************
Found copy paste section:
"""
                sections[i]=True
                n = 1
                while fVec[i+n]==fVec[j+n]:
                    output += fVec[i+n]
                    sections[i+n]=True
                    n += 1
                    if j+n >= len(fVec):
                        break
                if n >= options.length:
                    print output
