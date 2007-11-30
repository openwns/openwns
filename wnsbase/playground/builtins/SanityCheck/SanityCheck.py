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

from wnsbase.playground.builtins.Lint.Lint import lintCommand
from wnsbase.playground.builtins.Changes.Changes import statusCommand
from wnsbase.playground.builtins.Install.Install import installCommand
from wnsbase.playground.builtins.Testing.Testing import runTestsCommand

def sanityCheckCommand(arg = "unused"):

    def sanityCheckRunner(fun, message, arg = "unused"):
        print message
	answer = ""
        # run once
        fun(arg)
        # run again upon user's request
        while not core.userFeedback.askForReject("Do you want to fix something and run again?"):
            fun(arg)

    sanityCheckRunner(lintCommand, "running ./playground.py --lint" )
    sanityCheckRunner(statusCommand, "running ./playground.py --changes" )

    print "running ./playground.py --install=dbg"
    installCommand("dbg")

    print "running ./playground.py --install=opt"
    installCommand("opt")

    runTestsCommand()
