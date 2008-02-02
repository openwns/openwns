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

import os
import shutil

from wnsbase.playground.Tools import *

import wnsbase.playground.Core
import wnsbase.playground.plugins.Command
core = wnsbase.playground.Core.getCore()

class ConsistencyCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog consistency TARGET\n\n"
        rationale = "Check if projects.py is consistent with file system contents."

        usage += rationale
        usage += """Use this command to check if the projects defined in projects.py are also present in the file system."""
        wnsbase.playground.plugins.Command.Command.__init__(self, "consistency", rationale, usage)

    def checkConsistency(self, project):
	print "Checking consistency for %s" % project.getDir()
	parentBranchFileSystem = project.getRCS().getFQRN().rstrip("/")
	parentBranchProjectsPy = project.getRCSUrl()

	if parentBranchFileSystem != parentBranchProjectsPy:
	    print "WARNING! Inconsistency detected"
            print "  Directory     : %s" % project.getDir()
	    print "  Parent is     : %s" % parentBranchFileSystem
	    print "  but should be : %s" % parentBranchProjectsPy
	    print "You should remove this directory and do ./playground.py upgrade to fetch the correct version"
            print "Make sure you do not delete uncommited or unpushed changes (use ./playground.py status/missing)"

    def run(self):
	core.foreachProject(self.checkConsistency)
