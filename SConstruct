import os
import sys
import wnsbase.playground.Project

sys.path.append('config')
import projects
sys.path.remove('config')

SetOption('num_jobs', os.sysconf('SC_NPROCESSORS_ONLN'))
SetOption('implicit_cache', True)

# Load options from file and from command line
optionFile = os.path.join('config','options.py')
if not os.path.exists(optionFile):
    print "No options file found. Creating empty options file..."
    defaultoptions = \
    """# This is the build option file. Specify your build options here.

# The 'buildDir' option specifies a directory where the object files are built.
# It is a good idea to choose a directory on a fast harddisk to speed up the
# build process.
#
# buildDir = '/path/to/fast/harddisk/'

# The 'profile' option specifies if the openWNS is built with profiling support.
#
# profile = False

# The 'sandboxDir' specifies the directory where the modules and the openwns 
# executable will be installed.
#
# sandboxDir = '/path/to/the/sandbox'

# The 'cacheDir' option specifies a shared directory for object files.
#
# cacheDir = '/path/to/cacheDir'

# With the 'static' option set to True, all modules will be linked statically.
# 
# static = False
"""
    of = open(optionFile, 'w')
    of.write(defaultoptions)
    of.close

opts = Options(os.path.join('config','options.py'))
opts.Add(BoolOption('static', 'Set to build the static version', False))
opts.Add(PathOption('buildDir', 'Path to the build directory',  os.path.join(os.getcwd(), '.build'), PathOption.PathIsDirCreate))
opts.Add(BoolOption('profile', 'Set to enable profiling support', False))
opts.Add(PathOption('sandboxDir', 'Path to the sandbox', os.path.join(os.getcwd(), 'sandbox'), PathOption.PathIsDirCreate))
opts.Add(PackageOption('cacheDir', 'Path to the object cache', False))
environments = []
installDirs = {}


# Create the debug environment
dbgenv = Environment(options = opts)
dbgenv.Append(CXXFLAGS = ['-g', '-O0', '-fno-inline'])

dbgenv.flavour = 'dbg'
environments.append(dbgenv)


# Create the opt Environment
optenv = Environment(options = opts, CPPDEFINES= {'NDEBUG': '1',
                                                  'WNS_NDEBUG' : '1',
                                                  'WNS_NO_LOGGING' : '1'})

optenv.Append(CXXFLAGS = ['-O3',
                          '-fno-strict-aliasing',
                          '-Wno-unused-variable',
                          '-Wno-unused-parameter'])
optenv.flavour = 'opt'
environments.append(optenv)

# Create the callgrind environment
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


# We use the debug environment to generate the help text for the options.
Help( """
The openWNS SDK provides rich tools to build the framework and modules.

Type: 'scons' to build all libraries and modules for the debug flavour.
      'scons opt' to build all libraries and module for the opt flavour.
      'scons sandbox/<flavour>/lib/<lib of your choice>' to build a single library.
      'scons static=yes' to build openwns executable with statically linked libraries.
      'scons pyconfig' to install the pyconfig files for all flavours.

You can customize your build with the following arguments:
""" +  opts.GenerateHelpText(dbgenv) 
)


# Check if we have to modify the compiler
def CheckICECCBuilder(context):
    context.Message('Checking for icecc compiler...')
    result = context.TryCompile('int main (int, char**){return 0;}', '.cpp')
    context.Result(result)
    return result

CXX = dbgenv['CXX']
confenv = dbgenv.Clone()
confenv.Replace(CXX ='icecc')
conf = Configure(confenv, custom_tests ={'CheckICECCBuilder': CheckICECCBuilder})
if conf.CheckICECCBuilder():
    CXX = 'icecc'
confenv = conf.Finish()

# Overwrite compiler from command line, if available
if ARGUMENTS.get('CXX'):
    CXX = ARGUMENTS.get('CXX')


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
    env.Replace(CXX = CXX)
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
        env.BuildDir(buildDir, project.getDir(), duplicate = False)
        env.SConscript(os.path.join(buildDir, 'SConscript'), exports='env')
    
Alias('default', os.path.join(env['sandboxDir'], 'default'))
Default(installDirs['dbg'])
Alias('pyconfig', pyConfigDirs)
