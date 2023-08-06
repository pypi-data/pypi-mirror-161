from config import Reflector, RotorList, ShiftList, shorts
from components import *
'''
This file contains the code for a virtual enigma machine used in world war 2 
to encrypt and decrypt messages.

NOTE: This model does not support symbols

The machine has two main mechanisms for generating encrypted messages:
The first one is an intricate system of rotors. 
The second is a switchboard which simply replaces one letter with another one.

The Rotor system includes:
1) A set of three rotors.
2) A reflector
Each of these contributes to encryption / encoding as follows:
1) The rotors are useful in following two ways:
a) Each rotor has an input and an output . A rotor is simple a disc with metal 
contacts on either of the circular surfaces.
there are 26 contacts on either side. Each contact corresponds to an alphabet. 
1 refers to A , 2 to B and so on, the input is an electrical signal. The input 
is given to the rotor and output is taken from the other end. The corresponding
contact lights up on the other side. So a rotor essentially switches on alphabet 
to another.
b) Three rotors are used, there happens a shift in contact from one rotor to other.
The 1 numbered contact may not be in contact with the  numbered contact of next rotor.
This resuls in a shift when input rotor to ouput rotor.
2) The reflector reflects the input coming from rotor 3 and gives it as input on the 
other side of rotor3. The signal now moves in reverse direction and is scrambled once
more

The switchbaord shorts one alphabet with other and it is possible to only provide an
additional shift for only some alphabets. This add further entropy in the signal.
'''
class EnigmaInterface:
    '''
    This is the interface for enigma machine. Currently it just provides an encryption
    and decryption method for strings.
    The setup of the machine can be changed in the config file.
    '''
    def __init__(self):
        '''
        Just sets up the enigma machine core
        '''
        self._enigmaCore = EnigmaCore()

    def get_cipherText(self,inputStr:str) -> str:
        '''
            The method converts the characters in the string one by one to an intger from 
            0 to 25 and calls encrypt function from the enigma core converts the number
            back to chr and creates a new string
        '''
        cipher = ""
        for char in inputStr:
            num = self.conv_num(char)
            num = self._enigmaCore.encrypt(num)
            cipher+=chr(num + 97)
        return cipher
    
    def get_plainText(self,inputStr:str) -> str:
        '''
            The method converts the characters in the string one by one to an intger from 
            0 to 25 and calls decrypt function from the enigma core converts the number
            back to chr and creates a new string
        '''
        cipher = ""
        for char in inputStr:
            num = self.conv_num(char)
            num = self._enigmaCore.decrypt(num)
            cipher+=chr(num + 97)
        return cipher
    
    def conv_num(self,value:chr) -> int:
        '''
        Converts a character both upper and lower case into an int 
        from 0 to 25 based on the positional value of the chr in alphabet.
        '''
        if value.isupper():
            return ord(value) - 65
        else:
            return ord(value) - 97
    
    def changeRotor(self,rotor_num:int,rotor_type:str)->None:
        '''
        Allows for the changing of Rotor in the machine manually.
        The input needs to be the poition form 0-2 of the rotor that
        needs to be changed. The other input is rotor_type.
        '''
        self._enigmaCore._RotorList[rotor_num] = Rotor(rotor_type)

    def addShort(self,short:tuple)->None:
        '''
        Allows for the adding shorts at the switchboard.
        The input is a tuple conating two ints from 0 to 25
        '''
        self._enigmaCore._switchb.add_Short(short)
    
    def removeShort(self,short:tuple)->None:
        '''
        Allows for the removal of a short cable 
        The input is a tuple conating two ints from 0 to 25.
        The short must be added before it can be removed.

        '''

class EnigmaCore:
    def __init__(self):
        '''
        This method sets up things on default from the config file.
        sets up a rotor list
        sets up the shift between the rotors
        sets up the switch board
        '''
        self._RotorList = []
        for type in RotorList:
            self._RotorList.append(Rotor(type))
        self._reflector = Rotor(Reflector)
        self._shiftList = []
        for value in ShiftList:
            self._shiftList.append(Shift(value))
        self._switchb  = SwitchBoard()
        for short in shorts:
            self._switchb.add_Short(short[0],short[1])
    
    def encrypt(self,inputChar:chr) -> chr:
        '''
        Method that encrypts the character and returns a character. 
        This is done by passing the charater in one direction through a
        series of rotors and shifts and then it hits the reflector and
        then it passes through all the rotors in reverse and the output 
        is derived.
        Every call to this function all leads to a call to the moveShift
        function.
        '''
        for rotor,shift in zip(self._RotorList,self._shiftList[0:3]):
            inputChar = shift + inputChar
            inputChar = rotor.get_output(inputChar)
        inputChar = self._shiftList[3] + inputChar
        inputChar = self._reflector.get_output(inputChar)
        for rotor,shift in zip(list(reversed(self._RotorList)),list(reversed(self._shiftList[1:4]))):
            inputChar = shift - inputChar
            inputChar = rotor.get_rev_output(inputChar)
        
        inputChar = self._shiftList[0] - inputChar
        self.moveShift()
        return self._switchb.get_output(inputChar)

    def decrypt(self,inputChar:chr) -> chr:
        '''
        Method that decrypts the character and returns a character. 
        This is done by passing the charater in one direction through a
        series of rotors and shifts and then it hits the reflector where 
        the rev output acquired and then it passes through all the rotors '
        in reverse and the output is derived.
        Every call to this function all leads to a call to the moveShift
        function.
        '''
        inputChar = self._switchb.get_output(inputChar)
        for rotor,shift in zip(self._RotorList,self._shiftList[0:3]):
            inputChar = shift + inputChar
            inputChar = rotor.get_output(inputChar)
        inputChar = self._shiftList[3] + inputChar
        inputChar = self._reflector.get_rev_output(inputChar)
        for rotor,shift in zip(list(reversed(self._RotorList)),list(reversed(self._shiftList[1:4]))):
            inputChar = shift - inputChar
            inputChar = rotor.get_rev_output(inputChar)
        
        inputChar = self._shiftList[0] - inputChar
        self.moveShift()
        return inputChar

    def moveShift(self):
        '''
        The moveShift method ensures that even if one character is typed more
        than once in succession, the code genrated is different. It is like the 
        actuator bar of the machine and the notches on the rotors combined. 
        The function is essentially to keep incrementing the shift of the first rotor
        and then if the shift of first rotor reaches beyond 25 then the next rotor is
        incremented and further it moves from Rotor2 to Rotor3.
        '''
        self._shiftList[0].incShift()
        if self._shiftList[1].incShift() > 0:
            if self._shiftList[2].incShift() > 0:
                self._shiftList[3]



                    







if __name__ == "__main__":
    r1 = EnigmaInterface()
    r2 = EnigmaInterface()
    print(r1.get_cipherText("arwinder"))
    print(r2.get_plainText("zypqusrh"))
    