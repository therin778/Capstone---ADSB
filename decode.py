#decode single buffer from demod module
#might eventually include crc correction later? idk
#Last Update : 12/31/22

#different libraries
import numpy as np
from Decoding import decode_iden, decode_sur_pos, decode_air_pos, decode_air_velo
import pyModeS as pms


# --- Function Definitions ---

# --- Decodes DF-17 Message Type ---
def DF17_decode(msg_in, counter_array, msg_array):

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

    #Aircraft Ident
    if TC == 1 or TC == 2 or TC == 3 or TC == 4:
        out = decode_iden(msg, TC_bin)

    #Surface Pos
    #xtra message output? IDK man
    if TC == 5 or TC == 6 or TC == 7 or TC == 8:

        #see if another message of same type exists

        #no other message
        if counter_array[0] == 0:
            msg_array_true.append(msg)
            msg_array_true.append(TC)
            msg_array_true.append(ICAO)
            counter_array[0] = 1
            return
        
        
        else: 
            #if other messages exist
            if counter_array[0] == 1:
               
                #check if any same ICAO addresses
                ICAO_array = msg_array_true[3::3]
                for i in range(len(ICAO_array)):
                    if ICAO_array[i] == ICAO:
                        #not sure conds are correct
                        #double checks type code
                        if msg_array[3*i+2] == 5 or msg_array[3*i+2] == 6 or msg_array[3*i+2] == 7 or msg_array[3*i+2] == 8:
                            out = decode_sur_pos(msg_array_true[i*3+1], msg, msg_array_true[3*i+3], ICAO)
                            
                            #deletes older message
                            del msg_array_true[i*3+1]
                            del msg_array_true[3*i+1]
                            del msg_array_true[3*i+1]
                
                #adds most recent message for ICAO address/ TC
                msg_array_true.append(msg)
                msg_array_true.append(TC)
                msg_array_true.append(ICAO)
                counter_array[0] = 0
            else:

                #if for some reason counter goes over reset
                #could add hard reset in future
                counter_array[0] = 0
                return

    #airborne position baro 
    if TC == 9 or TC == 10 or TC == 11 or TC == 12 or TC == 13 or TC == 14 or TC == 15 or TC == 16 or TC == 17 or TC == 18:

        #see if another message of same type exists

        #if no messages exist
        if counter_array[1] == 0:
            #add attributes
            msg_array_true.append(msg)
            msg_array_true.append(TC)
            msg_array_true.append(ICAO)
            counter_array[1] = 1
            return
        
        
        else: 
            #if message exists
            if counter_array[1] == 1:
               
                #check if same ICAO address and TC
                ICAO_array = msg_array_true[3::3]
                #pull msgs for specific set based on icao array placement
                for i in range(len(ICAO_array)):
                    if ICAO_array[i] == ICAO:
                        if msg_array[3*i+2] == TC:
                            out = decode_air_pos(msg_array_true[i*3+1], msg, bin(msg_array[3*i+2]), msg_array_true[3*i+3], ICAO)
                            #delete old message
                            del msg_array_true[i*3+1]
                            del msg_array_true[3*i+1]
                            del msg_array_true[3*i+1]
                
                #always adds current message
                msg_array_true.append(msg)
                msg_array_true.append(TC)
                msg_array_true.append(ICAO)
                counter_array[1] = 0
            else:
                #reset if counter goes over 1
                counter_array[1] = 0
                return
    #airborne velocities
    if TC == 19:
        out = decode_air_velo(msg, TC_bin)

    #airborne pos GNSS
    if TC == 20 or TC == 21 or TC == 22:

        #see if existing messages
        if counter_array[2] == 0:
            msg_array_true.append(msg)
            msg_array_true.append(TC)
            msg_array_true.append(ICAO)
            counter_array[2] = 1
            return
        
        
        else: 
            #if message exists
            if counter_array[2] == 1:
               
               #checks if ICAO and TC the same and computes
                ICAO_array = msg_array_true[3::3]
                for i in range(len(ICAO_array)):
                    if ICAO_array[i] == ICAO:
                        if msg_array[3*i+2] == TC:
                            out = decode_air_pos(msg_array_true[i*3+1], msg, bin(msg_array[3*i+2]), msg_array_true[3*i+3], ICAO)
                            
                            #deletes old message
                            del msg_array_true[i*3+1]
                            del msg_array_true[3*i+1]
                            del msg_array_true[3*i+1]
                
                #adds existing message
                msg_array_true.append(msg)
                msg_array_true.append(TC)
                msg_array_true.append(ICAO)
                counter_array[2] = 0
            else:
                #if counter goes over return to zero
                counter_array[2] = 0
                return
    #reserved
    if TC == 23 or TC == 24 or TC == 25 or TC == 26 or TC == 27:
        print('Reserved')
    #aircraft status
    if TC == 28:
        print('Aircraft status')
    #State and Status
    if TC == 29:
        print('State and Status')
    #Op status
    if TC == 31:
        print('Op status')

    #print output to terminal
    lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC), ' | Msg: ', str(out)]
    print(lines)

    #print and output table to external text file
    with open('output.txt', 'a') as f:
        for line in lines:
            f.write(''.join(line))
        f.write('\n')
    out = ""
        

# ---Takes 4096 long message from demod
def decode_from_demod(demod_out, counter_array, msg_array_true):
    
    #check if 0 messages 
    if demod_out[0] == '0':
        return
    else:

        demod_out = demod_out[1:]
        #split the different messages apart
        msg_array = demod_out.split('2')
        num_msg = len(msg_array) - 1

        #take the last message and take off the -1s at end
        last = msg_array[num_msg]
        msg_array[num_msg] = last.replace('-1', '')
        
        #decode each individual message
        for i in range(num_msg+1):
            if msg_array[i] != "":
                DF17_decode(msg_array[i], counter_array, msg_array_true)
        

            

# --- Main Program ---

#message from demod output
#test_output = '210001101010010000100000011010110001000000010110011000011011100011100001100101100111000000101011101100000100110002100011010100100001000000110101100010000000101100110000110111000111000011001011001110000001010111011000001001100021000110101001000010000001101011000100000001011001100001101110001110000110010110011100000010101110110000010011000-1-1-1-1'
#test_output = '2100011000100100001000001011101010011101010101011001000111000011100110011110010001100110101000000001000001011000121000110001001000010000010111010100111010100010100011010100110010001111111010111010111101101011000111000000101101-1-1-1-1-1'

#test that includes surf pos, air ident, and air pos messages
test_output = '610001101010010000100000011010110001000000010110011000011011100011100001100101100111000000101011101100000100110002100011010100100001000000110101100010000000101100110000110111000111000011001011001110000001010111011000001001100021000110101001000010000001101011000100000001011001100001101110001110000110010110011100000010101110110000010011000221000110001001000010000010111010100111010101010110010001110000111001100111100100011001101010000000010000010110001210001100010010000100000101110101001110101000101000110101001100100011111110101110101111011010110001110000001011012100011010100000001100010000111010101100011000011100000101101011010010000110010001010110000101000011000111010011121000110101000000011000100001110101011000110000111000011001000011010111001100010000010010011010010010101011010110-1-1-1-1-1'

#indicates if specific message type exists
counter_array = [0, 0, 0]

#collection of prev messages by ICAO address and TC
#storage order: msg, TC, and ICAO: indexes at 1 
msg_array_true = ['']

#clears output document
with open('output.txt', 'w') as f:
      f.write('')

decode_from_demod(test_output, counter_array, msg_array_true)

