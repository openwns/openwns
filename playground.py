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
import commands
import shutil
import sys
import glob

def installEnvironment():
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

import subprocess
import optparse
import re
import sets
import datetime
import wnsrc

class UserMadeDecision:

    def askForConfirmation(self, question):
        """ Returns true if user answers yes to the question"""
        answer = raw_input(question + " (Y/n) ")
        while answer.lower() not in  ["n", "y", '']:
            answer = raw_input(question + " (Y/n) ")
        return (answer.lower() == 'y') or (answer == '')

    def askForReject(self, question):
        """ Returns false if user answers yes to the question"""
        answer = raw_input(question + " (y/N) ")
        while answer.lower() not in  ["n", "y", '']:
            answer = raw_input(question + " (y/N) ")
        return (answer.lower() == 'n') or (answer == '')

class AcceptDefaultDecision:

    def askForConfirmation(self, question):
        """ Always returns true """
        return True

    def askForReject(self, question):
        """ Always retruns true """
        return True

userFeedback = UserMadeDecision()

#
# commands
#
class Tester:
    def __init__(self, project):
        self.project = project

    def python(self):
        return self.project.getExe() == 'python'

    def lib(self):
        return self.project.getExe() == 'lib'

    def bin(self):
        return self.project.getExe() == 'bin'

    def none(self):
        return self.project.getExe() is None

    def changed(self):
        f = os.popen('tla changes -d ' + self.project.getDir() + " 2>&1")
        output = f.read()
        result = f.close()
        if result is None:
            return False
        if os.WEXITSTATUS(result) != 1:
            print "Warning: Excluding dirty project", self.project.getDir()
            print output
            print
            print "Warning: Consider using ./playground --lint in advance."
            print
            return False
        return True

    def scons(self):
        return os.path.exists(os.path.join(self.project.getDir(), 'SConstruct'))

    def ask(self):
        return userFeedback.askForConfirmation("Execute command for project " + self.project.getDir() + " ?")

def includeProject(project):
    if options.if_expr is None:
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

    token = re.split('\W+', options.if_expr)
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
        return eval(options.if_expr, context)
    except SyntaxError, e:
        print "Syntax error in --if expression:", e
        sys.exit(1)

class ForEachResult:
    def __init__(self, dirname, result):
        self.dirname = dirname
        self.result = result

def foreachProject(projects, fun, **args):
    """run function fun for each of the projects.

       change directory to each project directory, calling fun
       with the projects as parameter.
    """
    results = []
    for project in projects:
        if not includeProject(project):
            continue

        cwd = os.path.abspath(os.curdir)
        os.chdir(project.getDir())

        results.append(ForEachResult(dirname = project.getDir(), result = fun(project, **args)))

        os.chdir(cwd)

    return results


def projectDepth(projectPath):
    # calculate the depth with respect to the testbed dir
    normalizedPath = os.path.normpath(projectPath)
    # by splitting at the slashes we can find the depth
    return len(normalizedPath.split(os.sep))

def relativePathToTestbed(projectPath):
    depth = projectDepth(projectPath)
    return os.path.normpath(("/").join([".."]*depth))

def checkForConflicts(projectDir):
    """Returns a list with confilct files"""
    result = []
    for (dirname, dirs, files) in os.walk(projectDir):
        # conflicts cannot occure in '{arch}' or ".arch-ids" directory
        if not "{arch}" in dirname and not ".arch-ids" in dirname:
            for f in files:
                if f.endswith("rej"):
                    result.append(os.path.join(dirname, f))
        else:
            dirs=[]

    return result

def checkForConflictsAndExit(projectDir):
    conflicts = checkForConflicts(projectDir)
    if len(conflicts) > 0:
        print "Error: %s has conflicts:" % (os.path.abspath(projectDir))
        print conflicts
        sys.exit(1)


def runCommand(command):
    fh = os.popen(command)
    line = fh.readline()
    while line:
        print line.strip('\n')
        line = fh.readline()
    return fh.close()

def runProjectHook(project, hookName):
    if not hasattr(project, hookName):
        return True

    hook = getattr(project, hookName)
    if not callable(hook):
        return True

    print "Running '%s' hook for project %s" % (hookName, project.getDir())
    return hook()

def missingCommand(playgroundEnvironment, arg = 'unused'):
    def run(project):
        print "Missing in", project.getDir(), "..."
        project.getRCS().missing(project.getRCSUrl() ,{"-s":""}).realtimePrint("  ")

    foreachProject(projects.all,
                   run)


