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
import sys

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

def lintCommand(arg = 'unused'):
    def run(project):
        return linter(project)

    def linter(project):
        sys.stdout.write ("Linting" + project.getDir() + " ... ")
        result = str(project.getRCS().lint())
        if result == "":
            sys.stdout.write(" OK\n")
        else:
            sys.stdout.write(" Fail\n")
        return result

    print "Linting all project trees. A summary will be listed at the end ..."
    lintedResults = core.foreachProject(run)
    print
    print
    for ii in lintedResults:
        if ii.result != "":
            print "Lints in " + ii.dirname + ":"
            print ii.result
            print
            print
