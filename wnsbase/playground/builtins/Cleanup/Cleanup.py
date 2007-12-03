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

class CleanupCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog clean TARGET\n\n"
        rationale = "Cleanup the build environment."

        usage += rationale
        usage += """Use this command to remove files that are created during the build process and that are
not necessarily needed.

TARGET can be one of :
  pristine-trees : GNUArch creates pristine-trees that hold the current archived version. You can safely remove
                   these files. Note they can only be restored if you have access to the archive, i.e. you need
                   access to the Internet.

  objs           : The object files that were created during the build process. You do not loose any information
                   if you remove these files. But you will need to rebuild everything if you recompile.

  sandbox        : Remove the contents of the sandbox. The sandbox can be populated again with 'playground create'.

  docu           : Remove documentation for all modules

  extern         : Remove build files created when building the external programs

  build-dirs     : Remove build-dirs

  all            : All of the above
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "clean", rationale, usage)

    def run(self):
        option = " ".join(self.args)
        print option
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
            if core.isStaticBuild() == True:
                addPrint = " (static build)"
                staticOption = " static=1"
                if project.getExe() == "lib":
                    staticOption += " install-slib"
            else:
                addPrint = ""
                staticOption = " static=0"

            print "Cleaning objects for '" + core.getBuildFlavour() + "' of " + project.getDir() + addPrint
            runCommand("scons -c flavour=" + core.getBuildFlavour() + staticOption)

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
