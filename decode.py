#decode single buffer from demod module
#Last Update : 03/04/23

#different libraries
import numpy as np
from DF17_decoding_functions import decode_iden, decode_sur_pos, decode_air_pos, decode_air_velo
import pyModeS as pms
import folium


# This class will contain all the information for a single aircraft.
# All planes are stored in the "aircraft" array. The functions below the 
# plane_class are created to make updating the array easier.
# Simply call the updateArray functions with the array, ID, and information to be added
# and it will take care of the rest. 

class plane_class:
    def __init__(self, ID): # this happens whenever a new plane is discovered: all variables are blank by default
        self.ID = ID
        self.lat = []
        self.long = []
        self.alt = []
        self.heading = []
        self.vel = []

    def updatePos(self, newLat, newLong, newAlt): # appends the new position of the plane to their respective arrays
        self.lat.append(newLat)
        self.long.append(newLong)
        self.alt.append(newAlt)
    
    def updateHeading(self, newHeading): # updates heading 
        self.heading.append(newHeading)

    def updateVelocity(self, newVel): # updates velocity
        self.vel.append(newVel)

    def ID(self): return self.ID # these 6 functions just let you access the data inside the plane object
    def lat(self): return self.lat
    def long(self): return self.long
    def heading(self): return self.heading
    def vel(self): return self.vel
    def alt(self): return self.alt

def updateArrayPos(aircraft, newLat, newLong, newAlt, ID):
    isPresent = False # stores whether or not the ID is located in aircraft

    for plane in aircraft:
        if plane.ID == ID: # if the plane is found, update it and end the loop immediately
            plane.updatePos(newLat, newLong, newAlt)
            isPresent = True
            break
    
    if (not isPresent): # if the ID isn't found, create a new plane, update it, then add it to the array
        plane = plane_class(ID)
        plane.updatePos(newLat, newLong)
        aircraft.append(plane)

def updateArrayVel(aircraft, newVel, newHeading, ID):
    isPresent = False 

    for plane in aircraft:
        if plane.ID == ID:
            plane.updateHeading(newHeading)
            plane.updateVelocity(newVel)
            isPresent = True
            break
    
    if (not isPresent):
        plane = plane_class(ID)
        plane.updateHeading(newHeading)
        plane.updateVelocity(newVel)
        aircraft.append(plane)






# --- Function Definitions ---

