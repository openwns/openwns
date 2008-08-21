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
import wnsrc
import subprocess
import FilePatcher

#from wnsbase.playground.Tools import *

import wnsbase.rcs.Bazaar

import wnsbase.playground.Core
import wnsbase.playground.plugins.Command
core = wnsbase.playground.Core.getCore()

class CreateModuleCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog createModule TARGET\n\n"
        rationale = "Create a new module from project ModuleTemplate."

        usage += rationale
        usage += """Use this command to create your new module
                 """

        wnsbase.playground.plugins.Command.Command.__init__(self, "createmodule", rationale, usage)

    def run(self):
        moduleName = core.userFeedback.askForInput("What is the name of your module (e.g.: ProjNameModule) ? ")

        moduleSeries = core.userFeedback.askForInput("What is the series of your module (e.g.: main, trunk, etc.) ? ")

        moduleVersion = core.userFeedback.askForInput("What is the version of your module (e.g. 0.8, 1.2, etc.) ? ")

        branchLocation = core.userFeedback.askForInput("Where should the branch be pushed (e.g.: file:///home/you/archive/) ? ")

        sdkLocation = core.userFeedback.askForInput("Where should the files be locate in the SDK (e.g.: ./modules/dll/) ? ")

        maintainer = core.userFeedback.askForInput("Who is the maintainer of the module (e.g. John Doe <john.doe@example.com>) ? ")

        dest = os.path.join(sdkLocation, moduleName + '--' + moduleSeries + '--' + moduleVersion)

        self._copyTemplate(dest)
        
        self._initBranch(dest)

        self._patchProject(moduleName, moduleSeries, moduleVersion, branchLocation, dest, maintainer)
        
        self._appendToProjectsPy(moduleName, moduleSeries, moduleVersion, branchLocation, dest)

        core.projects = core.readProjectsConfig(core.projectsFile)

        core.fixConfigurationLinks()

        pushTarget = "%s/%s--%s--%s" % (branchLocation, moduleName, moduleSeries, moduleVersion)

        if not core.userFeedback.askForReject("Do you want to push the project to %s" % pushTarget):
            # Push initial version
            self._pushProject(dest, pushTarget)


    def _copyTemplate(self, sdkLocation):

        orig = os.path.join(wnsrc.wnsrc.pathToWNS, "wnsbase", "playground", "builtins", "CreateModule", "moduleTemplate")

        shutil.copytree(orig, sdkLocation)

    def _initBranch(self, destination):

        curdir = os.getcwd()

        os.chdir(destination)
        
        subprocess.check_call(["bzr", "init"])

        subprocess.check_call(["bzr", "add"])

        subprocess.check_call(["bzr", "commit", "-m", "'Initial version from template'"])

        os.chdir(curdir)

    def _patchProject(self, moduleName, moduleSeries, moduleVersion, branchLocation, dest, maintainer):

        p = FilePatcher.FilePatcher(os.path.join(dest, "MAINTAINER"), "John Doe <jdoe@doh.no>", maintainer).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "config", "common.py"),
                                    "PROJNAME       = 'projname',",
                                    "PROJNAME       = '%s'," % moduleName.lower()).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "config", "common.py"),
                                    "RCS.Bazaar\('../', 'ModuleTemplate', 'main', '1.0'\),",
                                    "RCS.Bazaar('../', '%s', '%s', '%s')," % (moduleName, moduleSeries, moduleVersion)).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "config", "libfiles.py"),
                                    "ProjName",
                                    moduleName,
                                    ignoreCase=False).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.hpp"),
                                    "PROJNAME",
                                    moduleName.upper(),
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.hpp"),
                                    "ProjName",
                                    moduleName,
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.hpp"),
                                    "projname",
                                    moduleName.lower(),
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.cpp"),
                                    "PROJNAME",
                                    moduleName.upper(),
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.cpp"),
                                    "ProjName",
                                    moduleName,
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "src", "ProjNameModule.cpp"),
                                    "projname",
                                    moduleName.lower(),
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "PyConfig", "projname", "__init__.py"),
                                    "projname",
                                    moduleName.lower(),
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "PyConfig", "projname", "__init__.py"),
                                    "ProjName",
                                    moduleName,
                                    ignoreCase=False
                                    ).replaceAll()

        p = FilePatcher.FilePatcher(os.path.join(dest, "PyConfig", "projname", "__init__.py"),
                                    "-1.0",
                                    "-%s" % moduleVersion,
                                    ignoreCase=False
                                    ).replaceAll()

        curdir = os.getcwd()

        os.chdir(dest)
        
        subprocess.check_call(["bzr", "mv", "PyConfig/projname", "PyConfig/%s" % moduleName.lower() ])

        subprocess.check_call(["bzr", "mv", "src/ProjNameModule.hpp", "src/%sModule.hpp" % moduleName ])

        subprocess.check_call(["bzr", "mv", "src/ProjNameModule.cpp", "src/%sModule.cpp" % moduleName ])

        subprocess.check_call(["bzr", "ignore", ".objs", ".sconsign.dblite", "build", "include", "config/bversion.hpp", "config/private.py", "config/pushMailRecipients.py"])
 
        subprocess.check_call(["bzr", "commit", "-m", "'Applied your settings to the template'"])

        os.chdir(curdir)


    def _appendToProjectsPy(self, moduleName, moduleSeries, moduleVersion, branchLocation, destination):

        entry =  "\n"
        entry += "%s = Library('%s','%s--%s--%s', '%s',\n" % (moduleName, destination, moduleName, moduleSeries, moduleVersion, branchLocation)
        entry += "                 RCS.Bazaar('%s',\n" % (destination)
        entry += "                            '%s', '%s', '%s'),\n" % ( moduleName, moduleSeries, moduleVersion )
        entry += "%s           [ libwns ])\n" % (" " * len(moduleName))

        sourceName = os.path.join(wnsrc.wnsrc.pathToWNS, 'config', 'projects.py')
        origPPy = open(sourceName, "a")

        origPPy.write(entry)
        origPPy.write("all.append(%s)\n" % moduleName)
        origPPy.close()

    def _pushProject(self, destination, target):

        curdir = os.getcwd()

        os.chdir(destination)
        
        subprocess.check_call(["bzr", "push", target])

        os.chdir(curdir)
