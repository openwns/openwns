import os
import posix
import commands
import subprocess
import StringIO

class ProjectPathError(Exception):

	def __init__(self, reason):
		Exception.__init__(self)
		self.reason = reason

	def __str__(self):
		return repr(self.reason)

class Output:
	def __init__(self, sout, serr):
		self.sout = sout
		self.serr = serr
		self.hasError = False

	def __str__(self):
		s = ""
		error = ""
		for it in self.serr:
			error += it
		if error != "":
			raise("An error during TLA action occured:\n\n" + error )
		for i in self.sout:
			s += i
		return s.strip("\n")

	def __iter__(self):
		for s in self.sout, self.serr:
			line = s.readline()
			while line:
				if s == self.serr:
					self.hasError = True
				yield line.strip('\n')
				line = s.readline()

	def realtimePrint(self, prepend=""):
		for it in self:
			print prepend + it
		if self.hasError:
			raise("An error during TLA action occured!")


class RCS:
	pass

class No(RCS):
	def __init__(self, category, branch, revision, patchLevel):
		self.category = category
		self.branch = branch
		self.revision = revision
		self.patchLevel = patchLevel
		self.version = '--'.join([self.category, self.branch, self.revision])
		self.FQRN = 'local/'+self.revision+'--patch-'+self.patchLevel

