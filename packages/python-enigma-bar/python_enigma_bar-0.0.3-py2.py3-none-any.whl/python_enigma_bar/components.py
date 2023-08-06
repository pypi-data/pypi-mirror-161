'''
The rotor types are defined here, 
These values are 26 char long strings 
the character at a poisition represents the
character to which the alpha bet of that position is 
converted to by that rotor. For example 'A' or 'a' has a position 
0 in the alphabet and b has 2 and c has 3. If a rotor of 
type "IC" is used then according to the string 'a' will
be converted to 'D' and 'b' to 'M'.
'''

rotor_types = {"IC":"DMTWSILRUYQNKFEJCAZBPGXOHV",
                "IIC":"HQZGPJTMOBLNCIFDYAWVEUSRKX",
                "IIIC":"UQNTLSZFMREHDPXKIBVYGJCWOA",
                "I":"JGDQOXUSCAMIFRVTPNEWKBLZYH",
                "II":"NTZPSFBOKMWRCJDIVLAEYUXHGQ"}
class Shift:
    '''
    This class keeps the track between alignment of various rotors.
    The metal contact numbered 1 on first rotor may be in contact with a rotor 
    numbered 4 on rotor 2. This leads a shift in the character as it moves from one 
    rotor to next. This is done by objects of shift class.
    '''
    def __init__(self,value:int) -> None:
        '''
        By default the Shift class only has a value that keeps track of the
        value by which the input gets shifted.
        '''
        self._value = value
    
    def incShift(self) -> int :
        '''
        This method increases the value of shift by one. If the incremented value is more
        than 25 then it comes back to zero.
        The return value shows whether the shift has be reset to zero or no.
        In real world a shift value increment refers to the actuator bar of the machine
        moving the rotor after each letter is typed.
        ''' 
        self._value = (self._value+1)
        if int(self._value/26) > 0:
            self._value%=26
            return 1 
        self._value%=26
        return 0

    def __add__(self,num: Shift) -> int:
        '''
        returns an integer value when shift is added to an integer
        '''
        out = num + self._value 
        return out%26

    def __sub__(self,num):
        '''
        returns an integer value when shift and an integer are subtracted.
        '''
        out = num - self._value
        return out%26
    

    def __repr__(self):
        '''
        the string representation of a Shift is just its value
        '''
        return str(self._value)
    


class Rotor:
    def __init__(self,rotor_type:str):
        '''
        The Rotor class creates objects that represent a rotor in enigma machine
        a rotor gets an input and converts it into a different character.
        The inside of a rotor is wires mapping one contact on one side to a 
        different contact on the other side.
        The constructor requires a rotor type which should be a key for the
        rotor types dictionary given above.
        '''
        self._mapping = rotor_types[rotor_type]
    
    def get_output(self,input:int)-> int:
        '''
        The method that converts the input to the output across the rotor
        it simple means the getting the character from the rotor type string 
        based on the int position of input character.
        '''
        return ord(self._mapping[input]) - 65       
    
    def get_rev_output(self,input:int)->int:
        '''
        the method is same it gets the output from the other side.
        this is done by finding where the char being inpput is present 
        on the string of rotor type and return its index.
        '''
        return self._mapping.index(chr(input+65))

class SwitchBoard:
    def __init__(self):
        '''
        Swtich board is simple a facility to finally flip the letters 
        at the code before outputting them. This can be done by adding a short 
        cable between two letters on the switch board.
        This simply replaces the input character to the output one.
        '''
        self._mapping = {}
        self._revMapping = {}
    
    def add_Short(self,input:int,output:int)->None:
        '''
        This method allows the addition of a short cable between 
        input and output int representation of characters.
        The mapping and revMappping are used to show that shorts are 
        symmetric.s
        '''
        self._mapping[input] = output
        self._revMapping[output] = input

    def get_output(self,input:int)->int:
        '''
        Get a output from the switchboad according to the shorting cables that have 
        been applied to it. The method checks in both mapping and reMapping function.
        '''
        if input in self._mapping.keys():
            return self._mapping[input]
        if input in self._revMapping.keys():
            return self._revMapping[input]
        return input
    


if __name__ == "__main__":
    r = Shift(1)
    print(dir(r))
    r.incShift()


