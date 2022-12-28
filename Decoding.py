#Decoding the different message types
#contained within an ADS-B message.
#Last update: 12/28/2022


#This function decodes the aircraft identification message,
#which contains the Aircraft Category and the Tail-number.
def decode_iden(msg_in, TC_in):

    #Dividing the message data. The first 3 bits are Aircraft Category. The rest
    #of the message is the tail number, each character consisting of 6 bits 
    TC = int(TC_in, 2)
    indices = [0, 3, 9, 15, 21, 27, 33, 39, 45, 51]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:])]
    CA = int(parts[0], 2)
    print('Aircraft Category: ', CA)

    #The Wake Vortex Category is derived from a combination of the Type Code and the Aircraft Category.
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
    
    #When decoding the Tail-Number, 1-26 corresponds to 'A-Z', 36 corresponds to '_', and 48-57 corresponds to '0-9'.
    tail_number = ''
    for i in range(8):
        if int(parts[i + 1], 2) >= 1 and int(parts[i + 1], 2) <= 26: tail_number += chr(int(parts[i + 1], 2) + 64)
            
        if int(parts[i + 1], 2) == 32: tail_number += '_'
            
        if int(parts[i + 1], 2) >= 48 and int(parts[i + 1], 2) <= 57: tail_number += chr(int(parts[i + 1], 2))
               
    print('Tail-Number: ', tail_number)

def decode_air_pos(msg1_in, msg2_in, TC_in, ICAO1, ICAO2):
    if ICAO1 != ICAO2:
        return
    
    TC = int(TC_in, 2)
    indices = [0, 2, 3, 15, 16, 17, 34, 51]
    parts1 = [msg1_in[i:j] for i,j in zip(indices, indices[1:])]
    parts2 = [msg2_in[i:j] for i,j in zip(indices, indices[1:])]

    SS = int(parts1[0], 2)
    if SS == 0: print('Surveillance Status: No Condition')
    if SS == 1: print('Surveillance Status: Permanent Alert')
    if SS == 2: print('Surveillance Status: Temporary Alert')
    if SS == 3: print('Surveillance Status: SPI Condition')

    if TC >= 9 and TC <= 18:
        indices = [0, 7, 8, 12]
        parts_alt = [parts2[2][i:j] for i,j in zip(indices, indices[1:])]
        if parts_alt[1] == '1':
            alt_msg_bin = parts_alt[0] + parts_alt[2]
            alt_msg_dec = int(alt_msg_bin, 2)
            alt = (alt_msg_dec * 25) - 1000
            print('Aircraft Altitude (Barometric): ', alt)
        if parts_alt[1] == '0':                             ##############################
            alt_msg_gray = parts_alt[0] + parts_alt[2]      ##
            alt_msg_bin = gray_to_bin(alt_msg_gray)         ##Check this later I don't
            alt_msg_dec = int(alt_msg_bin, 2)               ##think it's right, it's hard
            alt = (alt_msg_dec * 100) - 1000                ##to find info on this.
            print('Aircraft Altitude (Barometric): ', alt)  ##############################
    if TC == 20 or TC == 21 or TC == 22:
        alt = int(parts2[2], 2)
        print('Aircraft Altitude (GNSS): ', alt)


def gray_to_bin(gray_in):
    print(gray_in)
    bin_out = ''
    bin_out += gray_in[0]
    for i in range(len(gray_in)-1):  
        if gray_in[i+1] != bin_out[i]:
            bin_out += '1'
        if gray_in[i+1] == bin_out[i]:
            bin_out += '0'
    return bin_out

# --- Main Program ---
msg_iden_bin = '000001011001100001101110001110000110010110011100000'
type_code_iden = '100'

msg_airpos1_bin = '000110000111000001011010110100100001100100010101100'
msg_airpos2_bin = '000110000111000011001000011010111001100010000010010'
type_code_airpos = '10010'
ICAO1_bin = '010000000110001000011101'
ICAO2_bin = '010000000110001000011101'

decode_iden(msg_iden_bin, type_code_iden)
decode_air_pos(msg_airpos1_bin, msg_airpos2_bin, type_code_airpos, ICAO1_bin, ICAO2_bin)
