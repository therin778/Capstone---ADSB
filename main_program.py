import numpy as np
import time
#import rtlsdr
import folium
from decode import decode_from_demod, plane_class
from mapping import mapping



 
# Change these before running the code!
from Demod_prototype_loop_checking import getMessages # change this to which program you want to test
run_from_file = True # If true run from file, if false run from SDR
input_file_loc = r"./samples_short.bin"
debug_info = False # Outputs some extra info to the terminal
debug_time = True  # Performs analysis of the program's operational speed
debug_file = False # Outputs the contents of the output to the next file
debug_file_loc = r"./bits.txt"

  



block_size = 4096 # the size of blocks of samples, currently 4096, may be increased if the program lags
tuning_factor = 2.5 # used for calibration. Increase if false messages are detected, decrease if real messages aren't detected.
# Note that this does different things with the different programs, but serves a similar purpose on both.

delta_tuning = 0.6 # Used for calibration. Setting it too low will lead to false messages, setting it too high can miss real messages.
# Only used on the loop checking style program.



# This function takes in an array of 112-bit message vectors, converts them to strings, then passes each message
# along to the decoding section of the code
def processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, aircraft):

    if(debug_info):
        print(len(messages), "messages found in block.")

    for message in messages:
        messageBits = "".join(str(x) for x in message)

        if(debug_info):
            print("Message processed, output to demod is: ", messageBits)

        decode_from_demod(messageBits, counter_array, msg_array_true, ICAO_array, debug_info, aircraft)


    #map.save("disp_map.html")






# Main_file and main_sdr are the main code that controls the entire program. Samples are extracted from either a file or an SDR and sent 
# for processing to other functions.
def main_file():
    startTime = time.time()

    infile = np.fromfile(input_file_loc, dtype=np.complex64) # Gets the data from the file as one huge array.

    if(debug_info):
        print("Input file read, file is", len(infile), "samples long.")


    # These three arrays are used internally by the decoding functions to store data.
    counter_array = [0, 0, 0]
    msg_array_true = ['']
    ICAO_array = ['']
    aircraft = []

    with open('output.txt', 'w') as f:
        f.write('')

    with open(debug_file_loc, 'w') as f:
        f.write('')



    # The process must be done once to initialize the stored block of samples before the loop begins.

    stored_block = np.empty(239) # Used to store the end of the block, so it can be added to the next block, in case a message is split between two blocks of data 

    sample_block = infile[0:block_size]

    stored_block = sample_block[block_size-239:]

    messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

    processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, aircraft)



    for i in range(block_size,len(infile),block_size-239):
        sample_block = np.append(stored_block, infile[i:(i+block_size-239)]) # The for loop breaks the file into manageable blocks which are then processed.

        stored_block = sample_block[block_size-239:]

        sample_block = np.abs(sample_block) 

        messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

        processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, aircraft)

    
    print("All aircraft received:")
    for plane in aircraft:
        print("\nID:", hex(int(plane.ID,2)))
        print("Tail number: ", plane.tail)
        print("All past latitudes:",  plane.lat)
        print("All past longitudes:", plane.long)
        print("All past altitudes:", plane.alt) 
        print("All past headings:", plane.heading)
        print("All past velocities:", plane.vel)



    mapping(aircraft)
    endTime = time.time()
    timeElapsed = endTime-startTime
    if(debug_time):
        print(timeElapsed, "s taken, program is running at", len(infile) / timeElapsed / 2000000 * 100 , "% of necessary speed")


# The other main function, this one gets samples from an SDR.
def main_sdr(sdr):
    startTime = time.time()


    print("SDR successfully acquired.")


    # These three arrays are used internally by the decoding functions to store data.
    counter_array = [0, 0, 0]
    msg_array_true = ['']
    ICAO_array = ['']
    aircraft = []

    with open('output.txt', 'w') as f:
        f.write('')

    with open(debug_file_loc, 'w') as f:
        f.write('')



    # The process must be done once to initialize the stored block of samples before the loop begins.

    stored_block = np.empty(239) # Used to store the end of the block, so it can be added to the next block, in case a message is split between two blocks of data 

    sample_block = sdr.read_samples(block_size)

    stored_block = sample_block[block_size-239:]

    messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

    processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, aircraft)



    while(True):
        sample_block = np.append(stored_block, sdr.read_samples(block_size-239)) # The for loop breaks the file into manageable blocks which are then processed.

        stored_block = sample_block[block_size-239:]

        sample_block = np.abs(sample_block) 

        messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

        processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, aircraft)






    endTime = time.time()
    timeElapsed = endTime-startTime
    if(debug_time):
        print(timeElapsed, "s taken, program is running at", len(infile) / timeElapsed / 2000000 * 100 , "% of necessary speed")    


if __name__ == "__main__":
    if run_from_file:
        main_file()
    else:
        sdr = rtlsdr.RtlSdr()

        # configure device
        sdr.sample_rate = 2e6  # Hz
        sdr.center_freq = 1090e6     # Hz
        sdr.freq_correction = 60   # PPM
        sdr.gain = 'auto'

        main_sdr(sdr)
