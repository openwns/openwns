# This is options.py. Specify your build options here.
import os
username = os.environ['USER']

buildDir = '/local2/KKS/kks/.build'
if os.path.exists('/local2/objectCache'):
    cacheDir = '/local2/objectCache'
