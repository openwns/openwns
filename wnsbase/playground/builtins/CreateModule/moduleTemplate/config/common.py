import os
import CNBuildSupport
from CNBuildSupport import CNBSEnvironment
import wnsbase.RCS as RCS

commonEnv = CNBSEnvironment(PROJNAME       = 'projname',
                            AUTODEPS       = ['wns'],
                            PROJMODULES    = ['TEST', 'BASE'],
                            LIBRARY        = True,
                            SHORTCUTS      = True,
                            FLATINCLUDES   = False,
			    REVISIONCONTROL = RCS.Bazaar('../', 'ModuleTemplate', 'main', '1.0'), 
                            )
Return('commonEnv')