def changesChecker(project):
    sys.stdout.write("Checking for changes in " + project.getDir() + " ...")
    sys.stdout.flush()
    changes = []
    foundChanges = False
    for line in project.getRCS().status({options.diffs:""}):
        if line.startswith('*') or line.strip(" ") == "":
            continue

        changes.append(line)
        foundChanges = True

    if foundChanges:
        sys.stdout.write(" " + str(len(changes)) + " files changed\n")
    else:
        sys.stdout.write(" no changes\n")
    return changes


def statusCommand(playgroundEnvironment, arg = 'unused'):
    def run(project):
        return changesChecker(project)

    print "Searching changes. A summary will be listed at the end ..."
    projectChanges = []
    projectChanges.extend(foreachProject(projects.all, run))

    print
    for ii in projectChanges:
        if len(ii.result) > 0:
            print "Changes in: " + ii.dirname
            for change in ii.result:
                print "  " + change


def docuCommand(playgroundEnvironment, arg = 'unused'):
    def run(project):
        if not project.generateDoc:
            return

        if not userFeedback.askForConfirmation("Do you want to install documentation for '" + project.getDir() + "'?"):
            return

        print "\nInstalling documentation for", project.getDir(), "..."

        command = 'scons %s docu; scons %s install-docu' % (options.scons, options.scons,)
        print "Executing:", command
        result = runCommand(command)
        if not result == None:
            raise "Documentation for " + project.getDir() +  " failed"


    foreachProject(projects.all,
                   run)
    createTestbedDocu(projects)


def createTestbedDocu(projects):
    stdin, stdout = os.popen4('doxygen -')
    rcs = projects.root.getRCS() 
    for i in file(os.path.join("doc", "config", "Doxyfile")):
        stdin.write(i)
    stdin.write('PROJECT_NAME="'+ rcs.getVersion() + '"\n')
    stdin.write('PROJECT_NUMBER="'+ rcs.getPatchLevel() + '<br>(archive: '+ rcs.getFQRN() +')"\n')
    stdin.close()
    line = stdout.readline()
    while line:
        print line.strip()
        line = stdout.readline()

    # copy all ppt stuff
    if os.path.isdir(os.path.join("sandbox", "default", "doc", "WNS", "ppt")):
        shutil.rmtree(os.path.join("sandbox", "default", "doc", "WNS", "ppt"))
    shutil.copytree(os.path.join("doc", "ppt"), os.path.join("sandbox", "default", "doc", "WNS", "ppt"))

    # copy all pdf stuff
    if os.path.isdir(os.path.join("sandbox", "default", "doc", "WNS", "pdf")):
        shutil.rmtree(os.path.join("sandbox", "default", "doc", "WNS", "pdf"))
    shutil.copytree(os.path.join("doc", "pdf"), os.path.join("sandbox", "default", "doc", "WNS", "pdf"))

    # copy all images
    if os.path.isdir(os.path.join("sandbox", "default", "doc", "WNS", "images")):
        shutil.rmtree(os.path.join("sandbox", "default", "doc", "WNS", "images"))
    shutil.copytree(os.path.join("doc", "images"), os.path.join("sandbox", "default", "doc", "WNS", "images"))

    # copy all flash movies
    if os.path.isdir(os.path.join("sandbox", "default", "doc", "WNS", "flash")):
        shutil.rmtree(os.path.join("sandbox", "default", "doc", "WNS", "flash"))
    shutil.copytree(os.path.join("doc", "flash"), os.path.join("sandbox", "default", "doc", "WNS", "flash"))

    writeDoxygenHeader(projects)

