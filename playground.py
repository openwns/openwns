#! /usr/bin/env python
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
import commands
import shutil
import sys

def installEnvironment():
    """ Installs wnsrc.py to /home/$USER/.wns

    openWNS-sdk needs a common way to setup paths for some directories in
    the sandbox. The entry point for this is wnsrc.py. The master wnsrc.py
    file is under version and is located in openwns-sdk/config/wnsrc.py.
    Changes in openwns-sdk/config/wnsrc.py will always be copied to
    /home/$USER/.wns/wnsrc.py everytime playground.py is executed.
    """

    # This will install wnsrc.py to /home/$USER/.wns
    wnsDir = os.path.join(os.environ["HOME"], ".wns")
    if not os.path.exists(wnsDir):
        os.mkdir(wnsDir)
    if not os.path.exists("sandbox"):
        os.mkdir("sandbox")

    # The wnsrc.py will always be copied.
    shutil.copy("config/wnsrc.py", wnsDir)
    if not os.environ.has_key("PYTHONPATH") or wnsDir not in os.environ["PYTHONPATH"]:
        print "\nERROR:"
        print "Please add '" + wnsDir + "' to the environment variable PYTHONPATH"
        print "You have three options:"
        print "1.) type 'export PYTHONPATH=$PYTHONPATH:"+wnsDir+"' in your current shell"
        print "    This affects only your current shell!"
        print "2.) add the above line to your ~/.bashrc"
        print "    Prefered: next time you login the variable will already be set."
        print "3.) call " + os.path.join(os.getcwd(), "bin", "setEnvironment")
        print "    Again, this affects only your current shell!"
        print
        sys.exit(1)

def installWNSBase():
    """ Installs wnsbase package to the sandbox.

    openWNS-sdk provides the python package wnsbase. This includes python classes that
    are available for all modules within your openWNS-sdk. Everytime you invoke playground.py
    openWNS-sdk/wnsbase is installed openWNS-sdk/sandbox/default/lib/python2.4/site-packages/wnsbase.
    """

    # Install all files in wnsbase to sandbox
    sandboxSrcSubDir = os.path.join("default", "lib", "python2.4", "site-packages", "wnsbase")
    if commands.getstatusoutput("rm -rf sandbox/" + str(sandboxSrcSubDir))[0] != 0:
        print "\nERROR:"
        print "Unable to remove path for wnsbase Python module in sandbox"

    if commands.getstatusoutput("mkdir -p sandbox/" + str(sandboxSrcSubDir))[0] != 0:
        print "\nERROR:"
        print "Unable to create path for wnsbase Python module in sandbox"

    if commands.getstatusoutput("cp -R wnsbase/* sandbox/" + str(sandboxSrcSubDir))[0] != 0:
        print "\nERROR:"
        print "Unable to install wnsbase files to sandbox"

installEnvironment()
installWNSBase()

import wnsrc
import wnsbase.playground.Core

if __name__ == "__main__":

    core = wnsbase.playground.Core.getCore()

    pywnsPluginsPath = os.path.join("sandbox", "default", "lib", "python2.4", "site-packages", "pywns", "playgroundPlugins")

    core.addPluginPath(pywnsPluginsPath)

    core.addPluginPath(os.path.join(os.environ["HOME"], ".wns", "playgroundPlugins"))

    core.startup()

    core.run()

    core.shutdown()
