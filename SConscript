import os
Import('env')
libname,srcFiles,headers,pyconfigs,dependencies = SConscript('config/libfiles.py')

if len(srcFiles) != 0:
    if env['static']:
        lib = env.StaticLibrary(libname, srcFiles)
    else:
        lib = env.SharedLibrary(libname, srcFiles, LIBS = dependencies)
    env.Install(os.path.join(env.installDir, 'lib'), lib )

for config in pyconfigs:
    env.InstallAs(os.path.join(env.installDir, 'lib', 'PyConfig', config),
                  os.path.join('PyConfig', config))

