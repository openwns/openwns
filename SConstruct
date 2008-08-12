import os
import sys
import wnsbase.playground.Project
sys.path.append('config')
import projects
sys.path.remove('config')

#SetOption('implicit-cache',1)
opts = Options()
opts.Add(BoolOption('NDEBUG', 'Set to disable debug', False))
opts.Add(BoolOption('WNS_NDEBUG', 'Set to disable wns specific debug', False))
opts.Add(BoolOption('WNS_NO_LOGGING', 'Set to disable logging output at compile time', False))
opts.Add(BoolOption('profile','Set to true to enable profiler support', False))
flavour = ARGUMENTS.get('flavour', 'dbg')
profile = ARGUMENTS.get('profile', False)

environments = []
installDirs = {}

# Debug environment
dbgenv = Environment(options = opts,
                     CPPDEFINES= {'WNS_ASSERT': '1'}
                     )
dbgenv.Append(CXXFLAGS = ['-g', '-O0', '-fno-inline'])

dbgenv.flavour = 'dbg'
environments.append(dbgenv)

# Opt Environment
optenv = Environment(options = opts,
                     CPPDEFINES= {'NDEBUG': '1',
                                  'WNS_NDEBUG' : '1',
                                  'WNS_NO_LOGGING' : '1'},
                      )
optenv.Append(CXXFLAGS = ['-O3',
                          '-fno-strict-aliasing',
                          '-Wno-unused-variable',
                          '-Wno-unused-parameter'])
optenv.flavour = 'opt'
environments.append(optenv)
    
includeDir=os.path.join(os.getcwd(),'include')

for env in environments:
    env.Append(CPPPATH = ['#include', '/usr/include/python2.5'])
    env.Append(LIBPATH = '#' + 'sandbox/' + env.flavour)
    env.Replace(CXX = 'icecc')
    installDir = os.path.join(os.getcwd(), 'sandbox', env.flavour)
    installDirs[env.flavour] = Dir(installDir)
    Alias(env.flavour, installDirs[env.flavour])

    if profile:
        env.Append(CXXFLAGS = '-pg')
        env.Append(LINKFLAGS = '-pg')

    for project in projects.all:
        if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
            continue
        buildDir = os.path.join('.build/', env.flavour, project.getRCSSubDir())
        env.BuildDir(buildDir, project.getDir())
        env.SConscript(os.path.join(buildDir, 'SConscript'), exports='env installDir includeDir')
    

for project in projects.all:
    if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
        continue
    if project.includeBaseName is not None:
        libs,headers,pyconfigs = SConscript(os.path.join(project.getDir(), 'config', 'libfiles.py'))
        headertargets = [header.replace('src/', '') for header in headers]
        InstallAs([os.path.join(includeDir, project.includeBaseName ,target) for target in headertargets],\
                  [os.path.join(project.getDir(), header) for header in headers])



Default(installDirs['dbg'])
