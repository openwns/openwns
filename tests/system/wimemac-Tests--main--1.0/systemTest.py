#! /usr/bin/env python

# this is needed, so that the script can be called from everywhere
import os
import sys
base, tail = os.path.split(sys.argv[0])
os.chdir(base)

# Append the python sub-dir of WNS--main--x.y ...
sys.path.append(os.path.join('..', '..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages'))

# ... because the module WNS unit test framework is located there.
import pywns.WNSUnit

testSuite = pywns.WNSUnit.TestSuite()

# create a system test
testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'One-on-one communication with: Copper, Glue, IP, Constanze',
                                                disabled = False,
                                                disabledReason = ""))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                
                                                configFile = 'config80211.py',
                                                runSimulations = True,
                                                shortDescription = 'One-on-one communication with: Copper, 802.11, IP, Constanze',
                                                disabled = False,
                                                disabledReason = ""))

if __name__ == '__main__':
    # This is only evaluated if the script is called by hand

    # if you need to change the verbosity do it here
    verbosity = 2

    pywns.WNSUnit.verbosity = verbosity

    # Create test runner
    testRunner = pywns.WNSUnit.TextTestRunner(verbosity=verbosity)

    # Finally, run the tests.
    testRunner.run(testSuite)
