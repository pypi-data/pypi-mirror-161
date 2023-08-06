import unittest
from main import EnigmaInterface
from components import Rotor,Shift

class OverallTestCase1(unittest.TestCase):
    def setUp(self) -> None:
        self.encMachine = EnigmaInterface()
        self.decMachine = EnigmaInterface()
    
    def testA(self,inputStr="arwinder"):
        assert inputStr == self.decMachine.get_plainText(self.encMachine.get_cipherText(inputStr))

class OverallTestCase2(unittest.TestCase):
    def setUp(self) -> None:
        self.encMachine = EnigmaInterface()
        self.decMachine = EnigmaInterface()

    def testB(self,inputStr="arwinder"):
        assert inputStr == self.encMachine.get_cipherText(self.decMachine.get_plainText(inputStr))

class RotorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rotor = Rotor("II")

    def testA(self):
        testChr = 4
        opt = self.rotor.get_output(testChr)
        ropt = self.rotor.get_rev_output(opt)
        assert testChr == ropt
    

    
class ShiftTest(unittest.TestCase):
    def setUp(self) -> None:
        self.shift = Shift(4)
        self.shift2 = Shift(22)
    
    def testA(self):
        testChr = 12
        assert self.shift + testChr == 16
    
    def testB(self):
        testChr = 25
        assert self.shift + testChr == 3

    def testC(self):
        testChr = 5
        assert self.shift2 + testChr == 1
    
    def testD(self):
        testChr = 5
        assert self.shift2 - testChr == 9
    
    def testE(self):
        testChr = 5
        opt = self.shift2 + testChr
        assert testChr == self.shift2 - opt
    

if __name__== "__main__":
    unittest.main()