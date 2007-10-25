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
import os

# Don't edit soemthing in this file! It will be installed to
# $HOME/.wns
# There it will be overwritten every time you call ./playground.py

class WNSRC:
    def __init__(self, sandboxName = "sandbox"):
        self.rootSign = ".thisIsTheRootOfWNS"
        self.sandboxName = sandboxName
        self.pathToWNS = None
        self.pathToSandbox = None
        self.activeConfigFlavour = ''
        try:
            pathToCurrentScript = os.path.abspath(sys.argv[0])
            head, tail = os.path.split(pathToCurrentScript)
            self.pathToWNS = self.__searchPathToWNS(head)
        except AttributeError, errstr:
            if "'module' object has no attribute 'argv'" not in errstr:
                raise
        if self.pathToWNS == None:
            # try from current working dir
            self.pathToWNS = self.__searchPathToWNS(os.getcwd())
        if self.pathToWNS != None:
            self.pathToSandbox = os.path.join(self.pathToWNS, self.sandboxName)

    def setPathToWNS(self, addExtern = True):
        """ Append path to current sandbox to sys.path
        """
        if self.pathToWNS != None:
            sys.path = [os.path.join(self.pathToSandbox, "default", "lib", "python2.4", "site-packages")] + sys.path
        else:
            print "WARNING: Could not set path to sandbox. You are not inside a WNS testbed!"
            print "         Your current working directory is: " + os.getcwd()

    def __searchPathToWNS(self, path):
        while self.rootSign not in os.listdir(path):
            if path == os.sep:
                # arrived in root dir
                return None
            path, tail = os.path.split(path)
        return path

    def setPathToPyConfig(self, flavour):
        """ Append path to current sandbox to sys.path
        """
        if self.pathToWNS != None:
            try:
                sys.path.remove(os.path.join(self.pathToSandbox, self.activeConfigFlavour, "lib", "PyConfig"))
            except:
                pass
            sys.path.append(os.path.join(self.pathToSandbox, flavour, "lib", "PyConfig"))

        self.activeConfigFlavour=flavour


wnsrc = WNSRC()
wnsrc.setPathToWNS()

pathToWNS = wnsrc.pathToWNS
pathToSandbox = wnsrc.pathToSandbox
