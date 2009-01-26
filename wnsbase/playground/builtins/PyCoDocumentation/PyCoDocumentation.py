import os
import shutil
import wnsbase.playground.plugins.Command
from wnsbase.playground.Tools import *
import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

class PyCoDocumentationCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog pycodocu\n\n"
        rationale = "Creates documentation for the PyConfig configuration tree"

        usage += rationale

        usage += """

EpyDoc is used to create the documentation of all PyConfig classes located under
sandbox/FLAVOUR/lib/PyConfig. You can find the documentation in sandbox/FLAVOUR/PyCoDoc.

Note: EpyDoc currently produces a lot of warnings.
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "pycodocu", rationale, usage)

        self.optParser.add_option("", "--flavour",
                                  type="string", dest = "flavour", metavar = "TYPE", default = "dbg",
                                  help = "choose a flavour (TYPE=[dbg|opt|prof|...]) to operate with.")

    def run(self):

        print "Install PyConfig"
        command = "scons %sPyConfig" % self.options.flavour
        result = runCommand(command)
        if not (result is None):
            print "Could not execute %s" % command

        command = "touch sandbox/%s/lib/PyConfig/__init__.py" % self.options.flavour
        result = runCommand(command)
        if not (result is None):
            print "Could not execute %s" % command

        destination = "sandbox/default/doc/api/PyCoDoc"
        package = "sandbox/%s/lib/PyConfig/" % self.options.flavour

        print "Creating Python Documentation"
        if os.path.exists(destination):

            shutil.rmtree(destination)

            os.makedirs(destination)

        command = "PYTHONPATH=$PYTHONPATH:%s epydoc -o %s --html --show-sourcecode --simple-term --name=openWNS --graph=all %s" % (package, destination, package)
        result = runCommand(command)
        if not (result is None):
            print "Could not execute %s" % command

        command = "rm -f sandbox/%s/lib/PyConfig/__init__.py" % self.options.flavour
        result = runCommand(command)
        if not (result is None):
            print "Could not execute %s" % command

