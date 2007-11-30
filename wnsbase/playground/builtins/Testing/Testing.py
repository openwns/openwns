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
from wnsbase.playground.Tools import *
import pywns.MemCheck
import pywns.WNSUnit

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

def runTestsCommand(arg = "unused"):
    # create test collector
    import pywns.WNSUnit

    tests = []
    for project in core.getProjects().all:
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
                                            command = core.getOptions().executable + " -f config.py -t -y'WNS.masterLogger.backtrace.enabled=True'",
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

def runLongTestsCommand(arg = "unused"):
    # create test collector
    import pywns.WNSUnit

    tests = []
    for project in core.getProjects().all:
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

def memcheckUnitTestsCommand(arg = "unused"):
    r = pywns.MemCheck.Runner(args=[core.getOptions().executable, "-tv"], cwd="tests/unit/unitTests")
    returncode = r.run()
    sys.exit(returncode)
