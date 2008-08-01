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

class CPPDocuCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog cppdocu\n\n"
        rationale = "Build all in one project CPP documentation."

        usage += rationale
        usage += """ Build the CPP documentation for the whole project. The created documentation will
be placed in ./doxydoc.
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "cppdocu", rationale, usage)
        self.examplesPath = ".doxydocExamples"

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

        # remove old examples
        print "Preparing examples."
        print "Removing old examples."
        shutil.rmtree(self.examplesPath, True)
        os.mkdir(self.examplesPath)
        for project in docProjects:
            print "Generating examples for " + project.getDir()
            generateExamples(os.path.join(project.getDir(), "src"), self.examplesPath)

        # find the right doxygen file
        dirNameOfThisModule = os.path.dirname(__file__)
        doxygenFileName = os.path.join(dirNameOfThisModule, "Doxyfile")
        # try if we have a directory "doc". This is the documentation
        # of the SDK. If available use documentation from there.
        masterDocDoxyfile = os.path.join(masterDocumentationProject.getDir(), "config/Doxyfile")
        if os.path.exists(masterDocDoxyfile):
            doxygenFileName = masterDocDoxyfile

        # read the doxygen file and modify according to our needs ...
        doxygenConfig = DoxygenConfigParser(doxygenFileName)

        # force output to doxdoc
        doxygenConfig.set("OUTPUT_DIRECTORY", "doxydoc")
        doxygenConfig.set("HTML_OUTPUT", "html")
        doxygenConfig.set("LATEX_OUTPUT", "latex")

        for project in docProjects:
            # default path to source files
            srcPath = os.path.join(project.getDir(), "src")
            if os.path.exists(srcPath):
                doxygenConfig.append("INPUT", srcPath)

            # default path to documentation files
            docPath = os.path.join(project.getDir(), "doc")
            if os.path.exists(docPath):
                doxygenConfig.append("INPUT", docPath)

            # default path to images
            imgPath = os.path.join(project.getDir(), "doc/pics")
            if os.path.exists(imgPath):
                doxygenConfig.append("IMAGE_PATH", imgPath)

            doxygenConfig.append("STRIP_FROM_INC_PATH", os.path.join(os.getcwd(), project.getDir(), "src"))

        doxygenConfig.append("FILE_PATTERNS", "*.hpp *.cpp *.txt *.h")
        doxygenConfig.append("EXAMPLE_PATH", self.examplesPath)
        doxygenConfig.append("STRIP_FROM_PATH", os.getcwd())
        doxygenConfig.append("STRIP_FROM_INC_PATH", os.getcwd())
        doxygenConfig.append("ALIASES", 'pyco{1}="<dl><dt><b>Configuration Class:</b></dt><dd><A HREF=\\"PyCoDoc/PyConfig.\\1-class.html\\">\\1</A></dd></dl>"')
        doxygenConfig.append("ALIASES", 'pycoshort{1}="<A HREF=\\"PyCoDoc/PyConfig.\\1-class.html\\">\\1</A>"')
        doxygenConfig.append("MSCGEN_PATH", "./bin")

        # if the masterProject has a special header.htm will use this as header
        customHeader = os.path.join(masterDocumentationProject.getDir(), "config/header.htm")
        if os.path.exists(customHeader):
            doxygenConfig.set("HTML_HEADER", customHeader)

        # feed configuration to doxygen on stdin
	print "Calling doxygen ... please wait: 'doxygen -'"
        doxygenProcess = subprocess.Popen('doxygen -',
                                          shell=True,
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          close_fds=True)
        stdIn = doxygenProcess.stdin
        stdOutAndErr = doxygenProcess.stdout
	for i in doxygenConfig.options():
		conf = i.upper() + " = " + doxygenConfig.get(i) + "\n"
		stdIn.write(conf)
	stdIn.close()
        for line in stdOutAndErr:
		print line.strip()
        print "Done!"
        doxygenProcess.wait()
        if doxygenProcess.returncode != 0:
            raise Exception("Doxygen failed to create the documentation.")
        print "Copying files to sandbox/default/doc"
        if os.path.exists("sandbox/default/doc"):
            shutil.rmtree("sandbox/default/doc")

        shutil.copytree("doxydoc/html", "sandbox/default/doc")


def processFile(path, fileName, dstPath):
    """Search a file for examples and store them at dstPath.
    """
    start_re = re.compile(r'\s*//\s*begin\s+example\s+"(.+)".*')
    stop_re = re.compile(r'\s*//\s*end\s+example.*')

    fullFileName = os.path.join(path, fileName)

    unquote = False
    example = None
    for line in file(fullFileName):
        match = start_re.match(line)
        if match is not None:
	    unquote = "unquote" in line
            exampleName = match.group(1)
            example = []
            continue

        match = stop_re.match(line)
        if match is not None:
            example = textwrap.dedent(''.join(example))
            example = example.replace('CPPUNIT_', '')

            exampleFileName = os.path.join(dstPath, exampleName)
            fd = os.open(exampleFileName, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            f = os.fdopen(fd, "w")
            f.write(example)

            example = None
            continue

        if example is not None:
	    if unquote:
		    line = line.strip().lstrip('"').rstrip('"').rstrip('\\n').replace('\\"', '"')
		    line += "\n"
            example.append(line)


def generateExamples(path, dst):
    """Search all *.{cpp|hpp} files in path for examples.

       Every example found will be written to a file with the name
       given at the 'begin example' tag.
       All the example files will be stored in the directory dst.
    """

    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.hpp') or f.endswith('.cpp'):
                processFile(root, f, dst)

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
