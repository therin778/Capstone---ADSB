#decode single buffer/ message line (112 long DF17)
#might eventually include crc correction later? idk
#Last Update : 12/26/22

#different libraries
import numpy as np
import pyModeS as pms

# --- Function Definitions ---

def DF17_decode(msg_in):

    #split bin into diff message components
    indices = [0, 5, 8, 32, 88, 112]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:]+[None])]
    print(parts)

    #check that DF = 17
    if parts[0] != '10001':
        return
    
    

# --- Main Program ---
#dummy data in hex
#msg_hex = '8D4840D6202CC371C32CE0576098'
msg_bin = '1000110101001000010000001101011000100000001011001100001101110001110000110010110011100000010101110110000010011000'
integer_msg = int(msg_bin, 2)
msg_hex = hex(integer_msg)


#check for crc, will use premade function until new one built
#I think all ads-b messages have total crc remainder of 0, source https://mode-s.org/decode/content/ads-b/8-error-control.html
rem = pms.crc(msg_hex)

if rem == 0:
    DF17_decode(msg_bin)
   
