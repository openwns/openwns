#! /usr/bin/env python2.4
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
import sys
import shutil
import re
import unittest
import os

#We assume username@maildomain as E-Mail address
maildomain = "comnets.rwth-aachen.de"

class FilePatcher:

    def __init__(self, filename, search, replace):
        self.search = search
        self.replaceWith = replace
        self.filename = filename

    def replaceAll(self):
        f = open(self.filename, 'r')

        output = ""
        for l in f:
            l = l.replace(self.search, self.replaceWith)
            output += l

        # close file
        f.close()

        # re-write new file
        fc = open(self.filename, 'w')
        fc.write(output)
        fc.close()


def searchPathToSDK(path):
    rootSign = ".thisIsTheRootOfWNS"
    while rootSign not in os.listdir(path):
        if path == os.sep:
            # arrived in root dir
            return None
        path, tail = os.path.split(path)
    return os.path.abspath(path)

pathToSDK = searchPathToSDK(os.path.abspath(os.path.dirname(sys.argv[0])))

if pathToSDK == None:
    print "Error! You are note within an openWNS-SDK. Giving up"
    exit(1)

sys.path.append(os.path.join(pathToSDK, 'sandbox/default/lib/python2.4/site-packages/'))
import wnsbase.RCS
sys.path.remove(os.path.join(pathToSDK, 'sandbox/default/lib/python2.4/site-packages/'))

class Dict2Class:
    def __init__(self, dictionary):
        for key in dictionary.iterkeys():
            if not key.startswith("__"):
                self.__dict__[key] = dictionary[key]
def runCommand(command):
    fh = os.popen(command)
    lines = []
    line = fh.readline()
    while line:
        lines.append(line.strip('\n'))
        line = fh.readline()
    return lines

def readProjectsConfig():
    sys.path.append(os.path.join(pathToSDK, "config"))
    foobar = {}
    execfile(os.path.join(pathToSDK, "config/projects.py"), foobar)
    sys.path.remove(os.path.join(pathToSDK, "config"))
    return Dict2Class(foobar)

def getProjectFiles(project):
	foundFiles = []
	#print project
	basedir = project.getDir()
	incDir = os.path.join(pathToSDK, basedir, "src")
	for (dirname, dirs, files) in os.walk(incDir):
			#print dirname
			relDirname = dirname[len(incDir) + 1:]
			for f in files:
				extension = f.split('.')[-1]
				if extension in ['h', 'hpp', 'cpp'] and not f.startswith('.'):
					foundFiles.append(os.path.abspath(os.path.join(dirname,f)))
	return foundFiles

def setupFileList():
	projects = readProjectsConfig()
	allFiles = []
	for project in projects.all:
            if project.getExe() in ['lib', 'bin']:
                print "Searching for files in %s" % project.getDir()
                allFiles = allFiles + getProjectFiles(project)
            
                if project.hasAddOns():
                    for addOn in project.getAddOns():
                        print "Searching for files in %s" % addOn.getDir()
                        allFiles = allFiles + getProjectFiles(addOn)
                
	allFiles = [f.replace(pathToSDK + "/", "") for f in allFiles]

	# Write to file
	fc = open(os.path.join(pathToSDK, "WNS.kdevelop.filelist"), 'w')
	fc.write("# KDevelop Custom Project File List\n")
        fc.write("\n".join(allFiles))
        fc.close()

def setupProjectFile():
	import getpass
	import pwd

	template = os.path.join(pathToSDK, "config/WNS.kdevelop.template")
	projectFile = os.path.join(pathToSDK, "WNS.kdevelop")
	shutil.copy (template, projectFile)
	username = getpass.getuser()
	tmp = pwd.getpwnam(username)
	authorname = tmp[4]
	email = username + "@" + maildomain
	FilePatcher(projectFile, "___AUTHORNAME___", authorname).replaceAll()
	FilePatcher(projectFile, "___EMAILADDRESS___", email).replaceAll()
	FilePatcher(projectFile, "___PATHTOWNS___", pathToSDK).replaceAll()

def setupDevsesFile():
	template = os.path.join(pathToSDK, "config/WNS.kdevses.template")
	projectFile = os.path.join(pathToSDK, "WNS.kdevses")
	shutil.copy (template, projectFile)

setupFileList()
setupProjectFile()
setupDevsesFile()

