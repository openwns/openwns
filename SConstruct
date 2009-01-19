import os
import sys
import wnsbase.playground.Project
sys.path.append('config')
import projects
sys.path.remove('config')

SetOption('num_jobs', os.sysconf('SC_NPROCESSORS_ONLN'))
SetOption('implicit_cache', True)

opts = Options(os.path.join('config','options.py'))
opts.Add(BoolOption('static', 'Set to build the static version', False))
opts.Add(PathOption('buildDir', 'Path to the build directory',  os.path.join(os.getcwd(), '.build'), PathOption.PathIsDirCreate))
opts.Add(BoolOption('profile', 'Set to enable profiling support', False))
opts.Add(PathOption('sandboxDir', 'Path to the sandbox', os.path.join(os.getcwd(), 'sandbox'), PathOption.PathIsDirCreate))
opts.Add(PackageOption('cacheDir', 'Path to the object cache', False))
environments = []
installDirs = {}

# Debug environment
dbgenv = Environment(options = opts)
dbgenv.Append(CXXFLAGS = ['-g', '-O0', '-fno-inline'])

dbgenv.flavour = 'dbg'
environments.append(dbgenv)

#we use only the debug environment to generate the help text for the options
Help(opts.GenerateHelpText(dbgenv))

# Opt Environment
optenv = Environment(options = opts, CPPDEFINES= {'NDEBUG': '1',
                                                  'WNS_NDEBUG' : '1',
                                                  'WNS_NO_LOGGING' : '1'})

optenv.Append(CXXFLAGS = ['-O3',
                          '-fno-strict-aliasing',
                          '-Wno-unused-variable',
                          '-Wno-unused-parameter'])
optenv.flavour = 'opt'
environments.append(optenv)

# Callgrind environment
callgrindenv = Environment(options = opts, CPPDEFINES = {'NDEBUG': '1',
                                                         'WNS_NDEBUG' : '1',
                                                         'WNS_NO_LOGGING': '1',
                                                         'CALLGRIND': '1'})
callgrindenv.Append(CXXFLAGS = ['-O3',
                                '-fno-strict-aliasing',
                                '-Wno-unused-variable',
                                '-Wno-unused-parameter',
                                '-g'])
callgrindenv.flavour = 'callgrind'
environments.append(callgrindenv)


includeDir = os.path.join(os.getcwd(),'include')
libraries = []
for project in projects.all:
    if isinstance(project, (wnsbase.playground.Project.Root, wnsbase.playground.Project.SystemTest, wnsbase.playground.Project.Generic)):
        continue
    if isinstance(project, wnsbase.playground.Project.Library):
        libname,srcFiles,headers,pyconfigs,dependencies = SConscript(os.path.join(project.getDir(), 'config', 'libfiles.py'))
        if len(srcFiles) != 0:
            libraries.append(libname)
            # if we static link we also need to include the dependencies of the libraries
            # if we compile for a different flavour than debug, the following is also true
            if dbgenv['static']:
                libraries += dependencies

    if isinstance(project, wnsbase.playground.Project.Python):
        # here we install python files from pure Python projects
        # w. l. o. g. we can use the dbg environment here
        env = dbgenv
        env.SConscript(os.path.join(project.getDir(), 'SConscript'), exports='env')

    if project.includeBaseName is not None:
        libname,srcFiles,headers,pyconfigs,dependencies = SConscript(os.path.join(project.getDir(), 'config', 'libfiles.py'))
        headertargets = [header.replace('src/', '') for header in headers]
        InstallAs([os.path.join(includeDir, project.includeBaseName ,target) for target in headertargets],\
                  [os.path.join(project.getDir(), header) for header in headers])

# remove duplicates
libraries = list(set(libraries))
pyConfigDirs = []

for env in environments:
    env.Append(CPPPATH = ['#include', '/usr/include/python2.5'])
    env.Append(LIBPATH = os.path.join('#sandbox', env.flavour, 'lib'))
    if ARGUMENTS.get('CXX'):
        env.Replace(CXX = ARGUMENTS.get('CXX'))
    env.installDir = os.path.join(env['sandboxDir'], env.flavour)
    env.includeDir = includeDir
    env['libraries'] = libraries
    if env['cacheDir']:
        env.CacheDir(env['cacheDir'])
    installDirs[env.flavour] = Dir(env.installDir)
    Alias(env.flavour, installDirs[env.flavour])
    pyConfigDirs.append(Alias(env.flavour + 'PyConfig', Dir(os.path.join(env.installDir, 'lib', 'PyConfig'))))

    if env['profile']:
        env.Append(CXXFLAGS = '-pg')
        env.Append(LINKFLAGS = '-pg')

    for project in projects.all:
        if isinstance(project, (wnsbase.playground.Project.Root, wnsbase.playground.Project.SystemTest, wnsbase.playground.Project.Generic, wnsbase.playground.Project.AddOn, wnsbase.playground.Project.Python)):
            continue
        buildDir = os.path.join(env['buildDir'], env.flavour, project.getRCSSubDir())
        env.BuildDir(buildDir, project.getDir())
        env.SConscript(os.path.join(buildDir, 'SConscript'), exports='env')
    
Default(installDirs['dbg'])
Alias('pyconfig', pyConfigDirs)
