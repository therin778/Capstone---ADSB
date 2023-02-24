import numpy as np
import time
import rtlsdr
import folium
from decode import decode_from_demod



 
# Change these before running the code!
<<<<<<< HEAD
from Demod_prototype_thresholding import getMessages # change this to which program you want to test
input_file_loc = r"C:/Users/MyPC/Desktop/Capstone---ADSB/Data Files/mode1s_GR.bin"
debug_info = True # Outputs some extra info to the terminal
debug_time = True  # Performs analysis of the program's operational speed
=======
from Demod_prototype_loop_checking import getMessages # change this to which program you want to test
run_from_file = True # If true run from file, if false run from SDR
input_file_loc = r"/Users/kategothberg/Capstone---ADSB/mode1s_GR.bin"
debug_info = False # Outputs some extra info to the terminal
debug_time = False  # Performs analysis of the program's operational speed
>>>>>>> 83db86b607a171ae17c904f17d781af20bc502ff
debug_file = False # Outputs the contents of the output to the next file
debug_file_loc = r"/Users/kategothberg/Capstone---ADSB/bits.txt"  

test_lat = 43.08488748841366 
test_long = 15.163225446428571

ohio_lat = 39.3292
ohio_long = -82.1013

map = folium.Map(location=[test_lat, test_long]) 
map.save("disp_map.html")


block_size = 4096 # the size of blocks of samples, currently 4096, may be increased if the program lags
tuning_factor = 1.5 # used for calibration. Increase if false messages are detected, decrease if real messages aren't detected.
# Note that this does different things with the different programs, but serves a similar purpose on both.

delta_tuning = 0.5 # Used for calibration. Setting it too low will lead to false messages, setting it too high can miss real messages.
# Only used on the loop checking style program.



# This function takes in an array of 112-bit message vectors, converts them to strings, then passes each message
# along to the decoding section of the code
def processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, map):

    if(debug_info):
        print(len(messages), "messages found in block.")

    for message in messages:
        messageBits = "".join(str(x) for x in message)

        if(debug_info):
            print("Message processed, output to demod is: ", messageBits)

        decode_from_demod(messageBits, counter_array, msg_array_true, ICAO_array, debug_info, map)

        map.save("disp_map.html")






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

    with open('output.txt', 'w') as f:
        f.write('')

    with open(debug_file_loc, 'w') as f:
        f.write('')



    # The process must be done once to initialize the stored block of samples before the loop begins.

    stored_block = np.empty(239) # Used to store the end of the block, so it can be added to the next block, in case a message is split between two blocks of data 

    sample_block = infile[0:block_size]

    stored_block = sample_block[block_size-239:]

    messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

    processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, map)



    for i in range(block_size,len(infile),block_size-239):
        sample_block = np.append(stored_block, infile[i:(i+block_size-239)]) # The for loop breaks the file into manageable blocks which are then processed.

        stored_block = sample_block[block_size-239:]

        sample_block = np.abs(sample_block) 

        messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

        processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, map)






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

    with open('output.txt', 'w') as f:
        f.write('')

    with open(debug_file_loc, 'w') as f:
        f.write('')



    # The process must be done once to initialize the stored block of samples before the loop begins.

    stored_block = np.empty(239) # Used to store the end of the block, so it can be added to the next block, in case a message is split between two blocks of data 

    sample_block = sdr.read_samples(block_size)

    stored_block = sample_block[block_size-239:]

    messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

    processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, map)



    while(True):
        sample_block = np.append(stored_block, sdr.read_samples(block_size-239)) # The for loop breaks the file into manageable blocks which are then processed.

        stored_block = sample_block[block_size-239:]

        sample_block = np.abs(sample_block) 

        messages = getMessages(sample_block, tuning_factor, delta_tuning, debug_info, debug_file, debug_file_loc) # Contains an array containing the messages, each as a 112-bit vector.

        processMessages(messages, counter_array, msg_array_true, ICAO_array, debug_info, map)






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
