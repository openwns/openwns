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
###############################################################################
import os
import commands

class Project(object):

    def __init__ (self,
                  directory,
                  rcsSubDir,
                  rcsBaseUrl,
                  rcs,
                  dependencies,
                  executable,
                  generateDoc = True,
                  alias = None):


        self.directory = directory

        self.rcsSubDir = rcsSubDir

        self.rcsBaseUrl = rcsBaseUrl

        self.rcsUrl = rcsBaseUrl.rstrip("/") + "/" + rcsSubDir

        self.rcs = rcs

        self.dependencies = dependencies

        self.executable = executable

        self.alias = alias

        self.generateDoc = generateDoc

        self.__buildDependencies()

    def getFQRN(self):
        return self.rcs.getFQRN()

    def getDir(self):
        return self.directory

    def getRCS(self):
        return self.rcs

    def getExe(self):
        return self.executable

    def getRCSBaseUrl(self):
        return self.rcsBaseUrl

    def getRCSSubDir(self):
        return self.rcsSubDir

    def getRCSUrl(self):
        return self.rcsUrl

    def addDependingProject(self, project):
        self.dependingProjects.append(project)

    def __buildDependencies(self):
        self.dependingProjects = []
        for project in self.dependencies:
            project.addDependingProject(self)


class Library(Project):
    def __init__(self, directory, rcsSubDir, rcsBaseUrl, rcs, dependencies = []):
        super(Library, self).__init__(directory = directory,
                                      rcsSubDir = rcsSubDir,
                                      rcsBaseUrl = rcsBaseUrl,
                                      rcs = rcs,
                                      dependencies = dependencies,
                                      executable = 'lib')

class AddOn(Library):
    def __init__(self, baseProject, rcsSubDir, rcsBaseUrl, rcs, addOnDir = "addOn"):
        super(AddOn, self).__init__(os.path.join(baseProject.getDir(), addOnDir),
                                    rcsSubDir = rcsSubDir,
                                    rcsBaseUrl = rcsBaseUrl,
				    rcs = rcs,
                                    dependencies = baseProject.dependencies + [baseProject])
        # handled by the "master" project
        self.executable = None
        # handled by the "master" project
        self.generateDoc = False
        self.rcs.setPath(self.getDir())

class Binary(Project):
    def __init__(self, directory, rcsSubDir, rcsBaseUrl, rcs, dependencies= []):
        super(Binary, self).__init__(directory = directory,
                                     rcsSubDir = rcsSubDir,
                                     rcsBaseUrl = rcsBaseUrl,
                                     rcs = rcs,
                                     dependencies = dependencies,
                                     executable = 'bin')

class Python(Project):
    def __init__(self, directory, rcsSubDir, rcsBaseUrl, rcs, generateDoc = True):
        super(Python, self).__init__(directory = directory,
                                     rcsSubDir = rcsSubDir,
                                     rcsBaseUrl = rcsBaseUrl,
                                     rcs = rcs,
                                     dependencies = [],
                                     executable = 'python',
                                     generateDoc = generateDoc)

class SystemTest(Project):
    def __init__(self, directory, rcsSubDir, rcsBaseUrl, rcs):
        super(SystemTest, self).__init__(directory = directory,
                                         rcsSubDir = rcsSubDir,
                                         rcsBaseUrl = rcsBaseUrl,
                                         rcs = rcs,
                                         dependencies = [],
                                         executable = None,
                                         generateDoc = False)

class Generic(Project):
    def __init__(self, directory, rcsSubDir, rcsBaseUrl, rcs, alias = None):
        super(Generic, self).__init__(directory = directory,
                                      rcsSubDir = rcsSubDir,
                                      rcsBaseUrl = rcsBaseUrl,
                                      rcs = rcs,
                                      alias = alias,
                                      dependencies = [],
                                      executable = None,
                                      generateDoc = False)

class Root(Generic):
    pass