import numpy as np


# This function takes in a string of 224 samples where an ADS-B message is located, and extracts the message, testing the 
# difference between samples to verify that it is a real message.


def ADSBbitsToMessage(raw_message, debug_info, delta_tuning):
    output = np.empty(112, dtype=int)
    total = 0 # Stores the total signal strength of each set of bits
    delta = 0 # Stores the difference between the "strong" bit and the "weak" bit for each set of bits

    for i in range(112):
        if raw_message[i*2] > raw_message[i*2+1]:
            output[i] = 1
            total += raw_message[i*2]
            delta += raw_message[i*2] - raw_message[i*2+1]
        else:
            output[i] = 0
            total += raw_message[i*2+1]
            delta += raw_message[i*2+1] - raw_message[i*2]


    isValid = delta > delta_tuning * total  # If random noise is detected as a message, there won't be much difference
    # between the high and low bits, so delta will be small and the message will not be valid.

    return output, isValid


# This function takes in the raw samples and returns the output as described in the ICD.
def getADSBBits(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc):

    i = 0
    output = []

    messageCounter = 0 # tracks the number of valid messages found


    # The program works by a series of checks. A loop is ran over the sample block, and if the given index is the start of the preamble
    # for a valid message, then that message is added to the output. Within the loop, several checks are used to determine if 
    # the message is likely a valid message, or random noise that might coincidentally look like a preamble. 
    while(i < len(sample_block) - 240): # Using a while loop instead of for loop so i can be incremented inside the loop.

        if(sample_block[i] <= sample_block[i+1]): 
            # Very simple check for speed- if the first sample isn't a pulse, no need to process more, because it's not a preamble
            i += 1
            continue



        # This if statement is a way of checking for a preamble. To view the specifics of the preamble go here:
        # https://web.stanford.edu/class/ee26n/Assignments/Assignment4.html 
        # The if statement checks to see if all of the samples that should be pulses are larger than all of the samples that 
        # should be blank.
        # Preambles are 16 samples long- if one is correctly detected, samples 0, 2, 7, and 9 will be a spike, while the rest will be empty.
        # If the preamble doesn't meet all these requirements, continue.
        # The tuning_factor variable can be used to adjust the sensitivity of this part.
        spike = (sample_block[i] + sample_block[i+2] + sample_block[i+7] + sample_block[i+9]) / 4 / tuning_factor
        if(not
            (spike > sample_block[i+1] and spike > sample_block[i+1] and spike > sample_block[i+3] 
            and spike > sample_block[i+6] and spike > sample_block[i+8] 
            and spike > sample_block[i+8] and spike > sample_block[i+10])):
            i +=1
            continue


        # If we've reached this point, the preamble is in the correct form, but this could also happen because of random noise. 
        # The part that converts the samples to a message also checks the message itself using the delta method- since each bit
        # should consist of a pulse and a blank spot, if the pulses and blank spots aren't very different, the message is likely
        # random noise.
        message, isValid = ADSBbitsToMessage(sample_block[i+16:i+241], debug_info, delta_tuning)
        if(not isValid):
            i += 1 
            continue

        # If we've reached this point without continuing, the message is likely valid, so add it to the output
        output.append(message)
        i += 240 # skip over the entire message we just read, no need to check it again
        messageCounter += 1


    if(debug_file and messageCounter != 0):
        file = open(debug_file_loc, "a")

        np.set_printoptions(threshold=np.inf, linewidth = 512) 
        for i in range(114 * messageCounter):
            file.write(str(int(output[i]))) # writes the raw data in the output to the debug file
        

        file.write("\n\n")

        file.close()

    
    return output




# getMessages takes in an array of raw SDR samples and converts them into ADS-B messages following the format set out in the 
# interface control document. Essentially this is what our GNURadio code did. It's now been split up into a couple 
# smaller functions.
def getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc):

        
    messages = getADSBBits(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc)


    return messages