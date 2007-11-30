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
import wnsrc

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

def replayCommand(arg = 'unused'):
    sys.stdout.write("Checking for new patches in: %s ... " % ("./"))
    sys.stdout.flush()
    projects = core.getProjects()
    missing = str(projects.root.getRCS().missing(projects.root.getRCSUrl(), {"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        print "\nRetrieving new patches for './' ... "
        try:
            projects.root.getRCS().replay().realtimePrint()
        except:
            print "An RCS error occured."
            sys.exit(1)
    else:
        print "None"

    sys.stdout.write("Checking for new patches in: %s ... " % ("./framework/buildSupport"))
    sys.stdout.flush()
    missing = str(projects.buildSupport.getRCS().missing(projects.buildSupport.getRCSUrl(),{"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        checkForConflictsAndExit("./framework/buildSupport")
        print "\nRetrieving new patches for './framework/buildSupport/' ..."
        try:
            projects.buildSupport.getRCS().replay().realtimePrint()
            checkForConflictsAndExit("./framework/buildSupport")
        except:
            print "An RCS error occured."
            sys.exit(1)
    else:
        print "None"

    def run(project):
        sys.stdout.write("Checking for new patches in: %s ... " % (project.getDir()))
        sys.stdout.flush()
        missing = str(project.getRCS().missing(project.getRCSUrl(), {"-s":""}))
        if(missing != ""):
            print "Found:"
            print missing
            checkForConflictsAndExit(".")
            print "\nRetrieving new patches for '" + project.getDir() + "' ..."
            rcs = project.getRCS()
            treeVersion = rcs.getTreeVersion()
            if treeVersion != project.getFQRN():
                print "Warning: You're upgrading version: " + treeVersion
                print "The version specified for this directory is: " + project.getFQRN()
                print "It has been kept back. To change to the new version try './playground.py --dist-upgrade'"
                if not core.userFeedback.askForConfirmation("Continue ?"):
                    return
            try:
                rcs.replay().realtimePrint()
                checkForConflictsAndExit(".")
            except:
                print "An TLA error occured."
                sys.exit(1)
        else:
            print "None"

    core.foreachProject(run)
