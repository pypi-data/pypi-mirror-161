
'''
This is the file where the config can be changed manually by the user.
This is also the default config of the system
You can add change the rotor type,  
you can change shifts 
you can add shorts.
'''
RotorList = ["IC","IIC","IIIC"]  #Always have 3 rotors and their types here.
Reflector = "I"                  #Reflector is also a type of rotor and needs to have a type
ShiftList = [22,2,24,25]         #There are always 4 shifts one between input and first rotor
                                 #others between others rotors and the last between andd third an reflector
shorts = [(1,5),(2,9)]           #Each tuple in the list has two ints between 0-25. The first one is simply
                                 #the input and the second is what it is replavced with. Physically these
                                 #resembe the shorting wires on the switchboard

