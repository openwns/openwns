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
from wnsbase.playground.Tools import *
import shutil

core = wnsbase.playground.Core.getCore()

class DocuCommand(wnsbase.playground.plugins.Command.Command):

    def __init__(self):
        usage = "\n%prog docu\n\n"
        rationale = "Build project documentation."

        usage += rationale
        usage += """ Build the documentation for the whole project. The created documentation will
be placed in sandbox/default/doc .
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "docu", rationale, usage)


    def run(self):

        def run(project):
            if not project.generateDoc:
                return

            if not core.userFeedback.askForConfirmation("Do you want to install documentation for '" + project.getDir() + "'?"):
                return

            print "\nInstalling documentation for", project.getDir(), "..."

            command = 'scons %s docu; scons %s install-docu' % (core.getSconsOptions(), core.getSconsOptions(),)
            print "Executing:", command
            result = runCommand(command)
            if not result == None:
                raise "Documentation for " + project.getDir() +  " failed"


        core.foreachProject(run)

        self.createTestbedDocu()


    def createTestbedDocu(self):
        projects = core.getProjects()
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

        self.writeDoxygenHeader()

    def writeDoxygenHeader(self):
        projects = core.getProjects()

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
