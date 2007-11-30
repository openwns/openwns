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

def installCommand(flavour, sandboxDir=""):

    def run(project):
        if project.getExe() == None:
            return

        print "Installing", project.getDir(), "..."

        parallel_compiles = ''
        if core.getOptions().jobs:
            parallel_compiles = '-j %d' % options.jobs

        executable = project.getExe()
        if core.getOptions().static and executable == "lib":
            executable = 's'+executable

        command = ""
        if core.getOptions().static:
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
            command += ' '.join(('scons', 'sandboxDir='+sandboxDir, staticSConsOptions, core.getOptions().scons, parallel_compiles, 'install-' + executable, 'flavour=' + flavour, ";"))
        else:
            raise("Unkown project.getExe() result: " + project.getExe())

        print "Executing:", command

        while True:
            if runProjectHook(project, 'prebuild'):
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

    if core.getOptions().static:
        # reorder: first libs then bin
        # in fact there is only one binary: WNS-CORE
        reorderedListOfProjects = [it for it in core.getProjects().all if it.getExe() == "lib"] + [it for it in core.getProjects().all if it.getExe() == "bin"]
        reorderedListOfProjects += [it for it in core.getProjects().all if it not in reorderedListOfProjects]
    core.foreachProjectIn(reorderedListOfProjects, run)


def runProjectHook(project, hookName):
    if not hasattr(project, hookName):
        return True

    hook = getattr(project, hookName)
    if not callable(hook):
        return True

    print "Running '%s' hook for project %s" % (hookName, project.getDir())
    return hook()

