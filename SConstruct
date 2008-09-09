import os
import sys
import wnsbase.playground.Project
sys.path.append('config')
import projects
sys.path.remove('config')

profile = ARGUMENTS.get('profile', False)
static = ARGUMENTS.get('static', False)
environments = []
installDirs = {}

# Debug environment
dbgenv = Environment(CPPDEFINES= {'WNS_ASSERT': '1'}
                     )
dbgenv.Append(CXXFLAGS = ['-g', '-O0', '-fno-inline'])

dbgenv.flavour = 'dbg'
environments.append(dbgenv)

# Opt Environment
optenv = Environment(CPPDEFINES= {'NDEBUG': '1',
                                  'WNS_NDEBUG' : '1',
                                  'WNS_NO_LOGGING' : '1'},
                      )
optenv.Append(CXXFLAGS = ['-O3',
                          '-fno-strict-aliasing',
                          '-Wno-unused-variable',
                          '-Wno-unused-parameter'])
optenv.flavour = 'opt'
environments.append(optenv)

includeDir = os.path.join(os.getcwd(),'include')
    
for env in environments:
    env.Append(CPPPATH = ['#include', '/usr/include/python2.5'])
    env.Append(LIBPATH = os.path.join('#sandbox', env.flavour, 'lib'))
    env.Replace(CXX = 'icecc')
    #env.SetOption('implicit-cache',1)
    env.installDir = os.path.join(os.getcwd(), 'sandbox', env.flavour)
    env.includeDir = includeDir
    installDirs[env.flavour] = Dir(env.installDir)
    Alias(env.flavour, installDirs[env.flavour])

    if profile:
        env.Append(CXXFLAGS = '-pg')
        env.Append(LINKFLAGS = '-pg')

    for project in projects.all:
        if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
            continue
        buildDir = os.path.join('.build/', env.flavour, project.getRCSSubDir())
        env.BuildDir(buildDir, project.getDir())
        env.SConscript(os.path.join(buildDir, 'SConscript'), exports='env')
    

for project in projects.all:
    if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
        continue
    if project.includeBaseName is not None:
        srcFiles,headers,pyconfigs = SConscript(os.path.join(project.getDir(), 'config', 'libfiles.py'))
        headertargets = [header.replace('src/', '') for header in headers]
        InstallAs([os.path.join(includeDir, project.includeBaseName ,target) for target in headertargets],\
                  [os.path.join(project.getDir(), header) for header in headers])



Default(installDirs['dbg'])
