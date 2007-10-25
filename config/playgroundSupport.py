#! /usr/bin/env python2.4
import os
import commands

class Project(object):
    # automatic setting of defaultArchive
    defaultArchive = commands.getoutput("tla tree-version").split("/")[0]

    def __init__ (self,
                  directory,
                  revision,
                  rcs,
                  dependencies,
                  executable,
                  generateDoc = True,
                  alias = None,
                  archive = None):

        if Project.defaultArchive == None:
            raise Exception("\nPlease set '(playgroundSupport.)Project.defaultArchive' in 'config/projects.py'"
                            " (e.g. to 'software@comnets.rwth-aachen.de--2006')!!!")

        if archive == None:
            self.__archive = Project.defaultArchive
        else:
            self.__archive = archive
        self.baseDir = directory
        self.revision = revision

        tmp = self.revision.split("--")

        self.version = ""
        self.patchLevel = ""

        if len(tmp) == 4:
            self.version = "--".join(tmp[0:3])
            self.patchLevel = "--" + tmp[3]
        else:
            self.version = self.revision
            self.patchLevel = ""

        self.rcs = rcs
        self.dependencies = dependencies
        self.executable = executable
        self.alias = alias
        self.generateDoc = generateDoc

        self.__buildDependencies()

    def getFQRN(self):
        return self.__archive + "/" + self.revision

    def getDir(self):
        return os.path.join(self.baseDir, self.version)

    def getRCS(self):
        return self.rcs

    def getExe(self):
        return self.executable

    def getArchive(self):
        return self.__archive

    def addDependingProject(self, project):
        self.dependingProjects.append(project)

    def __buildDependencies(self):
        self.dependingProjects = []
        for project in self.dependencies:
            project.addDependingProject(self)


class Library(Project):
    def __init__(self, directory, revision, rcs, dependencies, archive = None):
        super(Library, self).__init__(directory = directory,
                                      revision = revision,
                                      rcs = rcs,
                                      archive = archive,
                                      dependencies = dependencies,
                                      executable = 'lib')

class AddOn(Library):
    def __init__(self, baseProject, revision, rcs, addOnDir = "addOn", archive = None):
        super(AddOn, self).__init__(os.path.join(baseProject.getDir(), addOnDir),
                                    revision = revision,
				    rcs = rcs,
                                    archive = archive,
                                    dependencies = baseProject.dependencies + [baseProject])
        # handled by the "master" project
        self.executable = None
        # handled by the "master" project
        self.generateDoc = False
        self.rcs.setPath(self.getDir())

    def getDir(self):
        return self.baseDir


class Binary(Project):
    def __init__(self, directory, revision, rcs, dependencies, archive = None):
        super(Binary, self).__init__(directory = directory,
                                      revision = revision,
                                      rcs = rcs,
                                      archive = archive,
                                      dependencies = dependencies,
                                      executable = 'bin')

class Python(Project):
    def __init__(self, directory, revision, rcs, archive = None, generateDoc = True):
        super(Python, self).__init__(directory = directory,
                                     revision = revision,
                                     rcs = rcs,
                                     archive = archive,
                                     dependencies = [],
                                     executable = 'python',
                                     generateDoc = generateDoc)

class SystemTest(Project):
    def __init__(self, directory, revision, rcs, archive = None):
        super(SystemTest, self).__init__(directory = directory,
                                     revision = revision,
                                     rcs = rcs,
                                     archive = archive,
                                     dependencies = [],
                                     executable = None,
                                     generateDoc = False)
    
class Generic(Project):
    def __init__(self, directory, revision, rcs, alias = None, archive = None):
        super(Generic, self).__init__(directory = directory,
                                      revision = revision,
                                      rcs = rcs,
                                      alias = alias,
                                      archive = archive,
                                      dependencies = [],
                                      executable = None,
                                      generateDoc = False)

class SDL(Library):
    def prebuild(self):
        return os.system('scons -j1 s2s') == 0

class Root(Generic):
    def getDir(self):
        return self.baseDir
