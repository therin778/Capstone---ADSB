#Decoding the different message types
#contained within an ADS-B message.
#Last update: 12/30/2022

#Libraries
import math


###########################################################
#This function decodes the aircraft identification message#
###########################################################
def decode_iden(msg_in, TC_in):
    iden_out = ['AC', 'WV', 'TN']
    #Dividing the message data. The first 3 bits are Aircraft Category. The rest
    #of the message is the tail number, each character consisting of 6 bits 
    TC = int(TC_in, 2)
    indices = [0, 3, 9, 15, 21, 27, 33, 39, 45, 51]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:])]
    CA = int(parts[0], 2)
    #print('Aircraft Category: ', CA)
    iden_out[0] = CA

    #The Wake Vortex Category is derived from a combination of the Type Code and the Aircraft Category.
    if TC == 1: iden_out[1] = 'Reserved'
    if CA == 0: iden_out[1] = 'No Information'
    if TC == 2:
        if CA == 1: iden_out[1] = 'Surface Emergency Vehicle'
        if CA == 3: iden_out[1] = 'Surface Service Vehicle'
        if CA == 4 or CA == 5 or CA == 6 or CA == 7: iden_out[1] = 'Ground Obstruction'
    if TC == 3:
        if CA == 1: iden_out[1] = 'Glider / Sailplane'
        if CA == 2: iden_out[1] = 'Lighter-Than-Air'
        if CA == 3: iden_out[1] = 'Parachutist / Skydiver'
        if CA == 4: iden_out[1] = 'Ultralight / Hang-Glider / Paraglider'
        if CA == 5: iden_out[1] = 'Reserved'
        if CA == 6: iden_out[1] = 'Unmanned Aerial Vehicle'
        if CA == 7: iden_out[1] = 'Space or Transatmospheric Vehicle'
    if TC == 4:
        if CA == 1: iden_out[1] = 'Light'
        if CA == 2: iden_out[1] = 'Medium 1'
        if CA == 3: iden_out[1] = 'Medium 2'
        if CA == 4: iden_out[1] = 'High Vortex Aircraft'
        if CA == 5: iden_out[1] = 'Heavy'
        if CA == 6: iden_out[1] = 'High Performance and High Speed'
        if CA == 7: iden_out[1] = 'Rotorcraft'
    
    #When decoding the Tail-Number, 1-26 corresponds to 'A-Z', 36 corresponds to '_', and 48-57 corresponds to '0-9'.
    tail_number = ''
    for i in range(8):
        if int(parts[i + 1], 2) >= 1 and int(parts[i + 1], 2) <= 26: tail_number += chr(int(parts[i + 1], 2) + 64)
            
        if int(parts[i + 1], 2) == 32: tail_number += '_'
            
        if int(parts[i + 1], 2) >= 48 and int(parts[i + 1], 2) <= 57: tail_number += chr(int(parts[i + 1], 2))
               
    iden_out[2] = tail_number
    return iden_out 

    ###################################################################################
    #iden_out format: [0] aircraft category, [1] wake vortex category, [2] tail number#
    ####################################################################################

##############################################################################################################


#####################################################
#This function decodes the airborne position message#
#####################################################
def decode_air_pos(msg1_in, msg2_in, TC_in, ICAO1, ICAO2):
    airpos_out = ['SS', 'LAT', 'LONG', 'ALT', 'ALT_TYPE']
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
    if parts1[0] == '00': airpos_out[0] = 'No Condition'
    if parts1[0] == '01': airpos_out[0] = 'Permanent Alert'
    if parts1[0] == '10': airpos_out[0] = 'Temporary Alert'
    if parts1[0] == '11': airpos_out[0] = 'SPI Condition'

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
    airpos_out[1] = lat  

    #Calculating longitude
    NL = math.floor((2 * math.pi) / (math.acos(1 - (1 - math.cos(math.pi / (2 * Nz))) / (math.cos((math.pi * lat) / 180) ** 2))))
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
    airpos_out[2] = long
    
    #Calculating altitude
    if TC >= 9 and TC <= 18:    #Type code 9-18 indicates barometric altitude (given in feet)
        #Dividing the altitude message. Bit 8 is the "Q bit", the rest of the message is the altitude data
        indices = [0, 7, 8, 12]
        parts_alt = [parts2[2][i:j] for i,j in zip(indices, indices[1:])]

        if parts_alt[1] == '1':     #A "1" as the Q bit indicates altitude in 25 foot increments
            alt_msg_bin = parts_alt[0] + parts_alt[2]
            alt_msg_dec = int(alt_msg_bin, 2)
            alt = (alt_msg_dec * 25) - 1000
            airpos_out[3] = alt
            airpos_out[4] = 'BARO'
        if parts_alt[1] == '0':     #A "0" as the Q bit indicates altitude in 100 foot increments                            
            alt_msg_gray = parts_alt[0] + parts_alt[2]      ##############################
            alt_msg_bin = gray_to_bin(alt_msg_gray)         ##Check this later I don't
            alt_msg_dec = int(alt_msg_bin, 2)               ##think it's right, it's hard
            alt = (alt_msg_dec * 100) - 1000                ##to find info on this.
            airpos_out[3] = alt                             ##############################
            airpos_out[4] = 'BARO'

    if TC == 20 or TC == 21 or TC == 22:    #Type code 20-22 indicates GNSS altitude (given in meters)
        alt = int(parts2[2], 2)
        airpos_out[3] = alt
        airpos_out[4] = 'GNSS'

    return airpos_out

    ########################################################################################################
    #airpos_out format: [0] security status, [1] latitude, [2] longitude, [3] altitude, [4] altitude source#
    #(BARO in feet; GNSS in meters)                                                                        #                                     
    ########################################################################################################

