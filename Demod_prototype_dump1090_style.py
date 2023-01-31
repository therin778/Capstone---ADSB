import numpy as np
from decode import decode_from_demod
import time

# Change these before running the code!
input_file_loc = r"C:/Users/emssm/Downloads/CMH_airport_data_2_2MSPS"
debug_info = True # Outputs some extra info to the terminal
debug_file = False # Outputs the contents of the output to the next file
debug_file_loc = r"C:/Users/emssm/OneDrive/bits.txt" 


block_size = 3000 # the size of blocks of samples, currently 4096, may be increased if the program lags
tuning_factor = 2.5 # used for calibration. Increase if false messages are detected, decrease if real messages aren't detected.

# This function takes in a string of 224 samples where an ADS-B message is located, and extracts the message.
def ADSBbitsToMessage(raw_message):
    output = np.empty(112)
    for i in range(112):
        if raw_message[i*2] > raw_message[i*2+1]:
            output[i] = 1
        else:
            output[i] = 0
    return output


# Converts IQ samples to magnitudes, in integer form for faster math
def getMagnitudes(sample_block):
    return((np.abs(sample_block) * 1000000).astype(np.int64))



# This function takes in the raw ADS-B bitstream (as a string) and returns the output as described in the ICD.
def getADSBBits(sample_block):

    i = 0
    output = np.ones(block_size) * -1

    messageCounter = 0 # tracks the number of valid messages found

    while(i < len(sample_block) - 240): # Using a while loop instead of for loop so i can be incremented inside the loop

        # The if statement is a way of checking for a preamble. To view the specifics of the preamble go here:
        # https://web.stanford.edu/class/ee26n/Assignments/Assignment4.html 
        # The if statement checks to see if all of the samples that should be pulses are larger than all of the samples that 
        # should be blank.
        # Preambles are 16 samples long- if one is correctly detected, samples 0, 2, 7, and 9 will be a spike, while the rest will be empty.
        spike = (sample_block[i] + sample_block[i+2] + sample_block[i+7] + sample_block[i+9]) / 4 / tuning_factor
        if(spike > sample_block[i+1] and spike > sample_block[i+1] and spike > sample_block[i+3] 
            and spike > sample_block[i+6] and spike > sample_block[i+8] 
            and spike > sample_block[i+8] and spike > sample_block[i+10]):
            message = ADSBbitsToMessage(sample_block[i+16:i+241]) # Should contain a valid message.
            output[messageCounter*113 + 1 : messageCounter*113 + 113] = message
            output[messageCounter*113 + 113] = 2

            i += 240 # skip over the entire message we just read, no need to check it again
            messageCounter += 1

        else:
            i += 1


    output[0] = messageCounter
    
    if(debug_info):
        print(messageCounter, "messages found in that block")   # prints some data that may be useful, more debugging can be added if needed

    if(debug_file and messageCounter != 0):
        file = open(debug_file_loc, "a")

        np.set_printoptions(threshold=np.inf, linewidth = 512) 
        for i in range(114 * messageCounter):
            file.write(str(int(output[i]))) # writes the raw data in the output to the debug file
        

        file.write("\n\n")

        file.close()

    output_str = ""
    for i in range(block_size):
        output_str = output_str + str(int(output[i]))
    return output_str




# getMessages takes in an array of raw SDR samples and converts them into ADS-B messages following the format set out in the 
# interface control document. Essentially this is what our GNURadio code did. It's now been split up into a couple 
# smaller functions.
def getMessages(sample_block):

        
    ADSBBits = getADSBBits(sample_block)


    return ADSBBits




    
    





# This part is the main code that should control the entire program. Essentially we're replacing the GNURadio interface with 
# this Python code that reads data from a file (or an SDR, later on) and processes it.

infile = np.fromfile(input_file_loc, dtype=np.complex64) # Gets the data from the file as one huge array.

if(debug_info):
    print(len(infile))

#from decoding functions
counter_array = [0, 0, 0]
msg_array_true = ['']
ICAO_array = ['']

with open('output.txt', 'w') as f:
      f.write('')

with open('bits.txt', 'w') as f:
      f.write('')


startTime = time.time()

for i in range(0,len(infile),block_size):
    sample_block = infile[i:(i+block_size)] # The for loop breaks the file into manageable blocks which are then processed.

    magnitudes = getMagnitudes(sample_block)

    messageBits_array = getMessages(magnitudes) # Contains the message data as described in the ICD- decoding team, you guys process this data.
    
    messageBits = ''.join(str(messageBits_array))

    decode_from_demod(messageBits, counter_array, msg_array_true, ICAO_array)


endTime = time.time()
timeElapsed = endTime-startTime
if(debug_info):
    print(timeElapsed, "s taken, program is running at", len(infile) / timeElapsed / 2000000 * 100 , "% of necessary speed")