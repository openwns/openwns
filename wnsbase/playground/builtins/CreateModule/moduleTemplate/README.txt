How to write a Module for WNS:

This project should serve as a template when writing a WNS-Module that
should be integrated into the WNS (Wireless Network Simulator).

If you follow the next steps carefully you should end up with a
WNS-Module that can be loaded by WNS and is tuned to your needs.

MODULE_TEMPLATE_HOME = $TESTBED_HOME/framework/ModuleTemplate--main--3.0

1.) Find a name for your new WNS-Module. Names like
    * OFDMAPhy
    * WiMaxMac
    * RISE
    * ...
    are fine. From now on this name will be called NEWPROJNAME.
    The path to this new module is called NEWPROJ_PATH,
    e.g. NEWPROJ_PATH=$TESTBED_HOME/modules/dll


2.) Make sure that you are in the MODULE_TEMPLATE_HOME directory:
    > cd $MODULE_TEMPLATE_HOME

    Create a new project in the repository (TLA) that is a branch from
    this module template:

    > tla tag -S $(tla tree-version) foo@bar.de--2006/$NEWPROJNAME--main--0.1

    NOTE: Make sure you replace foo@bar.de--2006 with the archive of
    your choice. A new branch will be created in this archive. If you
    don't know which archive to choose here ask someone who is
    familiar with TLA.

3.) To modify your new WNS-Module you need to check out the branch
    that has been created under 2.). We assume that you're inside a
    testbed right now. Furthermore you should be inside
    MODULE_TEMPLATE_HOME.
    Move to the toplevel directory of this testbed:

    > cd $TESTBED_HOME

    You should now be in "WNS--main--x.x"

    Put a copy from the repository into this directory:

    > tla get foo@bar.de--2005/$NEWPROJNAME--main--0.1 $NEWPROJ_PATH/$NEWPROJNAME--main--0.1

    If everything worked fine you should now have a directory called
    $NEWPROJNAME--main--0.1 in your $NEWPROJ_PATH directory.

4.) Create a relative link to the global private.py of the testbed
    (needed to compile within the testbed):

    > cd $NEWPROJ_PATH/NEWPROJNAME--main--0.1/config
    > ln -s $TESTBED_HOME/config/private.py
    e.g., ln -s ../../../../config/private.py

5.) Now you have to edit a number of files in the directory of your new module in order to customize it:

    MAINTAINER
    replace:                                          | by:
    ----------------------------------------------------------------------------
    Joe Doe <joe.doe@doh.no                           | Your Name <yourmail@comnets.rwth-aachen.de>

    config/common.py:
    replace:                                          | by:
    ----------------------------------------------------------------------------
    PROJNAME = 'projname'                             | PROJNAME = '$NEWPROJNAME' (lower case)

    src/ProjNameModule.hpp:
    replace:				              | by:
    ----------------------------------------------------------------------------
    * ProjModule (Short Description)                  | * $NEWPROJNAME (Short Description)
    #ifndef PROJNAME_PROJNAMEMODULE_HPP               | #ifndef $NEWPROJNAME_$NEWPROJNAMEMODULE_HPP
    #define PROJNAME_PROJNAMEMODULE_HPP               | #define $NEWPROJNAME_$NEWPROJNAMEMODULE_HPP
    namespace projname                                | namespace $NEWPROJNAME (lower case)
    class ProjNameModule :                            | class $NEWPROJNAMEModule :
    public wns::Module<ProjNameModule>                | public wns::Module<$NEWPROJNAMEModule>
    ProjNameModule(const wns::PyConf...);             | $NEWPROJNAMEModule(const wns::PyConf...);
    virtual ~ProjNameModule();                        | virtual ~$NEWPROJNAMEModule();
    #endif // NOT defined PROJNAME_PROJNAMEMODULE_HPP | #endif // NOT defined $NEWPROJNAME_$NEWPROJNAMEMODULE_HPP

    src/ProjNameModule.cpp:
    replace:                                          | by:
    ----------------------------------------------------------------------------
    * ProjModule (Short Description)                  | * $NEWPROJNAME (Short Description)
    using namespace projname;                         | using namespace $NEWPROJNAME; (lower case)
    ...::ProjNameModule(conts PyCon...) :             | ...::$NEWPROJNAMEModule(conts PyCon...) :
    wns::Module<ProjNameModule>(_pyCon...)            | wns::Module<$NEWPROJNAMEModule>(_pyCon)
    ProjNameModule::~ProjNameModule()                 | $NEWPROJNAMEModule::~$NEWPROJNAMEModule()
    void ProjNameModule::configure()                  | void $NEWPROJNAMEModule::configure()
    void ProjNameModule::startUp()                    | void $NEWPROJNAMEModule::startUp()
    void ProjNameModule::shutDown()                   | void $NEWPROJNAMEModule::shutDown()

    and:
    STATIC_FACTORY_REGISTER_WITH_CREATOR(ProjNameModule, wns::ModuleBase, "projname", wns::PyConfigViewCreator);
    with:
    STATIC_FACTORY_REGISTER_WITH_CREATOR($NEWPROJNAMEModule, wns::ModuleBase, "$NEWPROJNAME", wns::PyConfigViewCreator);

6.) Go back to the directory $NEWPROJNAME--main--0.1:
    > tla mv src/ProjNameModule.cpp src/$NEWPROJNAMEModule.cpp
    > tla mv src/ProjNameModule.hpp src/$NEWPROJNAMEModule.hpp

    config/libfiles.py:
    replace:                              | by:
    ----------------------------------------------------------------------------
    'src/ProjNameModule.cpp'              | 'src/$NEWPROJNAMEModule.cpp'

7.) Before compiling/installing, you have to modify some files under
    PyConfig:

    > tla mv PyConfig/projname PyConfig/$NEWPROJNAME (lower case)
    > tla mv PyConfig/$NEWPROJNAME/ProjName.py PyConfig/$NEWPROJNAME/$NEWPROJNAME.py

    make sure to edit PyConfig/NEWPROJNAME/NEWPROJNAME.py as well as
    PyConfig/NEWPROJNAME/__init__.py.

8.) That's it. You're done. If everything went fine you should now be able to
    compile your new Module:
    > scons install-lib

9.) If that works you might want to commit your changes to the repository:
    > tla commit -s "New Module is now integrated into WNS"
    (or whatever you would like to use as commit message ...)

10.) Add the new Project to the multi-tree project testbed:

    - edit $TESTBED_HOME/config/projects.py and add your module, e.g. add new line:
      Library('./modules/dll', 'WiMAC--main--0.2', [speetcl, libwns, dllBase]),

11) Go to the testbed--main--x.y directory and commit on testbed:
    > cd $TESTBED_HOME

    Make sure you didn't forget any files.
    > tla tree-lint

    Make sure you only changed config/default and config/pg_config.py
    > tla changes

    Now you can really commit
    > tla commit -s "New Module $NEWPROJNAME is integrated into the testbed"
