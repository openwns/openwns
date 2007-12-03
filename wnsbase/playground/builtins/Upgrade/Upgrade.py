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

import sys
from wnsbase.playground.Tools import *
import wnsbase.playground.plugins.Command

from wnsbase.playground.builtins.Update.Update import UpdateCommand

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

class UpgradeCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog upgrade\n\n"
        rationale = "Update the whole project tree and all its modules."

        usage += rationale

        usage += """

Upgrade first uses the update command to update the project base. Afterwards
all project listed in the project configuration file will be update with new
patches from the remote repository (if any are available).
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "upgrade", rationale, usage)

    def run(self):
        updateCommand = UpdateCommand()
        updateCommand.startup([""])
        updateCommand.run()

        def upgrade(project):
            arch = project.getRCS()
            if project.getRCS().isPinned():
                sys.stdout.write("\nSkipping module in %s, because it is pinned to %s\n\n"
                                 % (project.getDir(), project.getRCS().getPinnedPatchLevel()))
                return
            sys.stdout.write("Checking for new patches in: %s ... " % (project.getDir()))
            sys.stdout.flush()
            missing = str(project.getRCS().missing(project.getRCSUrl(), {"-s":""}))
            if(missing != ""):
                print "Found:"
                print missing
                checkForConflictsAndExit(".")
                print "\nRetrieving new patches for '" + project.getDir() + "' ..."
                gnuArch = project.getRCS()

                try:
                    gnuArch.update().realtimePrint()
                    checkForConflictsAndExit(".")
                except:
                    print "An TLA error occured."
                    sys.exit(1)
            else:
                print "None"

        core.foreachProject(upgrade)
