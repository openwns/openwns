#!/usr/bin/env python2.4
import sys
import os
import unittest

sandboxPath = '../../../sandbox'

class PythonUnitTests:
    path = sandboxPath + '/dbg/lib/PyConfig'
    allTests = unittest.TestSuite()

    def __init__(self):
        sys.path.append(self.path)
        for root, dirs, files in os.walk(self.path):
            if root.find('/tests') != -1:
                for fileName in files:
                    if fileName.endswith('py') and fileName != '__init__.py':
                        pathName = os.path.join(root, fileName)
                        self.addModule(pathName)

    def addModule(self, modulePath):
        moduleName = modulePath.replace(self.path + '/', '').replace('.py', '').replace('/', '.')
        mod = __import__(moduleName, globals(), locals(), [''])
        suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
        self.allTests.addTest(suite)

    def runTests(self, v):
        return unittest.TextTestRunner(verbosity=v).run(self.allTests)

if "-v" in sys.argv:
    verbosity = 2
else:
    verbosity = 1

if PythonUnitTests().runTests(verbosity).wasSuccessful():
    sys.exit(0)
else:
    sys.exit(1)
