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

class InstallCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog install [FLAVOUR]\n\n"
        rationale = "Compile and install all projects to the sandbox"

        usage += rationale
        usage += """This command starts the build process and installs all files
to the sandbox. FLAVOUR selects a build flavour. Choose one of the following:

dbg (default) : Build with debug symbols
opt           : Build optimized version without debug symbols and assures
optPentium4   :
optPentium64  :
optPentiumM   :
optAthlonMP   :
optK8         :
prof          : Build version with profiling information for gprof. You must use --static to use this.
profOpt       : Optimized profiling version
size          :
massif        :
optAssure     :
optMsg        :
optAssureMsg  :
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "install", rationale, usage)

    def run(self):
        flavour = "dbg"
        sandboxDir = ""

        if len(self.args) > 0:
            flavour = " ".join(self.args)

        def install(project):
            if project.getExe() == None:
                return

            print "Installing", project.getDir(), "..."

            parallel_compiles = ''
            if core.getNumJobs():
                parallel_compiles = '-j %d' % core.getNumJobs()

            executable = project.getExe()
            if core.isStaticBuild() and executable == "lib":
                executable = 's'+executable

            command = ""
            if core.isStaticBuild():
                staticSConsOptions = 'static=1 '
                moduleNames = []
                # special handling for WNS-CORE
                if project.getExe() == 'bin':
                    for pp in core.getProjects().all:
                        if pp.getExe() != 'lib':
                            continue
                        # list all libraries in local lib dir (e.g. framework/libwns--main--3.0/build/dbg/lib)
                        dirToCheck = os.path.join(wnsrc.pathToWNS, pp.getDir(), "build", flavour, "lib")
                        # for the external libraries this path does not exist
                        # it would be better to check this somehow else ...
                        if os.path.exists(dirToCheck):
                            dirContent = os.listdir(dirToCheck)
                            for ff in dirContent:
                                if ff.endswith('.a'):
                                    # strip 'lib' and '.a'
                                    moduleNames.append(ff[3:-2])
                    # forward this modules to WNS -> WNS will link them statically
                    if len(moduleNames) != 0:
                        staticSConsOptions += 'staticallyLinkedLibs="' + ','.join(moduleNames) + '"'

            else:
                staticSConsOptions = 'static=0'

            projectExe = project.getExe()
            if projectExe in ["lib", "bin", "pyconfig", "python"]:
                installTarget = "install-" + projectExe
                command += ' '.join(('scons', 'sandboxDir='+sandboxDir, staticSConsOptions, core.getSconsOptions(), parallel_compiles, 'install-' + executable, 'flavour=' + flavour, ";"))
            else:
                raise("Unkown project.getExe() result: " + project.getExe())

            print "Executing:", command

            while True:
                if self.runProjectHook(project, 'prebuild'):
                    result = runCommand(command)
                    if result is None:
                        return

                    print "Failed to install:", project.getDir()

                    if not core.userFeedback.askForReject("Do you want to retry the install process?"):
                        pass
                    else:
                        if core.userFeedback.askForReject("Do you want to abort the install process?"):
                            return
                        else:
                            sys.exit(1)

        core.fixConfigurationLinks()

        reorderedListOfProjects = core.getProjects().all

        if core.isStaticBuild():
            # reorder: first libs then bin
            # in fact there is only one binary: WNS-CORE
            reorderedListOfProjects = [it for it in core.getProjects().all if it.getExe() == "lib"] + [it for it in core.getProjects().all if it.getExe() == "bin"]
            reorderedListOfProjects += [it for it in core.getProjects().all if it not in reorderedListOfProjects]
        core.foreachProjectIn(reorderedListOfProjects, install)


    def runProjectHook(self, project, hookName):
        if not hasattr(project, hookName):
            return True

        hook = getattr(project, hookName)
        if not callable(hook):
            return True

        print "Running '%s' hook for project %s" % (hookName, project.getDir())
        return hook()

