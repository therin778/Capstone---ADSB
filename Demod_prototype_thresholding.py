import numpy as np
import math
from decode import decode_from_demod

# Change these before running the code!
input_file_loc = r"C:/Users/emssm/Downloads/mode1S_GR.bin"
debug_info = True # Outputs some extra info to the terminal
debug_file = False # Outputs the contents of the output to the next file
debug_file_loc = r"C:/Users/emssm/OneDrive/bits.txt" 


block_size = 4096 # the size of blocks of samples, currently 4096, may be increased if the program lags
tuning_factor = 2.5 # used for calibration. Increase if false messages are detected, decrease if real messages aren't detected.




# This function converts the raw SDR samples into the unprocessed SDR bitstream which then needs to be processed.
# Returns them as a string.
def getRawBits(sample_block, debug_info):
    noise_floor = sum(sample_block[0::10]) / math.floor(block_size/10) * tuning_factor # Averages every 10th sample (for speed) to find the noise floor
    if(debug_info):
        print("The threshold is:", noise_floor)
    in0 = np.abs(sample_block)
    in0 = np.where(in0 > noise_floor, 1, 0)

    

    in0_str = ""
    

    for i in range(len(in0)):
        in0_str += (str(int(in0[i])))  # converts input into a single long string of bits
    
    return in0_str


def processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info):
    if(debug_info):
        print(len(messages), "messages found in block.")
    for message in messages:
        messageBits = "".join(str(x) for x in message)
        if(debug_info):
            print("Message processed, output to demod is: ", messageBits)
        decode_from_demod(messageBits, counter_array, msg_array_true, ICAO_array)
        




# This function takes in the raw ADS-B bitstream (as a string) and returns the output as described in the ICD.
def getADSBBits(rawBits, debug_info):
    if(debug_info):
        print("Processing new block of", len(rawBits), "bits:")

    message_loc = rawBits.find("1010000101000000") # searches for the first preamble it can find
    
    
    # This block will only execute if a preamble is found, and if the entire message is located within the data packet that GNURadio sent the block.
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
def getMessages(sample_block, debug_info):
    
    rawBitStream = getRawBits(sample_block, debug_info)
    ADSBBits = getADSBBits(rawBitStream, debug_info)
    return ADSBBits




    
    





# This part is the main code that should control the entire program. Essentially we're replacing the GNURadio interface with 
# this Python code that reads data from a file (or an SDR, later on) and processes it.

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


