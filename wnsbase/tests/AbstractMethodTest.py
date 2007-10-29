import unittest
import wnsbase.Interface
from wnsbase.Interface import abstractmethod

class IA(wnsbase.Interface.Interface):
   @abstractmethod
   def methodA(self, aParameter):
     pass

class IB(wnsbase.Interface.Interface):
   @abstractmethod
   def methodB(self,aParameter):
      pass

class IAB(IA, IB):
   pass


class A(IA):
    def methodA(self, aParameter):
       pass

class BadA(IA):
    pass

class AB(IAB):
   def methodA(self, aParameter):
      pass

   def methodB(self, aParameter):
      pass

class BadAB(IAB):
   def methodA(self, aParameter):
      pass

class AB2(IA, IB):

   def methodA(self, aParameter):
      pass

   def methodB(self, aParameter):
      pass

class BadAB2(IA, IB):

   def methodB(self, aParameter):
      pass

class AbstractMethodTests(unittest.TestCase):


    def testSingleInheritance(self):
        # This must work
        a = A()

    def testMultipleInheritance(self):
        ab = AB2()

    def testMultipleInheritanceHierarchy(self):
        ab = AB()

    def testBadSingleInheritance(self):
        typeErrorThrown = False
        try:
            badA = BadA()
        except TypeError:
            typeErrorThrown = True
        assert(typeErrorThrown, "No TypeError was thrown when creating an instance of BadA")

    def testBadMultipleInheritance(self):
        typeErrorThrown = False
        try:
            badAB2 = BadAB2()
        except TypeError:
            typeErrorThrown = True
        assert(typeErrorThrown, "No TypeError was thrown when creating an instance of BadAB2")

    def testBadMultipleInheritanceHierarchy(self):
        typeErrorThrown = False
        try:
            badAB = BadAB()
        except TypeError:
            typeErrorThrown = True
        assert(typeErrorThrown, "No TypeError was thrown when creating an instance of BadAB")