# --- Decodes DF-17 Message Type ---
def DF17_decode(msg_in, counter_array, msg_array_true, ICAO_array, aircraft):

    out = 0
    #CRC check within each message
    integer_msg = int(msg_in, 2)
    msg_hex = hex(integer_msg)
    rem = pms.crc(msg_hex)
    if rem != 0:
        print("ERROR: CRC Error")
        return counter_array, msg_array_true, ICAO_array

    #split bin into diff message components based of Table 1.1
    indices = [0, 5, 8, 32, 37, 88, 112]
    parts = [msg_in[i:j] for i,j in zip(indices, indices[1:]+[None])]

    #check that DF = 17
    if parts[0] != '10001':
        print("ERROR: DF != 17")
        return counter_array, msg_array_true, ICAO_array
    
    #Capability Set
    cap = int(parts[1], 2)

    #ICAO address
    ICAO = parts[2]

    #actual message/decoding of said message
    TC_bin = parts[3]
    TC = int(TC_bin, 2)
    msg = parts[4]

    print(TC)

    #Do needed message decode based on TC

    #Aircraft Ident
    if TC == 1 or TC == 2 or TC == 3 or TC == 4:
        out = decode_iden(msg, TC_bin)

    #Surface Pos
    if TC == 5 or TC == 6 or TC == 7 or TC == 8:

        #see if another message of same type exists

        #no other message
        if counter_array[0] == 0:
            msg_array_true.append(msg)
            msg_array_true.append(TC)
            msg_array_true.append(ICAO)
            counter_array[0] = 1
            return counter_array, msg_array_true, ICAO_array
        
        
        else: 
            #if other messages exist
            if counter_array[0] == 1:

               
                #check if any same ICAO addresses
                ICAO_array = msg_array_true[3::3]

                #double check ICAO exists
                if len(ICAO_array) == 0:
                    #Append message in this case?
                    return counter_array, msg_array_true, ICAO_array

                for i in range(len(ICAO_array)):
                    if ICAO_array[i] == ICAO:

                        #not sure conds are correct
                        #double checks type code
                        if msg_array_true[3*i+2] == 5 or msg_array_true[3*i+2] == 6 or msg_array_true[3*i+2] == 7 or msg_array_true[3*i+2] == 8:
                            out = decode_sur_pos(msg_array_true[i*3+1], msg, msg_array_true[3*i+3], ICAO)
                            
                            #if good output delete old message and append new
                            if out != 'ERROR':
                                del msg_array_true[i*3+1]
                                del msg_array_true[3*i+1]
                                del msg_array_true[3*i+1]
                                msg_array_true.append(msg)
                                msg_array_true.append(TC)
                                msg_array_true.append(ICAO)

                            #if good output print to terminal/ text file
                                if out:
                                    if out != 'ERROR':
                                        lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC), ' | Msg: ', str(out)]
                                        
                                        out_str = str(out)
                                        out_vect = out_str.split(",")
                                        out_lat = float(out_vect[2])
                                        out_long = float(out_vect[3])

                                        print(lines)
                                        print("This is output msg:", str(out))
                                        with open('output.txt', 'a') as f:
                                            for line in lines:
                                                f.write(''.join(line))
                                            f.write('\n')
                                            
                                        return counter_array, msg_array_true, ICAO_array,

                    #if no match or no good output, append and leave
                    if i == len(ICAO_array):
                        if msg_array_true[3*i+2] != 5 or msg_array_true[3*i+2] != 6 or msg_array_true[3*i+2] != 7 or msg_array_true[3*i+2] != 8:
                            msg_array_true.append(msg)
                            msg_array_true.append(TC)
                            msg_array_true.append(ICAO)

            else:

                #if for some reason counter goes over reset
                #could add hard reset in future
                counter_array[0] = 0
                return counter_array, msg_array_true, ICAO_array

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

            return counter_array, msg_array_true, ICAO_array
        
        
        else: 
            #if message exists
            if counter_array[1] == 1:
               
                
                #check if same ICAO address and TC
                ICAO_array = msg_array_true[3::3]

                
                if len(ICAO_array) == 0:
                    return counter_array, msg_array_true, ICAO_array

                
                #pull msgs for specific set based on icao array placement
                for i in range(len(ICAO_array)):
                    
                    if ICAO_array[i] == ICAO:
                        if msg_array_true[3*i+2] == TC:
                            out = decode_air_pos(msg_array_true[i*3+1], msg, bin(msg_array_true[3*i+2]), msg_array_true[3*i+3], ICAO)
                                
                            #if good output delete old message and append new
                            if out != 'ERROR':
                                del msg_array_true[i*3+1]
                                del msg_array_true[3*i+1]
                                del msg_array_true[3*i+1]
                                msg_array_true.append(msg)
                                msg_array_true.append(TC)
                                msg_array_true.append(ICAO)

                            #if good output print to terminal/ text file
                                if out:
                                    if out != 'ERROR':
                                        lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC), ' | Msg: ', str(out)]
                                        
                                        out_str = str(out)
                                        out_vect = out_str.split(",")
                                        out_lat = float(out_vect[1])
                                        out_long = float(out_vect[2])
                                        updateArrayPos(aircraft, out[1], out[2], out[3], ICAO)

                                        with open('output.txt', 'a') as f:
                                            for line in lines:
                                                f.write(''.join(line))
                                            f.write('\n')

                                        return counter_array, msg_array_true, ICAO_array
                   
                   #if no match or no good output, append and leave
                    if i == len(ICAO_array) & msg_array_true[3*i+2] != TC:
                        msg_array_true.append(msg)
                        msg_array_true.append(TC)
                        msg_array_true.append(ICAO)

                
            else:
                #reset if counter goes over 1
                counter_array[1] = 0
                return counter_array, msg_array_true, ICAO_array

    #airborne velocities
    if TC == 19:
        out = decode_air_velo(msg, TC_bin)
        updateArrayVel(aircraft, out[5], out[6], ICAO)

    #airborne pos GNSS
    if TC == 20 or TC == 21 or TC == 22:

        #see if existing messages
        if counter_array[2] == 0:
            msg_array_true.append(msg)
            msg_array_true.append(TC)
            msg_array_true.append(ICAO)
            counter_array[2] = 1
            return counter_array, msg_array_true, ICAO_array
        
        
        else: 
            #if message exists
            if counter_array[2] == 1:
               
               #checks if ICAO and TC the same and computes
                ICAO_array = msg_array_true[3::3]

                if len(ICAO_array) == 0:
                    return counter_array, msg_array_true, ICAO_array


                for i in range(len(ICAO_array)):
                    if ICAO_array[i] == ICAO:
                        if msg_array_true[3*i+2] == TC:
                            out = decode_air_pos(msg_array_true[i*3+1], msg, bin(msg_array_true[3*i+2]), msg_array_true[3*i+3], ICAO)
                            
                             #if good output delete old message and append new
                            if out != 'ERROR':
                                del msg_array_true[i*3+1]
                                del msg_array_true[3*i+1]
                                del msg_array_true[3*i+1]
                                msg_array_true.append(msg)
                                msg_array_true.append(TC)
                                msg_array_true.append(ICAO)

                            #if good output print to terminal/ text file
                                if out:
                                    if out != 'ERROR':
                                        lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC), ' | Msg: ', str(out)]
                                        print(lines)
                                        out_str = str(out)
                                        out_vect = out_str.split(",")
                                        out_lat = float(out_vect[1])
                                        out_long = float(out_vect[2])
                                        updateArrayPos(aircraft, out_lat, out_long, ICAO)

                                        with open('output.txt', 'a') as f:
                                            for line in lines:
                                                f.write(''.join(line))
                                            f.write('\n')

                                        return counter_array, msg_array_true, ICAO_array
                        
                    #if no match or no good output, append and leave
                    if i == len(ICAO_array) & msg_array_true[3*i+2] != TC:
                        msg_array_true.append(msg)
                        msg_array_true.append(TC)
                        msg_array_true.append(ICAO)
                
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

    #print output to terminal and external Text File for functions without ICAO or TC storage

    if out:
        if out != 'ERROR':
            lines = ['DF: ', str(parts[0]), ' | ICAO: ', str(ICAO), ' | Type Code: ', str(TC), ' | Msg: ', str(out)]
            print(lines)
            with open('output.txt', 'a') as f:
                for line in lines:
                    f.write(''.join(line))
        
                f.write('\n')
    
    out = ""
    return counter_array, msg_array_true, ICAO_array
        

# ---Takes 4096 long message from demod
 
def decode_from_demod(demod_out, counter_array, msg_array_true, ICAO_array, demod_info, aircraft):
    DF17_decode(demod_out, counter_array, msg_array_true, ICAO_array, aircraft)
