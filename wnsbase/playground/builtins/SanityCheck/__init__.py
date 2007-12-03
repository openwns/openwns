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

import wnsbase.playground.Core
import SanityCheck

optParser = wnsbase.playground.Core.getCore().getOptParser()
commandQueue = wnsbase.playground.Core.getCore().getCommandQueue()
core = wnsbase.playground.Core.getCore()

if not core.hasPlugin("SanityCheck"):
    core.registerPlugin("SanityCheck")
    optParser.add_option("", "--sanityCheck",
                         action="callback", callback = commandQueue.append,
                         callback_args = (SanityCheck.sanityCheckCommand,),
                         help="Runs: --lint, --changes, --install=dbg, --install=opt, --runTests (None)")
