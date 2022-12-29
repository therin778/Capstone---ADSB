#Decoding the different message types
#contained within an ADS-B message.
#Last update: 12/29/2022

#Libraries
import math


###########################################################
#This function decodes the aircraft identification message#
###########################################################
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
##############################################################################################################


#####################################################
#This function decodes the airborne position message#
#####################################################
def decode_air_pos(msg1_in, msg2_in, TC_in, ICAO1, ICAO2):
    if ICAO1 != ICAO2:  #Error if the 2 messages are from different aircraft
        print('ERROR')
        return
    
    #Dividing the message data. Message structure: surveillance status (2 bits), single antenna flag (1),
    #altitude (12), time (1), even/odd (1), latitude (12), longitude (12).
    TC = int(TC_in, 2)
    indices = [0, 2, 3, 15, 16, 17, 34, 51]
    parts1 = [msg1_in[i:j] for i,j in zip(indices, indices[1:])]
    parts2 = [msg2_in[i:j] for i,j in zip(indices, indices[1:])]

    #Surveillance status, 4 statuses corresponding to 0-3
    if parts1[0] == '00': print('Surveillance Status: No Condition')
    if parts1[0] == '01': print('Surveillance Status: Permanent Alert')
    if parts1[0] == '10': print('Surveillance Status: Temporary Alert')
    if parts1[0] == '11': print('Surveillance Status: SPI Condition')

    #Assigning even/odd to the 2 messages according to the even/odd bit
    if parts1[4] == '0':
        if parts2[4] == '0':    #Error if both messages are even
            print('ERROR')
            return
        parts_even = parts1
        parts_odd = parts2
    
    if parts1[4] == '1':
        if parts2[4] == '1':    #Error if both messages are odd
            print('ERROR')
            return
        parts_odd = parts1
        parts_even = parts2
    
    #Calculating latitude
    Nz = 15     #Nz = 15 for Mode S
    d_lat_even = 360 / (4 * Nz)
    d_lat_odd = 360 / ((4 * Nz) - 1)
    lat_cpr_even = int(parts_even[5], 2) / (2 ** 17)
    lat_cpr_odd = int(parts_odd[5], 2) / (2 ** 17)
    lat_index = math.floor((59 * lat_cpr_even) - (60 * lat_cpr_odd) + 0.5)

    if parts_even[4] == '1':
        lat = d_lat_even * ((lat_index % 60) + lat_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '0':
       lat = d_lat_even * ((lat_index % 60) + lat_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '1':
       lat = d_lat_odd * ((lat_index % 59) + lat_cpr_odd)
    print('Aircraft Latitude: ', lat, '°', sep = '')  

    #Calculating longitude
    NL = math.floor(2 * math.pi / (math.acos(1 - (1 - math.cos(math.pi / (2 * Nz))) / (math.cos((math.pi * lat) / 180) ** 2))))
    n_even = max(NL, 1)
    n_odd = max(NL - 1, 1)
    d_long_even = 360 / n_even
    d_long_odd = 360 / n_odd
    long_cpr_even = int(parts_even[6], 2) / (2 ** 17)
    long_cpr_odd = int(parts_odd[6], 2) / (2 ** 17)
    long_index = math.floor((long_cpr_even * (NL - 1)) - (long_cpr_odd * NL) + 0.5)

    if parts_even[4] == '1':
        long = d_long_even * ((long_index % n_even) + long_cpr_even)
    if parts_even[4] == '0' and parts_odd == '0':
        long = d_long_even * ((long_index % n_even) + long_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '1':
        long = d_long_odd * ((long_index % n_odd) + long_cpr_odd)
    if long >= 180:
        long -= 360
    print('Aircraft Longitude: ', long, '°', sep = '')
    
    #Calculating altitude
    if TC >= 9 and TC <= 18:    #Type code 9-18 indicates barometric altitude (given in feet)
        #Dividing the altitude message. Bit 8 is the "Q bit", the rest of the message is the altitude data
        indices = [0, 7, 8, 12]
        parts_alt = [parts2[2][i:j] for i,j in zip(indices, indices[1:])]

        if parts_alt[1] == '1':     #A "1" as the Q bit indicates altitude in 25 foot increments
            alt_msg_bin = parts_alt[0] + parts_alt[2]
            alt_msg_dec = int(alt_msg_bin, 2)
            alt = (alt_msg_dec * 25) - 1000
            print('Aircraft Altitude (Barometric):', alt, 'ft.')
        if parts_alt[1] == '0':     #A "0" as the Q bit indicates altitude in 100 foot increments                            
            alt_msg_gray = parts_alt[0] + parts_alt[2]      ##############################
            alt_msg_bin = gray_to_bin(alt_msg_gray)         ##Check this later I don't
            alt_msg_dec = int(alt_msg_bin, 2)               ##think it's right, it's hard
            alt = (alt_msg_dec * 100) - 1000                ##to find info on this.
            print('Aircraft Altitude (Barometric):', alt, 'ft.')  ##############################

    if TC == 20 or TC == 21 or TC == 22:    #Type code 20-22 indicates GNSS altitude (given in meters)
        alt = int(parts2[2], 2)
        print('Aircraft Altitude (GNSS):', alt, 'm.')
##############################################################################################################


def decode_air_velo(msg_in, TC_in):
    #Dividing the message data. Message structure: sub-type (3 bits), intent change flag (1), IFR capability flag (1)
    #nav. uncertainty category for velo. (3), velocity message (22), vertical rate source bit (1), vertical rate
    # sign bit(1), vertical rate (9), reserved bits (2), GNSS/baro. altitude difference sign bit (1), GNSS/baro.
    #altitude difference (7).
    TC = int(TC_in, 2)
    indices = [0, 3, 4, 5, 8, 30, 31, 32, 41, 43, 44, 51]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:])]

    if parts[10] != '0000000' or parts[10] != '1111111':    #Decoding altitude difference, message DNE if all 1s or 0s
        delta_h = 25 * (int(parts[10], 2) - 1)
        if parts[9] == '1':
            delta_h = delta_h * -1
        print('GNSS / Barometric Altitude Difference: ', delta_h, ' ft.')

    if parts[5] == '0': print('Vertical Rate Source: GNSS')     #Decoding vertical rate
    if parts[5] == '1': print('Vertical Rate Source: Barometer')
    vert_rate = 64 * (int(parts[7], 2) - 1)
    if parts[6] == '0': print('Vertical Rate: Ascending @', vert_rate, 'ft./min.')
    if parts[6] == '1': print('Vertical Rate: Descending @', vert_rate, 'ft./min.')

    #Dividing the velocity data. Message structure for sub-type 1 & 2: E/W component direction (1 bit), E/W
    #velocity (10), N/S component direction (1), N/S velocity (10). Message structure for sub-type 3 & 4:
    #heading status (1), heading (10), air-speed type (1), airspeed (10).
    indices = [0, 1, 11, 12, 22,]
    parts_velo = [parts[4][i:j] for i,j in zip(indices, indices[1:])]

    #Decoding airspeed
    if parts[0] == '001':
        velo_ew = int(parts_velo[1], 2) -1
        velo_ns = int(parts_velo[3], 2) -1
        if parts_velo[0] == '1':
            velo_ew = velo_ew * -1
        if parts_velo[2] == '1':
            velo_ns = velo_ns * -1
        print('Air Speed (kt.):', velo_ew,' East-West,', velo_ns, 'North-South')
    
    if parts[0] == '010':
        velo_ew = 4 * (int(parts_velo[1], 2) -1)
        velo_ns = 4 * (int(parts_velo[3], 2) -1)
        if parts_velo[0] == '1':
            velo_ew = velo_ew * -1
        if parts_velo[2] == '1':
            velo_ns = velo_ns * -1
        print('Air Speed (kt):', velo_ew, 'East-West, ',velo_ns, 'North-South')

    if parts[0] == '001' or parts[0] == '010':
        total_velo = math.sqrt(velo_ew ** 2 + velo_ns ** 2)
        track_angle = math.atan2(velo_ew, velo_ns) * (360 / (2 * math.pi))
        print('Total Air Speed: ', total_velo, ' kt. @ ', track_angle, '° from North', sep = '')
    
    if parts[0] == '011' or parts[0] == '100':
        total_velo = int(parts_velo[3], 2) -1
        if parts[0] == '100':
            total_velo = total_velo * 4
        if parts_velo[0] == '0':
            print('Heading Not Available')
            print('Total Air Speed: ', total_velo, ' kt.')
        if parts_velo[0] == '1':
            track_angle = int(parts_velo[1], 2) * (360/1024)
            print('Total Air Speed: ', total_velo, ' kt. @ ', track_angle, '° from North', sep = '')
