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

import wnsbase.playground.Core
import wnsbase.playground.Project
import shutil
import ConfigParser
import StringIO
import os.path
import wnsrc
import re
import textwrap
import subprocess

from wnsbase.playground.builtins.CPPDocumentation.CPPDocumentation import prepareExamples

class CreateManualsCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog cppdocu\n\n"
        rationale = "Build all in one project CPP documentation."

        usage += rationale
        usage += """ Build the CPP documentation for the whole project. The created documentation will
be placed in ./doxydoc.
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "createmanuals", rationale, usage)

        self.workingdir = '.createManualsWorkingDir'

    def run(self):
        core = wnsbase.playground.Core.getCore()
        print "Identifying projects for documentation ..."
        # find all documentation projects:
        docProjects = []
        masterDocumentationProject = None
        for project in core.getProjects().all:
            if isinstance(project, (wnsbase.playground.Project.Library, wnsbase.playground.Project.Binary, wnsbase.playground.Project.Documentation)):
                print "... found: " + project.getDir()
                docProjects.append(project)
                if isinstance(project, wnsbase.playground.Project.MasterDocumentation):
                    # we can have only 1 (in words: one) master documentation project
                    assert masterDocumentationProject == None
                    masterDocumentationProject = project

        # we need exactly one master documentation project
        assert masterDocumentationProject != None

        import doxygenParser
        p = doxygenParser.Parser()

        # remove old working dir
        shutil.rmtree(self.workingdir, True)
        os.mkdir(self.workingdir)

        prepareExamples(self.workingdir, docProjects)

        cur = os.getcwd()
        os.chdir(masterDocumentationProject.getDir())

        retcode = subprocess.call("make latex", shell=True)

        if retcode != 0:
            print "\n\nThere were errors during processing of documentation\n\n"
            exit(1)

        os.chdir(os.path.join(masterDocumentationProject.getDir(), "build", "latex"))

        retcode = subprocess.call("make all-pdf", shell=True)

        if retcode != 0:
            print "\n\nThere were errors when executin latex\n\n"
            exit(1)

        os.chdir(cur)

#         for project in docProjects:
#             print "Finding documentation pages for " + project.getDir()
#             findDocumentation(p, os.path.join(project.getDir(), "src"))
#             findDocumentation(p, os.path.join(project.getDir(), "doc"))

#         # Create the manual structure. Note that swallow automatically shifts pages to sections,
#         # sections to subsections, etc. So that the swalloed node is one level below the
#         # swallower in the document hierarchy

#         document = doxygenParser.createRoot()

#         gs = document.swallow(doxygenParser.createPage("createmanuals_gettingstarted", "Getting Started"))
#         gs.swallow(p.root.getChildByName("prerequisites"))
#         gs.swallow(p.root.getChildByName("download"))
#         gs.swallow(p.root.getChildByName("installation"))
#         gs.swallow(p.root.getChildByName("SDKLayout"))

#         sdk = document.swallow(doxygenParser.createPage("createmanuals_sdk", "The Software Developer's Kit (SDK)"))
#         sdk.swallow(p.root.getChildByName("wns_documentation_playground"))
#         sdk.swallow(p.root.getChildByName("wns_documentation_branchingandmerging"))
#         sdk.swallow(p.root.getChildByName("wns_documentation_performancetips"))

#         sp = document.swallow(doxygenParser.createPage("createmanuals_simulationplatform", "The Simulation Platform"))
#         sp.swallow(p.root.getChildByName("schedulerBestPractices"))
#         sp.swallow(p.root.getChildByName("wns_documentation_randomnumberdistributions"))
#         sp.swallow(p.root.getChildByName("wns_probe_bus_probing"))
#         sp.swallow(p.root.getChildByName("wns_probe_bus_contextcollector"))
#         sp.swallow(p.root.getChildByName("openwns_evaluation"))
#         sp.swallow(p.root.getChildByName("BuildingSub"))
#         sp.swallow(p.root.getChildByName("HowToWriteFiniteStateMachine"))

#         md = document.swallow(doxygenParser.createPage("createmanuals_moduledocs", "Module Documentation"))
#         md.swallow(p.root.getChildByName("wns_ip_overview"))
        
#         wc = document.swallow(doxygenParser.createPage("createmanuals_writing", "Writing Code"))
#         wc.swallow(p.root.getChildByName("wns_documentation_codingguidelines"))
#         wc.swallow(p.root.getChildByName("wns_documentation_documentationvscomments"))
#         wc.swallow(p.root.getChildByName("wns_documentation_createnewmodule"))
#         wc.swallow(p.root.getChildByName("wns_documentation_writingunittests"))
#         wc.swallow(p.root.getChildByName("wns_documentation_clean"))

#         document.swallow(p.root.getChildByName("wns_documentation_codingguidelines_short"))
#         document.swallow(p.root.getChildByName("wns_documentation_networksimulators"))

#         i = 0
#         for pageName in document.getChildNames():
#             out = open(os.path.join(self.workingdir,'%d_%s.txt' % (i, pageName)),"w")
#             out.write("/**\n")
#             document.getChildByName(pageName).writeToFile(out, release=False)
#             out.write("*/")
#             out.close()

#             i += 1

#         # find the right doxygen file
#         dirNameOfThisModule = os.path.dirname(__file__)
#         doxygenFileName = os.path.join(dirNameOfThisModule, "Doxyfile")
#         # try if we have a directory "doc". This is the documentation
#         # of the SDK. If available use documentation from there.
#         masterDocDoxyfile = os.path.join(masterDocumentationProject.getDir(), "config/Doxyfile")
#         if os.path.exists(masterDocDoxyfile):
#             doxygenFileName = masterDocDoxyfile

#         # read the doxygen file and modify according to our needs ...
#         doxygenConfig = DoxygenConfigParser(doxygenFileName)

#         # force output to doxdoc
#         doxygenConfig.set("OUTPUT_DIRECTORY", os.path.join(self.workingdir,"doxydoc"))
#         doxygenConfig.set("INPUT", self.workingdir)
#         doxygenConfig.append("EXAMPLE_PATH", self.workingdir)
#         doxygenConfig.set("FILE_PATTERNS", "*.txt")
#         doxygenConfig.append("MSCGEN_PATH", "./bin")
#         doxygenConfig.append("LATEX_HEADER", os.path.join(masterDocumentationProject.getDir(), "config", "header.tex"))

#         # feed configuration to doxygen on stdin
# 	print "Calling doxygen ... please wait: 'doxygen -'"
#         doxygenProcess = subprocess.Popen('doxygen -',
#                                           shell=True,
#                                           stdout=subprocess.PIPE,
#                                           stdin=subprocess.PIPE,
#                                           stderr=subprocess.STDOUT,
#                                           close_fds=True)
#         stdIn = doxygenProcess.stdin
#         stdOutAndErr = doxygenProcess.stdout
# 	for i in doxygenConfig.options():
# 		conf = i.upper() + " = " + doxygenConfig.get(i) + "\n"
# 		stdIn.write(conf)
# 	stdIn.close()
#         usedConfig = open(os.path.join(self.workingdir,'Doxyfile'), "w")
#         for i in doxygenConfig.options():
#             conf = i.upper() + " = " + doxygenConfig.get(i) + "\n"
#             usedConfig.write(conf)
# 	usedConfig.close()
#         for line in stdOutAndErr:
# 		print line.strip()
#         print "Done!"
#         doxygenProcess.wait()
#         if doxygenProcess.returncode != 0:
#             raise Exception("Doxygen failed to create the documentation.")

#         shutil.copy(os.path.join(dirNameOfThisModule, "Makefile"),
#                     os.path.join(self.workingdir, "doxydoc", "latex"))

#         # Copy our custom stylesheet
#         shutil.copy(os.path.join(masterDocumentationProject.getDir(), "config", "doxygen.sty"),
#                     os.path.join(self.workingdir, "doxydoc", "latex"))

#         cur = os.getcwd()
#         os.chdir(os.path.join(self.workingdir, 'doxydoc', 'latex'))

#         retcode = subprocess.call("make", shell=True)
#         os.chdir(cur)

#         print "Generated your manual at %s" % os.path.join(self.workingdir, "doxydoc", "latex", "refman.pdf")

def processFile(parser, path, fileName):
    curr = os.getcwd()
    fullFileName = os.path.join(path, fileName)
    fullFileName = fullFileName.replace(curr, ".")
    parser.parseFile(fullFileName)

def findDocumentation(parser, path):

    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.hpp') or f.endswith('.cpp') or f.endswith('.txt'):
                processFile(parser, root, f)

class DoxygenConfigParser:
    """Parser for doxygen config files"""
    def __init__(self, filename):
        self.parser = ConfigParser.ConfigParser()
        text = open(filename).read()
        # the Python's ConfigParser expects the file to have
        # at least one section. Doxygen's config files don't
        # have such a section. Hence we prepend a dummy section
        newFileContent = StringIO.StringIO("[dummy]\n" + text)
        self.parser.readfp(newFileContent, filename)

    def get(self, parameter):
        """Provides access to the parameters of a doxygen config file"""
        return self.parser.get("dummy", parameter)

    def getSplit(self, parameter):
        """Provides access to the parameters of a doxygen config file (returns list of parameters)"""
        return self.parser.get("dummy", parameter).replace("\\", "").replace("\n", "").split()

    def options(self):
        return self.parser.options("dummy")

    def has_option(self, parameter):
        return self.parser.has_option("dummy", parameter)

    def set(self, parameter, value):
        self.parser.set("dummy", parameter, self.__listToString(value))

    def append(self, parameter, value):
        oldParameters = ""
        if self.has_option(parameter):
            oldParameters = self.get(parameter)

        self.set(parameter, oldParameters + " " + self.__listToString(value))

    def prepend(self, parameter, value):
        oldParameters = ""
        if self.has_option(parameter):
            oldParameters = self.get(parameter)

        self.set(parameter, self.__listToString(value) + " " + oldParameters)

    def __listToString(self, any):
        if not isinstance(any, str):
            return " ".join(any)
        else:
            return any
