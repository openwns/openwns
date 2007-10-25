#!/usr/bin/python
import pydcop
import os

def fullDCOPName(applicationName):
	for app in pydcop.registeredApplications():
		if app.startswith(applicationName):
			return app
	raise "Application " + applicationName + " not found using DCOP!"

def getFullPath():
	caption = str(apply(pydcop.DCOPMethod(fullDCOPName("kdevelop"), "SimpleMainWindow", "caption")))

	(projectname, fullpath, tail) = caption.split(" - ")

	modified = False

	if fullpath.endswith(" [modified]"):
		fullpath=fullpath.replace(" [modified]", "")
		modified=True

	fullpath = fullpath.replace("file://", "")
	return fullpath

def createSymlinks(modulepath):
	try:
		os.remove("./include")
	except OSError:
		pass

	try:
		os.remove("./src")
	except OSError:
		pass

	print "Creating symlink for " + modulepath
	os.symlink(modulepath + "/include", "./include")
	os.symlink(modulepath + "/src", "./src")

def isModule(fullpath):
	print "Checking if " + str(fullpath) + " is in module"
	import re
	m = re.compile("(.*)(/modules/)([a-zA-Z\-]*/[0-9a-zA-Z\-\.]*)(.*)").match(fullpath)
	if m!=None:
		if m.group(2) == "/modules/":
			return True
	return False

def isFramework(fullpath):
	print "Checking if " + str(fullpath) + " is in framework"
	import re
	m = re.compile("(.*)(/framework/)([0-9a-zA-Z\-\.]*)(.*)").match(fullpath)
	if m!=None:
		if m.group(2) == "/framework/":
			return True
	return False

def extractSubPaths(fullpath):
	import re
	m = re.compile("(.*)(/modules/)([a-zA-Z\-]*/[0-9a-zA-Z\-\.]*)(.*)").match(fullpath)
	if m!=None:
		# pathToWNS, modules, subPath
		return (m.group(1), m.group(2), m.group(3)) 
	
	m = re.compile("(.*)(/framework/)([0-9a-zA-Z\-\.]*)(.*)").match(fullpath)
	if m!=None:
		return (m.group(1), m.group(2), m.group(3)) 
		
def buildLocal(fullpath):
	(pathToWNS, modOrFrame, subpath) = extractSubPaths(fullpath)
	print "Building " + str(subpath)
	modulepath = pathToWNS + modOrFrame + subpath
	command = "cd " + modulepath + ";scons no-color=1 no-inf=1 no-filter=1"
	createSymlinks(modulepath)
	print "Executing : " + command
	if runCommand(command) == None:
		os.remove("./include")
		os.remove("./src")

def buildAll():
	print "Building whole WNS"
	runCommand("scons no-color=1 no-inf=1 no-filter=1")

def runCommand(command):
    fh = os.popen(command)
    line = fh.readline()
    while line:
        print line.strip('\n')
        line = fh.readline()
    return fh.close()

if os.getenv("WNSCURRENTMODULEBUILD") != None:
	print "Evaluating wether to build current module or whole WNS"
	if os.getenv("WNSCURRENTMODULEBUILD") == "1":
		currentFile = getFullPath()
		if isModule(currentFile) or isFramework(currentFile):
			buildLocal(currentFile)
		else:
			buildAll()
	else:
		print "Building whole WNS"
		buildAll()
else:
	print "Building whole WNS"
	buildAll()

#runCommand("cat " + getFullPath())
