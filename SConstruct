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

#flavour = ARGUMENTS.get('flavour', 'dbg')

environments = []

# Debug environment

dbgenv = Environment(options = opts,
                     CPPDEFINES= {'NDEBUG': '${NDEBUG}',
                                  'WNS_NDEBUG' : '${WNS_NDEBUG}',
                                  'WNS_NO_LOGGING' : '${WNS_NO_LOGGING}'},
                     )

dbgenv.Append(CXXFLAGS = '-g')
dbgenv.flavour = 'dbg'
environments.append(dbgenv)

optenv = Environment(options = opts,
                     CPPDEFINES= {'NDEBUG': '${NDEBUG}',
                                  'WNS_NDEBUG' : '${WNS_NDEBUG}',
                                  'WNS_NO_LOGGING' : '${WNS_NO_LOGGING}'},
                     )
optenv.Append(CXXFLAGS = '-O2')
optenv.flavour = 'opt'
environments.append(optenv)

    
includeDir=os.path.join(os.getcwd(),'include')

for env in environments:
    env.Append(CPPPATH = ['#include', '/usr/include/python2.5'])
    env.Append(LIBPATH = '#' + 'sandbox/' + env.flavour)
    installDir=os.path.join(os.getcwd(), 'sandbox', env.flavour)

    for project in projects.all:
        if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
            continue
        buildDir = '.build/' + env.flavour + '/' + project.getRCSSubDir()
        env.BuildDir(buildDir, project.getDir())
        env.SConscript(buildDir + '/SConscript', exports='env installDir includeDir')
    

for project in projects.all:
    if isinstance(project, wnsbase.playground.Project.Root) or isinstance(project, wnsbase.playground.Project.SystemTest):
        continue
    if project.includeBaseName is not None:
        libs,headers,pyconfigs = SConscript(os.path.join(project.getDir(), 'config', 'libfiles.py'))
        headertargets = [header.replace('src/', '') for header in headers]
        InstallAs([os.path.join(includeDir, project.includeBaseName ,target) for target in headertargets],\
                  [os.path.join(project.getDir(), header) for header in headers])
