#decode single buffer/ message line (112 long DF17)
#might eventually include crc correction later? idk
#Last Update : 12/26/22

#different libraries
import numpy as np
import pyModeS as pms

# --- Function Definitions ---

def DF17_decode(msg_in):

    #split bin into diff message components based of Table 1.1
    indices = [0, 5, 8, 32, 37, 88, 112]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:]+[None])]
    print(parts)

    #check that DF = 17
    if parts[0] != '10001':
        return
    
    #Capability Set
    cap = int(parts[1], 2)

    #ICAO address
    ICAO = parts[2]

    #actual message/decoding of said message
    TC_bin = parts[3]
    TC = int(TC_bin, 2)
    print(TC)

    #Do needed message decode based on TC
    if TC == 1 or TC == 2 or TC == 3 or TC == 4:
        print('Aircraft Ident')
    if TC == 5 or TC == 6 or TC == 7 or TC == 8:
        print('Surface Position')
    if TC == 9 or TC == 10 or TC == 11 or TC == 12 or TC == 13 or TC == 14 or TC == 15 or TC == 16 or TC == 17 or TC == 18:
        print('Airborne position Baro')
    if TC == 19:
        print('Airborne velocities')
    if TC == 20 or TC == 21 or TC == 22:
        print('Airborne position GNSS')
    if TC == 23 or TC == 24 or TC == 25 or TC == 26 or TC == 27:
        print('Reserved')
    if TC == 28:
        print('Aircraft status')
    if TC == 29:
        print('State and Status')
    if TC == 31:
        print('Op status')



# --- Main Program ---
#dummy data from 1090 riddle in hex
#msg_hex = '8D4840D6202CC371C32CE0576098'

#start in binary like mod output from ICD
msg_bin = '1000110101001000010000001101011000100000001011001100001101110001110000110010110011100000010101110110000010011000'
integer_msg = int(msg_bin, 2)
msg_hex = hex(integer_msg)


#check for crc, will use premade function until new one built
#I think all ads-b messages have total crc remainder of 0, source https://mode-s.org/decode/content/ads-b/8-error-control.html
rem = pms.crc(msg_hex)

if rem == 0:
    DF17_decode(msg_bin)
   