def writeDoxygenHeader(projects):

    # index.htm
    index = file(os.path.join("sandbox", "default", "doc", "index.htm"), "w")
    index.write("""
    <html><head><title>openWNS - The Wireless Network Simulator</title></head>
    <frameset rows="105,*">
    <frame marginwidth=0 marginheight=0 frameborder=0 src="head.htm">
    <frameset cols="250,*,250">
    <frame marginwidth=0 marginheight=0 frameborder=0 scrolling = "auto" src="left.htm">
    <frame marginwidth=0 marginheight=0 frameborder=0 src="WNS/index.htm" name="body">
    <frame marginwidth=0 marginheight=0 frameborder=0 src="right.htm">
    </frameset>
    </frameset>
    </html>
    """)

    # head.htm
    head = file(os.path.join("sandbox", "default", "doc", "head.htm"), "w")
    head.write("""
    <html><head><title>openWNS - The Wireless Network Simulator</title>
    <link href="WNS/doxygen.css" rel="stylesheet" type="text/css">
    <link href="WNS/tabs.css" rel="stylesheet" type="text/css">
    </head>
    <body>
    <table border=0 cellpadding=0 cellspacing=10 width=100%>
    <tr>
    <td width=25%><img src="WNS/images/openWNS.png"></td>
    <td width=50% valign=bottom align=center>
    <font size=+2><b>openWNS - The Wireless Network Simulator</b></font>
    </td>
    <td width=25% align=right><img src="WNS/images/RWTHAachen-ComNets.png"></td>
    </tr>
    <tr>
    <td colspan=3 width=100% height=1 bgcolor=black></td>
    </tr>
    </table>
    </body>
    </html>
    """)

    # right.htm (Menu on the right side)
    right = file(os.path.join("sandbox", "default", "doc", "right.htm"), "w")
    right.write("""
    <html><head><title>openWNS - Right Menu</title>
    <link href="WNS/doxygen.css" rel="stylesheet" type="text/css">
    <link href="WNS/tabs.css" rel="stylesheet" type="text/css">
    </head>
    <body>
    <font size=-1>
    """)

    right.write("<b>Framwork Documentation:</b><ul>")
    listOfProjects = []
    for i in projects.all:
        if os.path.normpath(i.getDir()).split(os.sep)[0] == "framework":
            rcs = i.getRCS()
            if os.path.exists(os.path.join("sandbox", "default", "doc", rcs.getVersion())):
                listOfProjects.append('<li><a target="body" href="'+rcs.getVersion()+'/index.htm">'+rcs.getVersion()+'</a>\n')

    listOfProjects.sort()
    for p in listOfProjects: right.write(p)
    right.write("""</ul>
    <b>Modules Documentation:</b>
    <ul>""")
    listOfProjects = []
    for i in projects.all:
        if os.path.normpath(i.getDir()).split(os.sep)[0] == "modules":
            rcs = i.getRCS()
            if os.path.exists(os.path.join("sandbox", "default", "doc", rcs.getVersion())):
                listOfProjects.append('<li><a target="body" href="'+rcs.getVersion()+'/index.htm">'+rcs.getVersion()+'</a>\n')

    listOfProjects.sort()
    for p in listOfProjects: right.write(p)
    right.write("</ul>")
    right.write("""
    </font></body>
    </html>
    """)

    # left.htm (Menu on the left side
    left = file(os.path.join("sandbox", "default", "doc", "left.htm"), 'w')
    left.write("""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html><head><meta http-equiv="Content-Type" content="text/html;charset=iso-8859-1">
    <title>WNS - Left Menu</title>
    <link href="WNS/doxygen.css" rel="stylesheet" type="text/css">
    <link href="WNS/tabs.css" rel="stylesheet" type="text/css">
    </head><body>
    <font size=-1>
    <b>General:</b>
    <ul>
    <li><a target="body" href="WNS/index.htm">Home</a></li>
    """)

    # generate from doc/pages.htm
    for line in file(os.path.join('sandbox', 'default', 'doc', 'WNS', 'pages.htm')):
        if line.startswith("<li>"):
            line = line.replace('class="el"', '')
            left.write(line.replace('href="', 'target="body" href="WNS/'))

    left.write("</ul></font><body></html>")


def installCommand(playgroundEnvironment, flavour, sandboxDir=""):
    def run(project):
        if project.getExe() == None:
            return

        print "Installing", project.getDir(), "..."

        linkPrivatePy("./", project)
        linkPushMailRecipientsPy("./", project)

        parallel_compiles = ''
        if options.jobs:
            parallel_compiles = '-j %d' % options.jobs

        executable = project.getExe()
        if options.static and executable == "lib":
            executable = 's'+executable

        command = ""
        if options.static:
            staticSConsOptions = 'static=1 '
            moduleNames = []
            # special handling for WNS-CORE
            if project.getExe() == 'bin':
                for pp in projects.all:
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
            command += ' '.join(('scons', 'sandboxDir='+sandboxDir, staticSConsOptions, options.scons, parallel_compiles, 'install-' + executable, 'flavour=' + flavour, ";"))
        else:
            raise("Unkown project.getExe() result: " + project.getExe())

        print "Executing:", command

        while True:
            if runProjectHook(project, 'prebuild'):
                result = runCommand(command)
                if result is None:
                    return

            print "Failed to install:", project.getDir()

            if not userFeedback.askForReject("Do you want to retry the install process?"):
                pass
            else:
                if userFeedback.askForReject("Do you want to abort the install process?"):
                    return
                else:
                    sys.exit(1)

    reorderedListOfProjects = projects.all
    if options.static:
        # reorder: first libs then bin
        # in fact there is only one binary: WNS-CORE
        reorderedListOfProjects = [it for it in projects.all if it.getExe() == "lib"] + [it for it in projects.all if it.getExe() == "bin"]
        reorderedListOfProjects += [it for it in projects.all if it not in reorderedListOfProjects]
    foreachProject(reorderedListOfProjects, run)

