import sys
import os
sys.path.append('config')
import projects
sys.path.remove('config')

# This enables filtering of SCons output ...
jobs = ARGUMENTS.get('j', '')
nc = ARGUMENTS.get('no-color', '0')
ni = ARGUMENTS.get('no-inf', '0')
nf = ARGUMENTS.get('no-filter', '0')
noAddOns = ARGUMENTS.get('no-addOns', '0')=='1'
pda = ARGUMENTS.get('project-dependent-aliases', '0')=='1'
flavour = ARGUMENTS.get('flavour', 'dbg')
static = ARGUMENTS.get('static', '0')=='1'
sandboxDir = ARGUMENTS.get('sandboxDir', '')

options = "no-color='%s' no-inf='%s' no-filter='%s' project-dependent-aliases='%s' flavour='%s' static='%s' sandboxDir='%s' no-addOns='%s'" % (nc, ni, nf, pda, flavour, static, sandboxDir, noAddOns)

def getTargetName(project):
    head, tail = os.path.split(project.getDir())
    return "_target_"+tail

def projectDepth(projectPath):
    # calculate the depth with respect to the testbed dir
    # this returns the path in normalized fashion ("foo/bar")
    normalizedPath = os.path.normpath(projectPath)
    # by splitting at the slashes we can find the depth
    return len(normalizedPath.split(os.sep))

def relativePathToTestbed(projectPath):
    depth = projectDepth(projectPath)
    return os.path.normpath(("/").join([".."]*depth))

targets = []

# setup all targets
for project in projects.all:
    if project.getExe() != None:
        if project.getExe() in ["bin", "lib"]:
            if not os.path.exists(os.path.join(project.getDir(), "config", "private.py")):
                os.symlink(os.path.join(relativePathToTestbed(project.getDir()), "..", "config", "private.py"),
                           os.path.join(project.getDir(), "config", "private.py"))

        command = 'bash -c "cd ' + project.getDir() + ';'
        if isinstance(project, projects.SDL):
            command += " scons s2s -j1;"

        command += ' scons '
        if jobs != '':
            command += " -j " + jobs + " "
        command += options + '"'
        targets.append(Command(getTargetName(project), None, command, ENV=os.environ))


# setup dependencies between targets
for project in projects.all:
    if project.getExe() != None:
        for dependency in project.dependencies:
            Depends(getTargetName(project), getTargetName(dependency))

Alias("install", targets)

Default("install")
