import numpy as np
from decode import decode_from_demod
import time

# Change these before running the code!
input_file_loc = r"C:/Users/emssm/Downloads/mode1s_GR.bin"
debug_info = False # Outputs some extra info to the terminal
debug_time = True  # Performs analysis of the program's operational speed
debug_file = False # Outputs the contents of the output to the next file
debug_file_loc = r"C:/Users/emssm/OneDrive/bits.txt" 


block_size = 15000 # the size of blocks of samples, currently 4096, may be increased if the program lags
tuning_factor = 3.5 # used for calibration. Increase if false messages are detected, decrease if real messages aren't detected.

# This function takes in a string of 224 samples where an ADS-B message is located, and extracts the message.
def ADSBbitsToMessage(raw_message):
    output = np.empty(112, dtype=int)
    for i in range(112):
        if raw_message[i*2] > raw_message[i*2+1]:
            output[i] = 1
        else:
            output[i] = 0
    return output


# Converts IQ samples to magnitudes, in integer form for faster math
def getMagnitudes(sample_block):
    return((np.abs(sample_block) * 1000000).astype(np.int64))


# This function takes in an array of 112-bit message vectors, converts them to strings, then passes each message
# along to the decoding section of the code
def processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info):
    if(debug_info):
        print(len(messages), "messages found in block.")
    for message in messages:
        messageBits = "".join(str(x) for x in message)
        if(debug_info):
            print("Message processed, output to demod is: ", messageBits)
        decode_from_demod(messageBits, counter_array, msg_array_true, ICAO_array)

# This function takes in the raw ADS-B bitstream (as a string) and returns the output as described in the ICD.
def getADSBBits(sample_block, debug_info):

    i = 0
    output = []

    messageCounter = 0 # tracks the number of valid messages found

    while(i < len(sample_block) - 240): # Using a while loop instead of for loop so i can be incremented inside the loop

        # The if statement is a way of checking for a preamble. To view the specifics of the preamble go here:
        # https://web.stanford.edu/class/ee26n/Assignments/Assignment4.html 
        # The if statement checks to see if all of the samples that should be pulses are larger than all of the samples that 
        # should be blank.
        # Preambles are 16 samples long- if one is correctly detected, samples 0, 2, 7, and 9 will be a spike, while the rest will be empty.

        if(sample_block[i] <= sample_block[i+1]): 
            # Very simple check for speed- if the first sample isn't a pulse, no need to process more
            i += 1
            continue

        spike = (sample_block[i] + sample_block[i+2] + sample_block[i+7] + sample_block[i+9]) / 4 / tuning_factor



        if(spike > sample_block[i+1] and spike > sample_block[i+1] and spike > sample_block[i+3] 
            and spike > sample_block[i+6] and spike > sample_block[i+8] 
            and spike > sample_block[i+8] and spike > sample_block[i+10]):
            message = ADSBbitsToMessage(sample_block[i+16:i+241]) # Should contain a valid message.
            output.append(message)

            i += 240 # skip over the entire message we just read, no need to check it again
            messageCounter += 1

        else:
            i += 1

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
def getMessages(sample_block, debug_info):

        
    ADSBBits = getADSBBits(sample_block, debug_info)


    return ADSBBits




    
    





# This part is the main code that should control the entire program. Essentially we're replacing the GNURadio interface with 
# this Python code that reads data from a file (or an SDR, later on) and processes it.

startTime = time.time()

infile = np.fromfile(input_file_loc, dtype=np.complex64) # Gets the data from the file as one huge array.

if(debug_info):
    print("Input file read, file is", len(infile), "samples long.")

#from decoding functions
counter_array = [0, 0, 0]
msg_array_true = ['']
ICAO_array = ['']

with open('output.txt', 'w') as f:
      f.write('')

with open('bits.txt', 'w') as f:
      f.write('')

for i in range(0,len(infile),block_size):
    sample_block = infile[i:(i+block_size)] # The for loop breaks the file into manageable blocks which are then processed.

    sample_block = np.abs(sample_block) 

    messages = getMessages(sample_block, debug_info) # Contains an array containing the messages, each as a 112-bit vector.

    processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info)


endTime = time.time()
timeElapsed = endTime-startTime
if(debug_time):
    print(timeElapsed, "s taken, program is running at", len(infile) / timeElapsed / 2000000 * 100 , "% of necessary speed")
