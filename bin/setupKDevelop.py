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
try:
    import wnsrc
except:
    import sys
    wnsDir = os.path.join(os.environ["HOME"], ".wns")
    sys.path.append(wnsDir)
    import wnsrc

import os
import sys
import shutil

#We assume username@maildomain as E-Mail address
maildomain = "comnets.rwth-aachen.de"

sys.path.append(os.path.join(wnsrc.pathToWNS, 'framework/buildSupport'))
import wnsbase.RCS
import FilePatcher
sys.path.remove(os.path.join(wnsrc.pathToWNS, 'framework/buildSupport'))

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
    sys.path.append(os.path.join(wnsrc.pathToWNS, "config"))
    foobar = {}
    execfile(os.path.join(wnsrc.pathToWNS, "config/projects.py"), foobar)
    sys.path.remove(os.path.join(wnsrc.pathToWNS, "config"))
    return Dict2Class(foobar)

def getProjectFiles(project):
	foundFiles = []
	#print project
	basedir = project.getDir()
	incDir = os.path.join(wnsrc.pathToWNS, basedir, "src")
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
			allFiles = allFiles + getProjectFiles(project)

	allFiles = [f.replace(wnsrc.pathToWNS + "/", "") for f in allFiles]

	# Write to file
	fc = open(os.path.join(wnsrc.pathToWNS, "WNS.kdevelop.filelist"), 'w')
	fc.write("# KDevelop Custom Project File List\n")
        fc.write("\n".join(allFiles))
        fc.close()

def setupProjectFile():
	import getpass
	import pwd

	template = os.path.join(wnsrc.pathToWNS, "config/WNS.kdevelop.template")
	projectFile = os.path.join(wnsrc.pathToWNS, "WNS.kdevelop")
	shutil.copy (template, projectFile)
	username = getpass.getuser()
	tmp = pwd.getpwnam(username)
	authorname = tmp[4]
	email = username + "@" + maildomain
	FilePatcher.FilePatcher(projectFile, "___AUTHORNAME___", authorname).replaceAll()
	FilePatcher.FilePatcher(projectFile, "___EMAILADDRESS___", email).replaceAll()
	FilePatcher.FilePatcher(projectFile, "___PATHTOWNS___", wnsrc.pathToWNS).replaceAll()

setupFileList()
setupProjectFile()
