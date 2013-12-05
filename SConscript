import os
import sys
Import('env')
libname,srcFiles,headers,pyconfigs,dependencies = SConscript(os.path.join('config','libfiles.py'))

pyconfigs = ['PyConfig/' + config for config in pyconfigs]

try:
    addOnLibname,addOnSrcFiles,addOnHeaders,addOnPyconfigs,addOnDependencies = SConscript(os.path.join('addOn', 'config', 'libfiles.py'))
    srcFiles += ['addOn/' + sourceFile for sourceFile in addOnSrcFiles]
    pyconfigs += ['addOn/PyConfig/' + pyconfig for pyconfig in addOnPyconfigs]
    dependencies += addOnDependencies

except TypeError:
    pass

if len(srcFiles) != 0:
    if env['static']:
        lib = env.StaticLibrary(libname, srcFiles)
    else:
        linkflags = ["$LINKFLAGS"]

        if sys.platform == 'darwin':
            linkflags.append('-Wl,-install_name,@rpath/lib%s.dylib' % (libname))
            linkflags.append(['-flat_namespace', '-undefined', 'suppress'])

        lib = env.SharedLibrary(libname, srcFiles, LIBS = dependencies, LINKFLAGS = linkflags)

    env.Install(os.path.join(env.installDir, 'lib'), lib )

for config in pyconfigs:
    env.InstallAs(os.path.join(env.installDir, 'lib', config.replace('addOn/', '')),
                  config)

