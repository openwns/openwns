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

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

def cleanCommand(option):
    def remove(base, directory):
        delDir = os.path.join(base, directory)
        if os.path.exists(base):
            print "Cleaning", base, "..."
            if os.path.exists(delDir):
                print "deleting", delDir
                shutil.rmtree(delDir)
            else:
                print "nothing to do"

    def runCleanPristines(project):
        remove(os.path.abspath(os.getcwd()),
               os.path.join("{arch}", "++pristine-trees"))

    def runCleanObjs(project):
        if project.getExe() == None:
            return
	if core.getOptions().static:
	    addPrint = " (static build)"
	    staticOption = " static=1"
            if project.getExe() == "lib":
                staticOption += " install-slib"
	else:
	    addPrint = ""
	    staticOption = " static=0"
        print "Cleaning objects for '" + core.getOptions().flavour + "' of " + project.getDir() + addPrint
        runCommand("scons -c flavour=" + core.getOptions().flavour + staticOption)

    def runCleanDocu(project):
        remove(os.path.abspath(os.getcwd()),
               "doxydoc")

    def runCleanExtern(project):
        if "/extern" in project.getFQRN():
            runCommand("scons clean")

    def runCleanBuildDirs(project):
        if project.getExe() in ["lib", "bin"]:
            remove(os.path.abspath(os.getcwd()), "build")

    if option == "pristine-trees" or option == "all":
        remove(os.getcwd(), os.path.join("{arch}", "++pristine-trees"))
        core.foreachProject(runCleanPristines)

    if option == "sandbox" or option == "all":
        remove("./", "sandbox")

    if option == "objs" or option == "all":
        core.foreachProject(runCleanObjs)

    if option == "docu" or option == "all":
        core.foreachProject(runCleanDocu)

    if option == "extern" or option == "all":
        core.foreachProject(+runCleanExtern)

    if option == "build-dirs" or option == "all":
	core.foreachProject(runCleanBuildDirs)