def updateCommand(playgroundEnvironment):
    projects = playgroundEnvironment['projects']
    checkForConflictsAndExit = playgroundEnvironment['checkForConflictsAndExit']

    myProject = projects.root
    if myProject.getRCS().isPinned():
        sys.stdout.write("\nSkipping module in %s, because it is pinned to %i\n\n"
                         % (myProject.getDir(), myProject.getRCS().getPinnedPatchLevel()))
        return
    sys.stdout.write("Checking for new patches in: %s ... " % ("./"))
    sys.stdout.flush()
    missing = str(myProject.getRCS().missing(myProject.getRCSUrl(), {"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        print "\nRetrieving new patches for './' ... "
        try:
            myProject.getRCS().update().realtimePrint()
        except:
            print "An RCS error occured."
            sys.exit(1)
    else:
        print "None"

    sys.stdout.write("Checking for new patches in: %s ... " % ("./framework/buildSupport"))
    sys.stdout.flush()
    missing = str(projects.buildSupport.getRCS().missing(projects.buildSupport.getRCSUrl(), {"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        checkForConflictsAndExit("./framework/buildSupport")
        print "\nRetrieving new patches for './framework/buildSupport/' ..."
        try:
            projects.buildSupport.getRCS().update().realtimePrint()
            checkForConflictsAndExit("./framework/buildSupport")
        except:
            print "An TLA error occured."
            sys.exit(1)
    else:
        print "None"

    # re-read projects configuration
    projects = readProjectsConfig()

def upgradeCommand(playgroundEnvironment, arg = 'unused'):
    updateCommand(playgroundEnvironment)

    # there may be new projects since config/projects.py got updated
    theProjects = playgroundEnvironment['projects']
    userFeedback = playgroundEnvironment['userFeedback']
    checkForConflictsAndExit = playgroundEnvironment['checkForConflictsAndExit']

    missingProjects = checkForMissingProjects(theProjects.all)
    updateMissingProjects(missingProjects)

    def run(project):
        arch = project.getRCS()
        if project.getRCS().isPinned():
            sys.stdout.write("\nSkipping module in %s, because it is pinned to %s\n\n"
                             % (project.getDir(), project.getRCS().getPinnedPatchLevel()))
            return
        sys.stdout.write("Checking for new patches in: %s ... " % (project.getDir()))
        sys.stdout.flush()
        missing = str(project.getRCS().missing(project.getRCSUrl(), {"-s":""}))
        if(missing != ""):
            print "Found:"
            print missing
            checkForConflictsAndExit(".")
            print "\nRetrieving new patches for '" + project.getDir() + "' ..."
            gnuArch = project.getRCS()

            treeVersion = gnuArch.getTreeVersion()
            if treeVersion != project.getFQRN():
                print "Warning: You're upgrading version: " + treeVersion
                print "The version specified for this directory is: " + project.getFQRN()
                print "It has been kept back. To change to the new version try './playground.py --dist-upgrade'"
                if not userFeedback.askForConfirmation("Continue ?"):
                    return
            try:
                gnuArch.update().realtimePrint()
                checkForConflictsAndExit(".")
            except:
                print "An TLA error occured."
                sys.exit(1)
        else:
            print "None"

    foreachProject(projects.all,
                   run)


def lintCommand(playgroundEnvironment, arg = 'unused'):
    def run(project):
        return linter(project)

    def linter(project):
        sys.stdout.write ("Linting" + project.getDir() + " ... ")
        result = str(project.getRCS().lint())
        if result == "":
            sys.stdout.write(" OK\n")
        else:
            sys.stdout.write(" Fail\n")
        return result

    theProjects = playgroundEnvironment['projects']

    print "Linting all project trees. A summary will be listed at the end ..."
    lintedResults = foreachProject(theProjects.all, run)
    print
    print
    for ii in lintedResults:
        if ii.result != "":
            print "Lints in " + ii.dirname + ":"
            print ii.result
            print
            print

def foreachCommand(playgroundEnvironment, command):
    def run(project):
        print "Running '%s' in %s ..." % (command, project.getDir())
        runCommand(command)

    foreachProject(projects.all,
                   run)

def cleanCommand(playgroundEnvironment, option):
    def remove(base, directory):
        delDir = os.path.join(base, directory)
        if os.path.exists(base):
            print "Cleaning", base, "..."
            if os.path.exists(delDir):
                print "deleting", delDir
                shutil.rmtree(delDir)
            else:
                print "nothing to do"

    def runCleanPristines(project):
        remove(os.path.abspath(os.getcwd()),
               os.path.join("{arch}", "++pristine-trees"))

    def runCleanObjs(project):
        if project.getExe() == None:
            return
	if options.static:
	    addPrint = " (static build)"
	    staticOption = " static=1"
            if project.getExe() == "lib":
                staticOption += " install-slib"
	else:
	    addPrint = ""
	    staticOption = " static=0"
        print "Cleaning objects for '" + options.flavour + "' of " + project.getDir() + addPrint
        runCommand("scons -c flavour=" + options.flavour + staticOption)

    def runCleanDocu(project):
        remove(os.path.abspath(os.getcwd()),
               "doxydoc")

    def runCleanExtern(project):
        if "/extern" in project.getFQRN():
            runCommand("scons clean")

    def runCleanBuildDirs(project):
        if project.getExe() in ["lib", "bin"]:
            remove(os.path.abspath(os.getcwd()), "build")

    if option == "pristine-trees" or option == "all":
        remove(os.getcwd(), os.path.join("{arch}", "++pristine-trees"))
        foreachProject(projects.all,
                       runCleanPristines)

    if option == "sandbox" or option == "all":
        remove("./", "sandbox")

    if option == "objs" or option == "all":
        foreachProject(projects.all,
                       runCleanObjs)

    if option == "docu" or option == "all":
        foreachProject(projects.all,
                       runCleanDocu)

    if option == "extern" or option == "all":
        foreachProject(projects.all,
                       runCleanExtern)

    if option == "build-dirs" or option == "all":
	foreachProject(projects.all,
	               runCleanBuildDirs)

def replayCommand(playgroundEnvironment, arg = 'unused'):
    sys.stdout.write("Checking for new patches in: %s ... " % ("./"))
    sys.stdout.flush()
    missing = str(projects.root.getRCS().missing(project.root.getRCSUrl(), {"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        print "\nRetrieving new patches for './' ... "
        try:
            projects.root.getRCS().replay().realtimePrint()
        except:
            print "An TLA error occured."
            sys.exit(1)
    else:
        print "None"

    sys.stdout.write("Checking for new patches in: %s ... " % ("./framework/buildSupport"))
    sys.stdout.flush()
    missing = str(projects.buildSupport.getRCS().missing(projects.buildSupport.getRCSUrl(),{"-s":""}))
    if(missing != ""):
        print "Found:"
        print missing
        checkForConflictsAndExit("./framework/buildSupport")
        print "\nRetrieving new patches for './framework/buildSupport/' ..."
        try:
            projects.buildSupport.getRCS().replay().realtimePrint()
            checkForConflictsAndExit("./framework/buildSupport")
        except:
            print "An TLA error occured."
            sys.exit(1)
    else:
        print "None"

    def run(project):
        sys.stdout.write("Checking for new patches in: %s ... " % (project.getDir()))
        sys.stdout.flush()
        missing = str(project.getRCS().missing(project.getRCSUrl(), {"-s":""}))
        if(missing != ""):
            print "Found:"
            print missing
            checkForConflictsAndExit(".")
            print "\nRetrieving new patches for '" + project.getDir() + "' ..."
            gnuArch = project.getRCS()
            treeVersion = gnuArch.getTreeVersion()
            if treeVersion != project.getFQRN():
                print "Warning: You're upgrading version: " + treeVersion
                print "The version specified for this directory is: " + project.getFQRN()
                print "It has been kept back. To change to the new version try './playground.py --dist-upgrade'"
                if not userFeedback.askForConfirmation("Continue ?"):
                    return
            try:
                gnuArch.replay().realtimePrint()
                checkForConflictsAndExit(".")
            except:
                print "An TLA error occured."
                sys.exit(1)
        else:
            print "None"

    foreachProject(projects.all,
                   run)

def runTestsCommand(playgroundEnvironment, arg = "unused"):
    # create test collector
    import pywns.WNSUnit

    tests = []
    for project in projects.all:
        if os.path.normpath(project.getDir()).split(os.sep)[0] == "tests" and \
               os.path.normpath(project.getDir()).split(os.sep)[1] == "system":
            tests.append(project)

    testCollector = pywns.WNSUnit.SystemTestCollector(suiteConfig = "systemTest.py",
                                                      suiteName = "testSuite")
    testCollector.setTests(tests)

    # Add PyConfig unit tests
    pyUnit = pywns.WNSUnit.ExternalProgram(dirname = "tests/unit/PythonUnitTests/",
                                           command = "./runPythonUnitTests.py -v",
                                           description = "PyConfig Unit Tests",
                                           includeStdOut = True)
    testCollector.addTest(pyUnit)


    # Add C++ unit tests

    cppUnit = pywns.WNSUnit.ExternalProgram(dirname = "tests/unit/unitTests/",
                                            command = options.executable + " -f config.py -t -y'WNS.masterLogger.backtrace.enabled=True'",
                                            description = "C++ unit tests",
                                            includeStdOut = True)
    testCollector.addTest(cppUnit)

    pywns.WNSUnit.verbosity = 2

    # you can get the beast even more verbose by enabling this:
    # testCollector.testRunner.verbosity = 2

    print "Starting test suites ..."
    print "NOTE: you may see slow progress since the tests run simulations"

    result = testCollector.run()
    if (len(result.errors) == 0) and (len(result.failures) == 0):
        sys.exit(0)
    else:
        sys.exit(1)

def runLongTestsCommand(playgroundEnvironment, arg = "unused"):
    # create test collector
    import pywns.WNSUnit

    tests = []
    for project in projects.all:
        if os.path.normpath(project.getDir()).split(os.sep)[0] == "tests" and \
               os.path.normpath(project.getDir()).split(os.sep)[1] == "system":
            tests.append(project)

    testCollector = pywns.WNSUnit.SystemTestCollector(suiteConfig = "systemLongTest.py",
                                                      suiteName = "testSuite")
    testCollector.setTests(tests)

    pywns.WNSUnit.verbosity = 2

    # you can get the beast even more verbose by enabling this:
    # testCollector.testRunner.verbosity = 2

    print "Starting test suites ..."
    print "NOTE: you may see slow progress since the tests run simulations"

    result = testCollector.run()
    if (len(result.errors) == 0) and (len(result.failures) == 0):
        sys.exit(0)
    else:
        sys.exit(1)

def memcheckUnitTestsCommand(playgroundEnvironment, arg = "unused"):
    import pywns.MemCheck
    r = pywns.MemCheck.Runner(args=["./openwns", "-tv"], cwd="tests/unit/unitTests")
    returncode = r.run()
    sys.exit(returncode)

def sanityCheckCommand(playgroundEnvironment, arg = "unused"):

    def sanityCheckRunner(fun, message, arg = "unused"):
        print message
	answer = ""
        # run once
        fun(arg)
        # run again upon user's request
        while not userFeedback.askForReject("Do you want to fix something and run again?"):
            fun(arg)

    sanityCheckRunner(lintCommand, "running ./playground.py --lint" )
    sanityCheckRunner(statusCommand, "running ./playground.py --changes" )

    print "running ./playground.py --install=dbg"
    installCommand("dbg")

    print "running ./playground.py --install=opt"
    installCommand("opt")

    runTestsCommand()

#
# tools
#

def Stripper(something):
    """iterate over something, yielding stripped, non-empty elements, that don't start with a hash.
    """

    for it in something:
        it = it.strip()
        if len(it) and not it.startswith("#"):
            yield it


def checkForMissingProjects(projects):
    """iterate over the projects in p, return a list of missing directory names.
    """
    return [project for project in projects if not os.path.isdir(project.getDir())]


def getMissingProjects(missingProjects):
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

        linkPrivatePy(project.getDir(), project)
        linkPushMailRecipientsPy(project.getDir(), project)

def linkPrivatePy(path, project):
    if not project.getExe() in ["bin", "lib"]:
        return
    if not os.path.exists(os.path.join(path, "config", "private.py")) and os.path.exists(os.path.join(path, "config")):
        os.symlink(os.path.join(relativePathToTestbed(project.getDir()), "..", "config", "private.py"),
                   os.path.join(path, "config", "private.py"))

def linkPushMailRecipientsPy(path, project):
    if not os.path.exists(os.path.join(path, "config", "pushMailRecipients.py")) and os.path.exists(os.path.join(path, "config")):
        os.symlink(os.path.join(relativePathToTestbed(project.getDir()), "..", "config", "pushMailRecipients.py"),
                   os.path.join(path, "config", "pushMailRecipients.py"))

def updateMissingProjects(missingProjects):
    if not len(missingProjects):
        return

    print "Warning: According to 'config/projects.py' the following directories are missing:"
    for project in missingProjects:
        print "  " + project.getDir() + " (from URL: " + project.getRCSUrl() + ")"

    if userFeedback.askForConfirmation("Try fetch the according projects?"):
        getMissingProjects(missingProjects)
    else:
        print "Not trying to fetch missing projects."
        print "Exiting"
        sys.exit(0)

#
# main
#

def readProjectsConfig():
    sys.path.append("config")
    foobar = {}
    if (options.configFile == "config/projects.py"):
        # Default value
        if not os.path.exists(options.configFile):
            os.symlink('projects.py.template', "config/projects.py")
    else:
        if not os.path.exists(options.configFile):
            print "Cannot open configuration file " + str(options.configFile)

    print "Using configuration file: %s" % options.configFile 
    execfile(options.configFile, foobar)
    sys.path.remove("config")
    return Dict2Class(foobar)


class Dict2Class:
    def __init__(self, dictionary):
        for key in dictionary.iterkeys():
            if not key.startswith("__"):
                self.__dict__[key] = dictionary[key]

class CommandQueue:
    def __init__(self):
        self.queue = []

    def append(self, option, opt, arg, parser, command):

        self.queue.append((command, arg, option))

    def run(self):
        global projects
        for command, arg, option in self.queue:
            command(globals(), arg)

def loadPlugins(parser, queue):
    def loadPluginsInDir(pluginsDir, parser, queue):
        if os.path.exists(pluginsDir):
            for (dirname, plugins, files) in os.walk(pluginsDir):
                break

            if plugins.count('.arch-ids') > 0:
                plugins.remove('.arch-ids')

            sys.path.append(pluginsDir)
            for plugin in plugins:
                try:
                    exec "import " + str(plugin) in globals(), locals()
                    funcPtr = eval(str(plugin) + ".addCommandLineOptions")
                    funcPtr(parser, queue)
                except:
                    print "WARNING: Unable to load " + str(plugin) + " plugin. Ignored."
                    print sys.exc_info()[0]
                    print sys.exc_info()[1]
                    print sys.exc_info()[2].tb_frame

        sys.path.pop()

    # Add plugins
    loadPluginsInDir(os.path.join(".", "framework", "PyWNS--main--1.0", "playgroundPlugins"), parser, queue)
    loadPluginsInDir(os.path.join(os.environ["HOME"], ".wns", "playgroundPlugins"), parser, queue)

if __name__ == "__main__":

    usage  = "usage: %prog command [options]\n\n"
    usage += "The list below shows all commands and available options.\n"
    usage += "The options that might be used together with a command are list in brackets."
    parser = optparse.OptionParser(usage = usage)

    queue = CommandQueue()

    options = None
    projects = None

    # commands
    parser.add_option("", "--install",
                      type="string", metavar = "FLAVOUR",
                      action="callback", callback = queue.append,
                      callback_args = (installCommand,),
                      help="install all projects with flavour FLAVOUR. (-f, --if, -j, --static, --scons)")

    parser.add_option("", "--create",
                      type="string", metavar = "FLAVOUR",
                      action="callback", callback = queue.append,
                      callback_args = (installCommand,),
                      help="alias for --install")

    parser.add_option("", "--upgrade",
                      action="callback", callback = queue.append,
                      callback_args = (upgradeCommand,),
                      help="update all projects (-f, --if)")

    parser.add_option("", "--missing",
                      action="callback", callback = queue.append,
                      callback_args = (missingCommand,),
                      help="search for missing patches (-f, --if)")

    parser.add_option("", "--sanityCheck",
                      action="callback", callback = queue.append,
                      callback_args = (sanityCheckCommand,),
                      help="Runs: --lint, --changes, --install=dbg, --install=opt, --runTests (None)")

    parser.add_option("", "--runTests",
                      action="callback", callback = queue.append,
                      callback_args = (runTestsCommand,),
                      help="runs the tests found in 'tests' (--executable)")

    parser.add_option("", "--runLongTests",
                      action="callback", callback = queue.append,
                      callback_args = (runLongTestsCommand,),
                      help="runs the tests found in 'longTests' (--executable)")

    parser.add_option("", "--memcheckUnitTests",
                      action="callback", callback = queue.append,
                      callback_args = (memcheckUnitTestsCommand,),
                      help="runs memory check (leaks, uninitialized reads, ...) for unit tests (--executable)")

    parser.add_option("", "--replay",
                      action="callback", callback = queue.append,
                      callback_args = (replayCommand,),
                      help="replay all projects (--f, -if)")

    parser.add_option("", "--docu",
                      action="callback", callback = queue.append,
                      callback_args = (docuCommand,),
                      help="create documentation for all projects (-f, --if)")

    parser.add_option("", "--lint",
                      action="callback", callback = queue.append,
                      callback_args = (lintCommand,),
                      help="lint project trees (-f, --if)")

    parser.add_option("", "--update",
                      action="callback", callback = queue.append,
                      callback_args = (updateCommand,),
                      help="update playground (None)")

    parser.add_option("", "--changes",
                      action="callback", callback = queue.append,
                      callback_args = (statusCommand,),
                      help="show changes for each project (-f, --if, --diffs)")

    parser.add_option("", "--clean",
                      type="string", metavar = "OPTION",
                      action="callback", callback = queue.append,
                      callback_args = (cleanCommand,),
                      help = "clean up OPTION: [pristine-trees, objs, sandbox, docu, extern, build-dirs, all] (-f, --if, --flavour, --static)")
    parser.add_option("", "--foreach",
                      type="string", metavar = "COMMAND",
                      action="callback", callback = queue.append,
                      callback_args = (foreachCommand,),
                      help="execute COMMAND in each project (-f, --if)")

    # modifying options
    parser.add_option("-f", "--configFile",
                      type="string", dest = "configFile", metavar = "FILE", default = "config/projects.py",
                      help = "choose a configuration file (e.g., --configFile=config/projects.py)")

    parser.add_option("-j", "--jobs",
                      type = "int", dest = "jobs", default = 0,
                      help = "use JOBS parallel compilation jobs", metavar = "JOBS")

    parser.add_option("", "--diffs",
                      action = "store_const", dest = "diffs", const = '--diffs', default = '',
                      help=" when using --changes, show diffs of changed files.")

    parser.add_option("", "--flavour",
                      type="string", dest = "flavour", metavar = "TYPE", default = "dbg",
                      help = "choose a flavour (TYPE=[dbg|opt|prof|...]) to operate with.")

    parser.add_option("", "--static",
                      dest = "static", default = False,
                      action = "store_true",
                      help = "build static executable")

    parser.add_option("", "--scons",
                      dest = "scons", default = "",
                      help="options forwarded to scons.")

    parser.add_option("", "--if",
                      type="string", dest = "if_expr", metavar = "EXPR", default = None,
                      help = "restrict commands to affect only projects that match EXPR (can be: 'python', 'bin', 'lib', 'none', 'changed', 'scons', 'ask').")
    parser.add_option("", "--noAsk",
                      action = "store_true", dest = "noAsk", default = False,
                      help = "Do not ask user. Accept all default answers. Use this for automation.")

    parser.add_option("", "--executable",
                      type="string", dest = "executable", default = "./openwns",
                      help = "The executable that is to be called by the respective command (default : \"./openWNS\")")

    loadPlugins(parser, queue)

    options, args = parser.parse_args()
    if len(args):
        parser.print_help()
        sys.exit(1)

    if options.noAsk:
        userFeedback = AcceptDefaultDecision()

    projects = readProjectsConfig()

    if not os.path.exists(os.path.join('config', 'private.py')):
        os.symlink('private.py.template', os.path.join('config', 'private.py'))

    missingProjects = checkForMissingProjects(projects.all)
    updateMissingProjects(missingProjects)

    sys.path.append('framework/buildSupport')
    import wnsbase.RCS as RCS
    import FilePatcher
    sys.path.remove('framework/buildSupport')


    # install necessary files
    # must happen after missing projects ...
    for command, sourcePath in projects.prereqCommands:
        savedDir = os.getcwd()
        os.chdir(sourcePath)
        stdin, stdout = os.popen4(command)
        line = stdout.readline()
        while line:
            line = stdout.readline()
            os.chdir(savedDir)

    if not len(queue.queue):
        parser.print_help()
        sys.exit(0)

    queue.run()

    sys.exit(0)