class Bazaar(RCS):
	def __init__(self, masterBranchURL, path, category, branch, revision, pinnedPatchLevel=None):
		self.cmd = "bzr"
		self.masterBranchURL = masterBranchURL
		self.category = category
		self.branch = branch
		self.revision = revision
		self.pinnedPatchLevel = pinnedPatchLevel
		self.version = self.category + "--" + self.branch + "--" + self.revision

		self.setPath(path)

	def setPath(self, path):
		self.path = os.path.abspath(path)

	def getPath(self):
		return self.path

	def __exec(self, command, switches, args):
		cwd = os.path.abspath(os.curdir)
		if (not os.path.exists(self.path)):
			if (not command == "branch"):
				raise ProjectPathError("Error executing bzr %s. The project path %s does not exist." % (command, self.path))
		else:
			os.chdir(self.path)

		switchString = [it + "=" + switches[it] for it in switches]
		finalCommand = (" ").join([self.cmd, command] + switchString + args)

		p = subprocess.Popen(finalCommand, shell=True,
				     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

		returnValue = Output(p.stdout, p.stderr)
		p.wait()
		os.chdir(cwd)
		return returnValue

	def updateVersionInfo(self):
		foobar = {}
		output = self.__exec("version-info", {"--format":"python"}, [])
		exec(str(output), foobar)
		if foobar.has_key("version_info"):
			self.patchLevel = foobar["version_info"]["revno"]

	def missing(self, switches={}, revision=""):
		if self.pinnedPatchLevel != None:
			return Output(StringIO.StringIO("This branch is pinned to " + str(self.masterBranchURL) + " at revision " + str(self.pinnedPatchLevel)), StringIO.StringIO())
		retval = self.__exec("missing", {"--log-format" : "short"}, [self.masterBranchURL])
		if str(retval).endswith("Branches are up to date."):
			return Output(StringIO.StringIO(""), StringIO.StringIO())
		else:
			return self.__exec("missing", {"--log-format" : "short"}, [])

	def status(self, switches={}):
		return self.__exec("status", {}, ["--short"])

	def lint(self):
		statusoutput = self.status()
		lintoutput = ""
		for line in str(statusoutput).split("\n"):
			if line.startswith("?"):
				lintoutput += line + "\n"
		lintoutput += str(self.__exec("conflicts", {}, []))
		tmp = Output(StringIO.StringIO(lintoutput), StringIO.StringIO())
		return tmp

	def update(self):
		# BZR update outputs partly on std error, we redirect this
		return self.__exec("pull", {}, ["2>&1"])

	def get(self, targetDir=None):
		namedArgs = {}

		if targetDir == None:
			targetDir = self.path

		if self.pinnedPatchLevel != None:
			namedArgs = { "--revision" : str(self.pinnedPatchLevel) }

		returnValue = self.__exec("branch", namedArgs, [self.masterBranchURL, targetDir])
		self.updateVersionInfo()
		return returnValue

	def getFQRN(self):
		return self.masterBranchURL

	def getTreeVersion(self):
		self.updateVersionInfo()
		return self.masterBranchURL + "/" + self.version

	def getVersion(self):
		return self.version

	def getCategory(self):
		return self.category

	def getBranch(self):
		return self.branch

	def getRevision(self):
		return self.revision

	def getPatchLevel(self):
		self.updateVersionInfo()
		return str(self.patchLevel)

class GNUArch(RCS):
	def __init__(self, archive, path, category, branch, revision, pinnedPatchLevel=None):
		# we prefer "tla" over "baz"
		if commands.getstatusoutput("type tla")[0] == 0:
			self.arch = "tla"
		elif commands.getstatusoutput("type baz")[0] == 0:
			self.arch = "baz"
		else:
			raise ("Found none of the follwing supported GNUArch binaries: [tla, baz]")

		self.archive = archive
		self.setPath(path)
		self.category = category
		self.branch = branch
		self.revision = revision
		self.version = self.category + "--" + self.branch + "--" + self.revision

		self.pinnedPatchLevel = pinnedPatchLevel
		self.patchLevel = None

	def setPath(self, path):
		self.path = os.path.abspath(path)

	def getPath(self):
		return self.path

	def __startup(self):
		self.treeVersion = self.getTreeVersion()
		self.category = self.getCategory()
		self.branch = self.getBranch()
		self.patchLevel = self.getPatchLevel()
		self.treeRoot = self.getTreeRoot()

	def __exec(self, command, switches, args):
		cwd = os.path.abspath(os.curdir)

		if (not os.path.exists(self.path)):
			if (not command == "get"):
				raise ProjectPathError("Error executing tla %s. The project path %s does not exist." % (command, self.path))
		else:
			os.chdir(self.path)

		switchString = [it + " " + switches[it] for it in switches]
		finalCommand = (" ").join([self.arch, command] + switchString + args)

		p = subprocess.Popen(finalCommand, shell=True,
				     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

		returnValue = Output(p.stdout, p.stderr)
		p.wait()
		os.chdir(cwd)
		return returnValue

	def missing(self, switches = {}, version = ""):
		self.__startup()
		switches["-d"] = self.path
	        return self.__exec("missing", switches, [version])

	def status(self, switches = {}):
		self.__startup()

		args = []
	        if self.arch == "tla":
			command = "changes"
			switches["-d"] = self.path
		elif self.arch == "baz":
		        command = "status"
			args.append("self.path")
		return self.__exec(command, switches, args)

	def commit(self, switches = {}, files = []):
		self.__startup()

		switches["-d"] = self.path
		if len(files) > 0:
			files = ["--"] + files
		return self.__exec("commit", switches, files)

	def update(self):
		self.__startup()

		return self.__exec("update", {"-d":self.path}, [])

	def ancestryGraph(self, switches = {}, specialRevision=""):
		self.__startup()

		switches["-d"] = self.path
		return self.__exec("ancestry-graph", switches, [specialRevision])

	def replay(self, specialRevision="", switches={}):
		self.__startup()

		switches["-d"] = self.path
		return self.__exec("replay", switches, [specialRevision])

	def starMerge(self, revision, switches={}):
		self.__startup()

		switches["-d"] = self.path
		return self.__exec("star-merge", switches, [revision])

	def tag(self, newBranch):
		self.__startup()

		return self.__exec("tag", {"--setup":""}, [self.getTreeVersion(), newBranch])

	def get(self, targetDir=None):

		if targetDir == None:
			targetDir = self.path

		project = self.archive + "/" + self.getVersion()

		if self.pinnedPatchLevel != None:
			if self.patchLevel == 0:
				return self.__exec("get", {}, [project + "--base-" + str(self.pinnedPatchLevel), targetDir])
			else:
				return self.__exec("get", {}, [project + "--patch-" + str(self.pinnedPatchLevel), targetDir])

		return self.__exec("get", {}, [project, targetDir])

	def lint(self, options = {}):
		self.__startup()

		if self.arch == "tla":
			command = "tree-lint"
		elif self.arch == "baz":
			command = "lint"
		return self.__exec(command, options, [self.path])

	def getTreeVersion(self):
		switch = ""
		if self.arch == "baz":
			switch = "-d"
		return str(self.__exec("tree-version", {switch : self.path}, []))

	def getArchive(self):
		self.__startup()

		return self.treeVersion.split('/')[0]

	def getVersion(self):
		return self.version

	def getRevision(self):
		return self.revision

	def getBranch(self):
		return self.branch

	def getCategory(self):
		return self.category

	def getPatchLevel(self):
		tmp = str(self.__exec("logs", {"-r" : "", "-d" : self.path}, [])).split("\n")[0]
		patchLevel = tmp.replace("patch-", "")
		patchLevel = patchLevel.replace("base-", "")
		return patchLevel

	def getFQRN(self):
		if self.pinnedPatchLevel != None:
			self.patchLevel = self.pinnedPatchLevel

		if self.patchLevel == None:
			return self.archive + "/" + self.getVersion()

		if self.patchLevel == 0:
			return self.archive + "/" + self.getVersion()+'--base-'+ str(self.patchLevel)
		else:
			return self.archive + "/" + self.getVersion()+'--patch-'+ str(self.patchLevel)

	def getTreeRoot(self):
		return str(self.__exec("tree-root " + self.path, {}, []))

	def cacheRev(self):
		self.__startup()

		return self.__exec("cacherev ", {}, [self.FQRN])

	def getCachedRevs(self):
		self.__startup()

		return self.__exec("cachedrevs ", {}, [self.treeVersion])

	def logs(self):
		self.__startup()

		return self.__exec("logs ", {}, [])

	def catlog(self,revision):
		self.__startup()

		return self.__exec("cat-log ",{}, [revision])

class LogParser:
    """This class can parse the output of the tla cat-log <revision-spec> command and make
    its different fields available in a dict. The most commonly wanted fields can be retrieved
    via access methods.
    """

    def creator(self):
        """returns the name of the creator of the patch"""
        return self.contents['Creator'][0]

    def date(self):
        """returns the creation date of the patch"""
        return self.contents['Date'][0]

    def patch(self):
        """returns the revision of the patch"""
        return self.contents['Revision'][0]

    def dump(self):
        """debug method. prints all data that was read from the patchlog"""
        print self.contents

    def fileChanged(self, fileName):
        """returns True if the string fileName was anywhere among the removed, modified or new files."""
        keys = [ 'Removed-files', 'Modified-files','New-files' ]
        changed = False
        for k in keys:
            if self.contents.has_key(k):
                files = self.contents[k]
                for f in files:
                    if f.count(fileName):
                        changed = True
        return changed

    def __init__(self, patchLog):
        """Constructor, requires the patchlog as an iterable data structure (file object)"""
        self.contents = {}

        for line in patchLog:
            if line.strip()=='':
                return

            if not line.startswith('    '):
                keyword = line.split(':')[0]
                fieldContent = line.lstrip(keyword+':').strip()
            else:
                fieldContent = line.strip()

            if self.contents.has_key(keyword):
                self.contents[keyword].append(fieldContent)
            else:
                self.contents[keyword] = [fieldContent]
