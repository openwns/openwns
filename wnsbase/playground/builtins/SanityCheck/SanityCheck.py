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

from wnsbase.playground.Tools import *

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

from wnsbase.playground.builtins.Lint.Lint import LintCommand
from wnsbase.playground.builtins.Changes.Changes import ChangesCommand
from wnsbase.playground.builtins.Install.Install import InstallCommand
from wnsbase.playground.builtins.Testing.Testing import RunTestsCommand

class CheckSanityCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog checksanity\n\n"
        rationale = "Sanity check for all projects. Runs lint, changes, install and runtests"

        usage += rationale

        usage += """

This is a convenience wrapper that runs the followoing playround commands
   1. %prog lint
   2. %prog changes
   3. %prog install dbg
   4. %prog install opt
   5. %prog runtests
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "checksanity", rationale, usage)

    def run(self):

        installCommand = InstallCommand()
        lintCommand = LintCommand()
        changesCommand = ChangesCommand()
        changesCommand.startup([""])
        runTestsCommand = RunTestsCommand()

        def sanityCheckRunner(fun, message, arg = "unused"):
            print message
            answer = ""
            # run once
            fun()
            # run again upon user's request
            while not core.userFeedback.askForReject("Do you want to fix something and run again?"):
                fun()

        sanityCheckRunner(lintCommand.run, "running ./playground.py --lint" )
        sanityCheckRunner(changesCommand.run, "running ./playground.py --changes" )

        print "running ./playground.py --install=dbg"
        installCommand.startup("dbg")
        installCommand.run()

        print "running ./playground.py --install=opt"
        installCommand.startup("opt")
        installCommand.run()

        runTestsCommand()