##############################################################################################################


########################################################
#This function converts Gray Code to traditional binary#
########################################################
def gray_to_bin(gray_in):
    bin_out = ''
    bin_out += gray_in[0]
    for i in range(len(gray_in) - 1):  
        if gray_in[i+1] != bin_out[i]:
            bin_out += '1'
        if gray_in[i+1] == bin_out[i]:
            bin_out += '0'
    return bin_out
##############################################################################################################


################################################################################
#Main Program, ADS-B messages used are from the examples on https://mode-s.org/#
################################################################################
msg_iden_bin = '000001011001100001101110001110000110010110011100000'
type_code_iden = '100'

msg_airpos1_bin = '000110000111000001011010110100100001100100010101100'
msg_airpos2_bin = '000110000111000011001000011010111001100010000010010'
type_code_airpos = '10010'
ICAO1_bin = '010000000110001000011101'
ICAO2_bin = '010000000110001000011101'

msg_air_velo = '001010001000000100110010100000010000011100000010111'
type_code_airvelo = '10011'

decode_iden(msg_iden_bin, type_code_iden)
decode_air_pos(msg_airpos1_bin, msg_airpos2_bin, type_code_airpos, ICAO1_bin, ICAO2_bin)
decode_air_velo(msg_air_velo, type_code_airvelo)
