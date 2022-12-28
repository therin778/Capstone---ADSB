#Decoding the different message types
#contained within an ADS-B message.
#Last update: 12/27/2022

import numpy as np

#This function decodes the aircraft identification message,
#which contains the Aircraft Category and the Tail-number.
def decode_identification(msg_in, TC):

    #Dividing the message data. The first 3 bits are Aircraft Category. The rest
    #of the message is the tail number, each character consisting of 6 bits 
    indices = [0, 3, 9, 15, 21, 27, 33, 39, 45, 51]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:])]
    CA = int(parts[0], 2)
    print('Aircraft Category: ', CA)


    if TC == 1: print('Wake Vortex Category: Reserved')
    if CA == 0: print('Wake Vortex Category: No Information')
    if TC == 2:
        if CA == 1: print('Wake Vortex Category: Surface Emergency Vehicle')
        if CA == 3: print('Wake Vortex Category: Surface Service Vehicle')
        if CA == 4 or CA == 5 or CA == 6 or CA == 7: print('Aircraft Category: Ground Obstruction')
    if TC == 3:
        if CA == 1: print('Wake Vortex Category: Glider / Sailplane')
        if CA == 2: print('Wake Vortex Category: Lighter-Than-Air')
        if CA == 3: print('Wake Vortex Category: Parachutist / Skydiver')
        if CA == 4: print('Wake Vortex Category: Ultralight / Hang-Glider / Paraglider')
        if CA == 5: print('Wake Vortex Category: Reserved')
        if CA == 6: print('Wake Vortex Category: Unmanned Aerial Vehicle')
        if CA == 7: print('Wake Vortex Category: Space or Transatmospheric Vehicle')
    if TC == 4:
        if CA == 1: print('Wake Vortex Category: Light')
        if CA == 2: print('Wake Vortex Category: Medium 1')
        if CA == 3: print('Wake Vortex Category: Medium 2')
        if CA == 4: print('Wake Vortex Category: High Vortex Aircraft')
        if CA == 5: print('Wake Vortex Category: Heavy')
        if CA == 6: print('Wake Vortex Category: High Performance and High Speed')
        if CA == 7: print('Wake Vortex Category: Rotorcraft')
    
    tail_number = ''
    for i in range(8):
        if int(parts[i + 1], 2) <= 26: tail_number += chr(int(parts[i + 1], 2) + 64)
            
        if int(parts[i + 1], 2) == 32: tail_number += '_'
            
        if int(parts[i + 1], 2) >= 48 and int(parts[i + 1], 2) <= 57: tail_number += chr(int(parts[i + 1], 2))
            
            
    print('Tail Number: ', tail_number)





# --- Main Program ---
msg_iden_bin = '000001011001100001101110001110000110010110011100000'
type_code = 4

decode_identification(msg_iden_bin, type_code)