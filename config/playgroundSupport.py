#! /usr/bin/env python2.4
import os
import commands

class Project(object):

    def __init__ (self,
                  directory,
                  rcsUrl,
                  rcs,
                  dependencies,
                  executable,
                  generateDoc = True,
                  alias = None):


        self.directory = directory

        self.rcsUrl = rcsUrl

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

    def getRCSUrl(self):
        return self.rcsUrl

    def addDependingProject(self, project):
        self.dependingProjects.append(project)

    def __buildDependencies(self):
        self.dependingProjects = []
        for project in self.dependencies:
            project.addDependingProject(self)


class Library(Project):
    def __init__(self, directory, rcsUrl, rcs, dependencies = []):
        super(Library, self).__init__(directory = directory,
                                      rcsUrl = rcsUrl,
                                      rcs = rcs,
                                      dependencies = dependencies,
                                      executable = 'lib')

class AddOn(Library):
    def __init__(self, baseProject, rcsUrl, rcs, addOnDir = "addOn"):
        super(AddOn, self).__init__(os.path.join(baseProject.getDir(), addOnDir),
                                    rcsUrl = rcsUrl,
				    rcs = rcs,
                                    dependencies = baseProject.dependencies + [baseProject])
        # handled by the "master" project
        self.executable = None
        # handled by the "master" project
        self.generateDoc = False
        self.rcs.setPath(self.getDir())

class Binary(Project):
    def __init__(self, directory, rcsUrl, rcs, dependencies= []):
        super(Binary, self).__init__(directory = directory,
                                      rcsUrl = rcsUrl,
                                      rcs = rcs,
                                      dependencies = dependencies,
                                      executable = 'bin')

class Python(Project):
    def __init__(self, directory, rcsUrl, rcs, generateDoc = True):
        super(Python, self).__init__(directory = directory,
                                     rcsUrl = rcsUrl,
                                     rcs = rcs,
                                     dependencies = [],
                                     executable = 'python',
                                     generateDoc = generateDoc)

class SystemTest(Project):
    def __init__(self, directory, rcsUrl, rcs):
        super(SystemTest, self).__init__(directory = directory,
                                         rcsUrl = rcsUrl,
                                         rcs = rcs,
                                         dependencies = [],
                                         executable = None,
                                         generateDoc = False)

class Generic(Project):
    def __init__(self, directory, rcsUrl, rcs, alias = None):
        super(Generic, self).__init__(directory = directory,
                                      rcsUrl = rcsUrl,
                                      rcs = rcs,
                                      alias = alias,
                                      dependencies = [],
                                      executable = None,
                                      generateDoc = False)

class Root(Generic):
    pass
