import math
import numpy as np

# This function converts the raw SDR samples into the unprocessed SDR bitstream which then needs to be processed.
# Returns them as a string. Consult the following link for information on how this bitstream works:
# https://web.stanford.edu/class/ee26n/Assignments/Assignment4.html 
def getRawBits(sample_block, tuning_factor, debug_info):
    noise_floor = sum(sample_block[0::10]) / math.floor(len(sample_block)/10) # Averages every 10th sample (for speed) to find the noise floor

    if(debug_info):
        print("The threshold is:", noise_floor)

    bits = np.where(sample_block > noise_floor * tuning_factor, 1, 0) # If a sample is above the noise floor by a certain factor set by tuning_factor,
                                                            # then it is a 1, if not, it is a 0

    

    bits_str = ""
    

    for i in range(len(bits)):
        bits_str += (str(int(bits[i])))  # converts the bits from an array to a string for easier processing
    
    return bits_str


# This function takes in the raw ADS-B bitstream (as a string) and returns the output as described in the ICD.
def getADSBBits(rawBits, debug_info, debug_file, debug_file_loc):
    if(debug_info):
        print("Processing new block of", len(rawBits), "bits:")

    message_loc = rawBits.find("1010000101000000") # searches for the first preamble it can find
    
    
    # This block will only execute on a single preamble, even if multiple are present in the sample block.
    # This results in a portion of messages being missed altogether. This will need to be improved for our final project.



    output = []

    if(message_loc != -1) & (message_loc + 240 < len(rawBits)): 

        message_start = message_loc + 16  # this is where the actual ADS-B data starts
        
        message = np.empty(112, dtype=int)


        for i in range (112):             # ADS-B messages are 112 bits long

            twoBits = rawBits[message_start + i*2] +  rawBits[message_start + i*2 + 1]
            # each bit of data is represented by two raw binary data bits, so we extract them
            # and process them two at a time
            if(twoBits == "01"):
                message[i] = 0
            elif(twoBits == "10"):
                message[i] = 1
            elif(twoBits == "11"):
                message[i] = 1
            elif(twoBits == "00"):
                message[i] = 0
            else:
                message[i] = '0'
            # "01" and "10" represent valid message data, the rest are error states. Error handling of some sort will need to be added here.

        output.append(message)
    

    




    if(debug_file):
        file = open(debug_file_loc, "a")

        np.set_printoptions(threshold=np.inf, linewidth = 512) 
        for i in range(len(output)):
            file.write(str(int(output[i]))) # writes the raw data in the output to the debug file
        

        file.write("\n\n")

        file.close()

    return output




# getMessages takes in an array of raw SDR samples and converts them into ADS-B messages following the format set out in the 
# interface control document. Essentially this is what our GNURadio code did. It's now been split up into a couple 
# smaller functions.
def getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc):

    rawBitStream = getRawBits(sample_block, tuning_factor, debug_info)
    messages = getADSBBits(rawBitStream, debug_info, debug_file, debug_file_loc)



    return messages
