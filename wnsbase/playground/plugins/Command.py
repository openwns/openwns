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

class Command:

    def __init__(self, name, rationale, usage):
        self.name = name
        self.usage = usage
        self.rationale = rationale
        self.optParser = optparse.OptionParser(usage = usage)

    def addOption(self, *args, **kwargs):
        self.optParser.add_option(*args, **kwargs)

    def startup(self, args):
        self.options, self.args = self.optParser.parse_args(args)

    def run(self):
        pass

    def shutdown(self):
        pass

