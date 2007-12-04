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
import optparse
import re
import sets
import exceptions

from wnsbase.playground.Tools import *

import builtins
import plugins.Command

class Core:
    """ This the core of the openWNS project tree management tool 'playground'. It
    includes the basic functionality. All extension plugins get the current
    instance of the core object when invoked.
    """

    def __init__(self):
        usage = ""
        usage += "The list below shows global available options.\n"

        self.optParser = optparse.OptionParser(usage = usage)
        self.commandQueue = CommandQueue()
        self.plugins = []
        self.commands = {}
        self.ifExpr = None
        self.buildFlavour = "dbg"
        self.staticBuild = False
        self.sconsOptions = ""
        self.numJobs = 10

    def startup(self):
        self._loadBuiltins()
        self._setupCommandLineOptions()
        self.configFile = "config/projects.py"
        self.userFeedback = UserMadeDecision()

        argv = sys.argv

        self.pluginArgs = []
        i = 1
        while i < len(argv):
            a = argv[i]
            if a.startswith('--configFile'):
                self.configFile = a.split("=")[1]
            elif a == "--noAsk":
                self.userFeedback = AcceptDefaultDecision()
            elif a.startswith("--if"):
                self.ifExpr = a.split("=")[1]
            elif a == "--static":
                self.staticBuild = True
            elif a == "--flavour":
                self.buildFlavour = a.split("=")[1]
            elif a.startswith("--scons"):
                self.sconsOptions = "=".join(a.split("=")[1:])
            elif a.startswith("-j=") or a.startswith("--jobs"):
                self.numJobs = int(a.split("=")[1])
            else:
                self.pluginArgs.append(a)
            i += 1

        self.projects = self.readProjectsConfig()

        missingProjects = self.checkForMissingProjects()

        self.updateMissingProjects(missingProjects)

        if not os.path.exists(os.path.join('config', 'private.py')):
            os.symlink('private.py.template', os.path.join('config', 'private.py'))

        # install necessary files
        # must happen after missing projects ...
        for command, sourcePath in self.getProjects().prereqCommands:
            savedDir = os.getcwd()
            os.chdir(sourcePath)
            stdin, stdout = os.popen4(command)
            line = stdout.readline()
            while line:
                line = stdout.readline()
                os.chdir(savedDir)

    def run(self):
        if len(self.pluginArgs) > 0:
            commandName = self.pluginArgs[0]
            if self.commands.has_key(commandName):
                command = self.commands[commandName]
                command.startup(self.pluginArgs[1:])
                command.run()
            else:
                self.printUsage()
        else:
            self.printUsage()

        self.commandQueue.run()

        sys.exit(0)

    def shutdown(self):
        pass

    def printUsage(self):
        print "\nUsage : playground COMMAND options"
        print "\n\nYou can use one of following commands. Use COMMAND --help to get"
        print "detailed help for the command\n\n"
        for commandname, command in self.commands.items():
            print "   " + commandname.ljust(20) + ":\t" + command.rationale

        print "\n\nThere are some global options that are available for all commands"
        self.optParser.print_help()

        sys.exit(1)

    def _loadBuiltins(self):
        self.loadPluginsInDir("./wnsbase/playground/builtins", "wnsbase.playground.builtins")

    def loadPluginsInDir(self, pluginsDir, targetPackage="wnsbase.playground.plugins"):
        if os.path.exists(pluginsDir):
            plugins.__path__.append(str(pluginsDir))
            for (dirname, topLevelDirs, files) in os.walk(pluginsDir):
                break

            if topLevelDirs.count('.arch-ids') > 0:
                topLevelDirs.remove('.arch-ids')

            sys.path.append(pluginsDir)
            for plugin in topLevelDirs:
                try:
                    exec "import %s.%s" % (targetPackage, str(plugin)) in globals(), locals()
                except exceptions.SystemExit:
                    sys.exit(1)
                except:
                    print "WARNING: Unable to load " + str(plugin) + " plugin. Ignored."
                    print "   " + str(sys.exc_info()[0])
                    print "   " + str(sys.exc_info()[1])
                    print "   " + str(sys.exc_info()[2].tb_frame)

            sys.path.pop()

    def hasPlugin(self, pluginName):
        return (self.plugins.count(pluginName) > 0)

    def registerPlugin(self, pluginName):
        if self.plugins.count(pluginName) > 0:
            print "Error! Pluging %s already registered." % pluginName
            print
            print "This could happen if you have a plugin installed to several places that are"
            print "read by playground. Some plugin did violate the hasPlugin/registerPlugin"
            print "protocol of playground."
            sys.exit(1)
        else:
            self.plugins.append(pluginName)

    def registerCommand(self, command):
        if self.commands.has_key(command.name) > 0:
            print "Error! Command %s already registered." % command.name
            print
            print "This could happen if you have a plugin installed to several places that are"
            print "read by playground or if two plugins try to register a command with the same"
            print "name."
            sys.exit(1)
        else:
            self.commands[command.name] = command

    def isStaticBuild(self):
        return self.staticBuild

    def getBuildFlavour(self):
        return self.buildFlavour

    def getSconsOptions(self):
        return self.sconsOptions

    def getNumJobs(self):
        return self.numJobs

    def getOptParser(self):
        return self.optParser

    def getCommandQueue(self):
        return self.commandQueue

    def getOptions(self):
        return self.options

    def getProjects(self):
        return self.projects

    def checkForMissingProjects(self):
        """iterate over the projects in p, return a list of missing directory names.
        """
        return [project for project in self.projects.all if not os.path.isdir(project.getDir())]

    def updateMissingProjects(self, missingProjects):
        if not len(missingProjects):
            return

        print "Warning: According to 'config/projects.py' the following directories are missing:"
        for project in missingProjects:
            print "  " + project.getDir() + " (from URL: " + project.getRCSUrl() + ")"

        if self.userFeedback.askForConfirmation("Try fetch the according projects?"):
            self.getMissingProjects(missingProjects)
        else:
            print "Not trying to fetch missing projects."
            print "Exiting"
            sys.exit(0)

    def getMissingProjects(self, missingProjects):
        """for each directory name in dirs, try to resolve the archive and retrieve it via GNUArch.
        """

        for project in missingProjects:

            basedir = os.path.abspath(os.path.join(project.getDir(), ".."))

            print basedir

            if project.alias != None:
                newLink = os.path.join(basedir, project.alias)
                if os.path.exists(newLink) or os.path.islink(newLink):
                    print "\nError: For this project I need to make a symlink!!"
                    print "Symlink would be: " + project.getDir() + " -> "  + project.alias + " in " + os.getcwd()
                    print "Error: " + project.alias + " already exists. Please move it out of the way."
                    print "Run '" + " ".join(sys.argv) + "' afterwards again."
                    sys.exit(1)

            print "Fetching project: " + project.getRCSUrl()

            project.getRCS().get(project.getRCSUrl())

            if project.alias != None:
                curDir = os.getcwd()
                os.chdir(basedir)
                linkDest = project.getDir().split("/")[-1]
                os.symlink(linkDest, project.alias)
                os.chdir(curDir)

        self.fixConfigurationLinks()

    def fixConfigurationLinks(self):
        self.foreachProject(self._linkPrivatePy)
        self.foreachProject(self._linkPushMailRecipientsPy)

    def foreachProject(self, fun, **args):
        return self.foreachProjectIn(self.projects.all, fun, **args)

    def foreachProjectIn(self, projectList, fun, **args):
        """run function fun for each of the projects.

        change directory to each project directory, calling fun
        with the projects as parameter.
        """
        results = []
        for project in projectList:
            if not self.includeProject(project):
                continue

            cwd = os.path.abspath(os.curdir)
            os.chdir(project.getDir())

            results.append(ForEachResult(dirname = project.getDir(), result = fun(project, **args)))

            os.chdir(cwd)

        return results

    def includeProject(self, project):
        if self.ifExpr is None:
            return True

        # we evaluate --if expressions using the python eval function.
        # thus, any valid python expression may be used. python2.3 allows
        # us to specify a dictionary to be used as globals during evaluation.
        # that means, that we can build a dictionary with the test results
        # in advance, and use this dictionary later during evaluation.
        # to limit the test evaluation to tests that are only used in
        # the expression, we first search for used tests within the
        # expression string. this is done in the following lines. after that
        # we loop over the tokenized testNames and run the tests, filling
        # the context dictionary.
        #
        # this works, but is not very nice. python2.4 allows us to use
        # anything talking the getattr protocol to be used as context.
        # this would allow us to do real lazy evaluation of tests.
        # think of the following expression:
        #   --if="changed and ask"
        # using the current approach, the user would be asked for *every*
        # project. even if the 'changed' test fails for most of them...
        #
        # -> get python2.4 now, dude! \o/

        token = re.split('\W+', self.ifExpr)
        token = [it for it in token if it not in ('and', 'or', 'not', '')]
        token = sets.Set(token)

        context = {}
        for testName in token:
            tester = Tester(project)
            if not hasattr(tester, testName):
                print "Unknown test in --if expression:", testName
                sys.exit(1)

            context[testName] = getattr(tester, testName)()

        try:
            return eval(self.ifExpr, context)
        except SyntaxError, e:
            print "Syntax error in --if expression:", e
            sys.exit(1)

    def getDirectoryDepth(self, path):
        # calculate the depth with respect to the testbed dir
        normalizedPath = os.path.normpath(path)
        # by splitting at the slashes we can find the depth
        return len(normalizedPath.split(os.sep))

    def getRelativePathToPlayground(self, path):
        depth = self.getDirectoryDepth(path)
        return os.path.normpath(("/").join([".."]*depth))

    def readProjectsConfig(self):
        sys.path.append("config")
        foobar = {}
        if (self.configFile == "config/projects.py"):
            # Default value
            if not os.path.exists(self.configFile):
                os.symlink('projects.py.template', "config/projects.py")
        else:
            if not os.path.exists(self.configFile):
                print "Cannot open configuration file " + str(self.configFile)

        execfile(self.configFile, foobar)
        sys.path.remove("config")
        return Dict2Class(foobar)

    def _linkPrivatePy(self, project):
        if not project.getExe() in ["bin", "lib"]:
            return
        if not os.path.exists(os.path.join("config", "private.py")) and os.path.exists(os.path.join(".", "config")):
            os.symlink(os.path.join(self.getRelativePathToPlayground(project.getDir()), "..", "config", "private.py"),
                       os.path.join("config", "private.py"))

    def _linkPushMailRecipientsPy(self, project):
        path = project.getDir()

        if not os.path.exists(os.path.join("config", "pushMailRecipients.py")) and os.path.exists(os.path.join(".", "config")):
            os.symlink(os.path.join(self.getRelativePathToPlayground(project.getDir()), "..", "config", "pushMailRecipients.py"),
                       os.path.join("config", "pushMailRecipients.py"))

    def _setupCommandLineOptions(self):
        # modifying options
        self.optParser.add_option("-f", "--configFile",
                                  type="string", dest = "configFile", metavar = "FILE", default = "config/projects.py",
                                  help = "choose a configuration file (e.g., --configFile=config/projects.py)")

        self.optParser.add_option("-j", "--jobs",
                                  type = "int", dest = "jobs", default = 0,
                                  help = "use JOBS parallel compilation jobs", metavar = "JOBS")

        self.optParser.add_option("", "--flavour",
                                  type="string", dest = "flavour", metavar = "TYPE", default = "dbg",
                                  help = "choose a flavour (TYPE=[dbg|opt|prof|...]) to operate with.")

        self.optParser.add_option("", "--static",
                                  dest = "static", default = False,
                                  action = "store_true",
                                  help = "build static executable")

        self.optParser.add_option("", "--scons",
                                  dest = "scons", default = "",
                                  help="options forwarded to scons.")

        self.optParser.add_option("", "--if",
                                  type="string", dest = "if_expr", metavar = "EXPR", default = None,
                                  help = "restrict commands to affect only projects that match EXPR (can be: 'python', 'bin', 'lib', 'none', 'changed', 'scons', 'ask', 'bzr', 'tla').")
        self.optParser.add_option("", "--noAsk",
                                  action = "store_true", dest = "noAsk", default = False,
                                  help = "Do not ask user. Accept all default answers. Use this for automation.")


theCore = Core()

def getCore():
    return theCore

