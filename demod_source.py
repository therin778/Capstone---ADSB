"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.decim_block):  # other base classes are basic_block, decim_block, interp_block
    "Takes in raw samples containing ADS-B data and outputs them"

    def __init__(self, file_loc = "", vector_size = 4096, debug = 0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.decim_block.__init__(
            self,
            name='ADS-B Demodulation',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[(np.float32,4096)],
            decim = vector_size
        )
        self.set_relative_rate(1.0/vector_size)
        self.decimation = vector_size
        
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.file_loc = file_loc
        self.debug = debug

    def work(self, input_items, output_items):
        threshold = 0.29
        in0 = np.array(input_items[0][:])
        in0 = np.abs(in0)
        in0 = np.where(in0 > threshold, 1, 0) # this thresholding solution will need to be replaced later
        

        in0_str = ""
        

        for i in range(len(in0)):
            in0_str += (str(int(in0[i])))  # converts input into a single long string of bits

        message_loc = in0_str.find("1010000101000000") # searches for the first preamble it can find
        
        
        # This block will only execute if a preamble is found, and if the entire message is located within the data packet that GNURadio sent the block.
        # This results in a portion of messages being missed altogether. This will need to be improved for our final project.


        output = np.empty(4096)
        output.fill(-1)

        if(message_loc != -1) & (message_loc + 240 < len(in0_str)): 
            message_start = message_loc + 16  # this is where the actual ADS-B data starts
            message = np.empty(112)

            for i in range (112):             # ADS-B messages are 112 bits long

                twoBits = in0_str[message_start + i*2] +  in0_str[message_start + i*2 + 1]
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
                    message[i] = 0
                # "01" and "10" represent valid message data, the rest are error states. Error handling of some sort will need to be added here.

            output[0] = 1
            output[1:113] = message
            output[114] = 2

        
        else:
            output[0] = 0
        
        output_items[0][0] = output

        

        if(self.debug):
            print(len(in0), message_loc)   # prints some data that may be useful, more debugging can be added if needed
            file = open(self.file_loc, "a")

            np.set_printoptions(threshold=np.inf, linewidth = 512) 
            file.write(np.array2string(output_items[0][0], None)) # writes the raw data in the output to the debug file
            file.write("\n\n")

            file.close()

        
     

        


        return len(output_items[0])