##############################################################################################################


####################################################
#This function decodes the surface position message#
####################################################
def decode_sur_pos(msg1_in, msg2_in, ICAO1, ICAO2):
    ref_lat = 39.212001     #Reference coords are the runway at the OU airport. Example
    ref_long = -82.229126   #messages may not match since the use a different reference.

    surpos_out = ['GS', 'GT', 'LAT', 'LONG']
    if ICAO1 != ICAO2:  #Error if the 2 messages are from different aircraft
        print('ERROR')
        return
    #Dividing the message data. Message structure: ground speed (7 bits), ground track status (1),
    #ground track (7), time (1), even/odd (1), latitude (17), longitude (17).
    indices = [0, 7, 8, 15, 16, 17, 34, 51]
    parts1 = [msg1_in[i:j] for i,j in zip(indices, indices[1:])]
    parts2 = [msg2_in[i:j] for i,j in zip(indices, indices[1:])]

    #Decoding surface speed, idk if this is right but the mode-s.org doc wasn't that clear, not super important anyway
    encoded_speed = int(parts2[0], 2)
    if encoded_speed == 0: surpos_out[0] = 'NO INFO'
    if encoded_speed != 0 and encoded_speed != 124:
        if encoded_speed == 1: sur_velo = 0
        if encoded_speed >= 2 and encoded_speed <= 8: sur_velo = encoded_speed * 0.125
        if encoded_speed >= 9 and encoded_speed <= 12: sur_velo = encoded_speed * 0.25
        if encoded_speed >= 13 and encoded_speed <= 38: sur_velo = encoded_speed * 0.5
        if encoded_speed >= 39 and encoded_speed <= 93: sur_velo =  encoded_speed * 1
        if encoded_speed >= 94 and encoded_speed <= 108: sur_velo = encoded_speed * 2
        if encoded_speed >= 109 and encoded_speed <= 123 : sur_velo = encoded_speed * 5
        surpos_out[0] = sur_velo
    if encoded_speed == 124: surpos_out[0] = '>175'

    #Decoding ground track
    if parts2[1] == '0':
        surpos_out[1] = 'NO INFO'
    if parts2[1] == '1':
        gnd_track = (360 * int(parts2[2], 2)) / 128
        surpos_out[1] = gnd_track

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

    #Decoding latitude
    Nz = 15     #Nz = 15 for Mode S
    d_lat_even = 90 / (4 * Nz)
    d_lat_odd = 90 / ((4 * Nz) - 1)
    lat_cpr_even = int(parts_even[5], 2) / (2 ** 17)
    lat_cpr_odd = int(parts_odd[5], 2) / (2 ** 17)
    lat_index = math.floor((59 * lat_cpr_even) - (60 * lat_cpr_odd) + 0.5)

    if parts_even[4] == '1':    
        lat = d_lat_even * ((lat_index % 60) + lat_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '0':
       lat = d_lat_even * ((lat_index % 60) + lat_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '1':
       lat = d_lat_odd * ((lat_index % 59) + lat_cpr_odd)
    lat1 = lat - 90
    delta = abs(lat - ref_lat)
    delta1 = abs(lat1 - ref_lat)
    if min(delta, delta1) == delta1: lat = lat1
    surpos_out[2] = lat

    #Decoding longitude
    NL = math.floor((2 * math.pi) / (math.acos(1 - (1 - math.cos(math.pi / (2 * Nz))) / (math.cos((math.pi * lat) / 180) ** 2))))
    n_even = max(NL, 1)
    n_odd = max(NL - 1, 1)
    d_long_even = 90 / n_even
    d_long_odd = 90 / n_odd
    long_cpr_even = int(parts_even[6], 2) / (2 ** 17)
    long_cpr_odd = int(parts_odd[6], 2) / (2 ** 17)
    long_index = math.floor((long_cpr_even * (NL - 1)) - (long_cpr_odd * NL) + 0.5)

    if parts_even[4] == '1':
        long = d_long_even * ((long_index % n_even) + long_cpr_even)
    if parts_even[4] == '0' and parts_odd == '0':
        long = d_long_even * ((long_index % n_even) + long_cpr_even)
    if parts_even[4] == '0' and parts_odd[4] == '1':
        long = d_long_odd * ((long_index % n_odd) + long_cpr_odd)
    long1 = long + 90
    long2 = long + 180
    long3 = long + 270
    delta = abs(long - ref_long)
    delta1 = abs(long1 - ref_long)
    delta2 = abs(long2 - ref_long)
    delta3 = abs(long3 - ref_long)
    if min(delta, delta1, delta2, delta3) == delta: long = long
    if min(delta, delta1, delta2, delta3) == delta1: long = long1
    if min(delta, delta1, delta2, delta3) == delta2: long = long2
    if min(delta, delta1, delta2, delta3) == delta3: long = long3
    surpos_out[3] = long
    
    return surpos_out

    ###################################################################################################
    #surpos_out format: [0] ground speed (kt), [1] ground track (degrees), [2] latitude, [3] longitude#
    ###################################################################################################

##############################################################################################################


######################################################
#This function decodes the airborne velocity function#
######################################################
def decode_air_velo(msg_in, TC_in):
    airvelo_out = ['AD', 'VRS', 'VR', 'EW', 'NS', 'TAS', 'TA']
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
        airvelo_out[0] = delta_h

    if parts[5] == '0': airvelo_out[1] = 'GNSS'     #Decoding vertical rate
    if parts[5] == '1': airvelo_out[1] = 'BARO'
    vert_rate = 64 * (int(parts[7], 2) - 1)
    if parts[6] == '1': vert_rate = vert_rate * -1
    airvelo_out[2] = vert_rate

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
        airvelo_out[3] = velo_ew
        airvelo_out[4] = velo_ns
    
    if parts[0] == '010':
        velo_ew = 4 * (int(parts_velo[1], 2) -1)
        velo_ns = 4 * (int(parts_velo[3], 2) -1)
        if parts_velo[0] == '1':
            velo_ew = velo_ew * -1
        if parts_velo[2] == '1':
            velo_ns = velo_ns * -1
        airvelo_out[3] = velo_ew
        airvelo_out[4] = velo_ns

    if parts[0] == '001' or parts[0] == '010':
        total_velo = math.sqrt((velo_ew ** 2) + (velo_ns ** 2))
        track_angle = math.atan2(velo_ew, velo_ns) * (360 / (2 * math.pi))
        airvelo_out[5] = total_velo
        airvelo_out[6] = track_angle
    
    if parts[0] == '011' or parts[0] == '100':
        airvelo_out[3] = 'NO INFO'
        airvelo_out[4] = 'NO INFO'
        total_velo = int(parts_velo[3], 2) -1
        if parts[0] == '100':
            total_velo = total_velo * 4
        if parts_velo[0] == '0':
            airvelo_out[5] = total_velo
            airvelo_out[6] = 'NO INFO'
        if parts_velo[0] == '1':
            track_angle = int(parts_velo[1], 2) * (360/1024)
            airvelo_out[5] = total_velo
            airvelo_out[6] = track_angle

    return airvelo_out

    #############################################################################################################
    #airvelo_out format: [0] GNSS/BARO altitude difference, [1] vertical rate source, [2] vertical rate (ft/min)#
    #[3] E/W velo (kt), [4] N/S velo (kt), [5] total air speed (kt), [6] track angle (degrees)                  #
    #############################################################################################################

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

msg_surpos1_bin = '010101010110010001110000111001100111100100011001101'
msg_surpos2_bin = '010100010100011010100110010001111111010111010111101'

msg_air_velo = '001010001000000100110010100000010000011100000010111'
type_code_airvelo = '10011'

iden = decode_iden(msg_iden_bin, type_code_iden)
print('Identification Message:')
print(iden)
airpos = decode_air_pos(msg_airpos1_bin, msg_airpos2_bin, type_code_airpos, ICAO1_bin, ICAO2_bin)
print('Air Position Message:')
print(airpos)
surpos = decode_sur_pos(msg_surpos1_bin, msg_surpos2_bin, ICAO1_bin, ICAO2_bin)
print('Surface Position Message')
print(surpos)
airvelo = decode_air_velo(msg_air_velo, type_code_airvelo)
print('Airborne Velocity Message')
print(airvelo)
