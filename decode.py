#decode single buffer/ message line (112 long DF17)
#might eventually include crc correction later? idk
#Last Update : 12/30/22

#different libraries
import numpy as np
from Decoding import decode_iden, decode_air_pos, decode_air_velo
import pyModeS as pms

# --- Function Definitions ---

# --- Decodes DF-17 Message Type ---
def DF17_decode(msg_in):

    #CRC check within each message
    integer_msg = int(msg_in, 2)
    msg_hex = hex(integer_msg)
    rem = pms.crc(msg_hex)
    if rem != 0:
        return

    #split bin into diff message components based of Table 1.1
    indices = [0, 5, 8, 32, 37, 88, 112]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:]+[None])]

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
    msg = parts[4]

    #Do needed message decode based on TC
    if TC == 1 or TC == 2 or TC == 3 or TC == 4:
        print('Aircraft Ident')
        decode_iden(msg, TC_bin)
    if TC == 5 or TC == 6 or TC == 7 or TC == 8:
        print('Surface Position')
        #decode_air_pos()
    if TC == 9 or TC == 10 or TC == 11 or TC == 12 or TC == 13 or TC == 14 or TC == 15 or TC == 16 or TC == 17 or TC == 18:
        print('Airborne position Baro')
    if TC == 19:
        print('Airborne velocities')
        decode_air_velo(msg, TC_bin)
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
    
    #print and output table
    lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC)]
    with open('output.txt', 'a') as f:
        for line in lines:
            f.write(''.join(line))
        f.write('\n')
        

# ---Takes 4096 long message from demod
def decode_from_demod(demod_out):
    
    #check if 0 messages 
    if demod_out[0] == '0':
        return
    else:

        #split the different messages apart
        msg_array = demod_out.split('2')
        num_msg = len(msg_array) - 1

        #take the last message and take off the -1s at end
        last = msg_array[num_msg]
        msg_array[num_msg] = last.replace('-1', '')
        
        #decode each individual message
        for i in range(num_msg+1):
            if msg_array[i] != "":
                DF17_decode(msg_array[i])
        

            

# --- Main Program ---

"""
---Test the DF17_decode---

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
"""


#message from demod output
test_output = '210001101010010000100000011010110001000000010110011000011011100011100001100101100111000000101011101100000100110002100011010100100001000000110101100010000000101100110000110111000111000011001011001110000001010111011000001001100021000110101001000010000001101011000100000001011001100001101110001110000110010110011100000010101110110000010011000-1-1-1-1'

with open('output.txt', 'w') as f:
      f.write('')

decode_from_demod(test_output)

