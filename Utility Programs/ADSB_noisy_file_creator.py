import numpy as np
import random

message_1 = "1000110101001101001000000010001110011001000100001000110010101011001010000111000000010100101010111011010100111100"
message_2 = "1000110101001101001000000010001110011001000100001000110110101011010010000111000000010100011001110011101110001001"

for noise in range(11):
    noise = noise / 10
    filename = "./noise_"+str(noise)+".bin"

    output = np.zeros(4096, dtype=np.complex64)

    i = 500 # first message will be at 500

    preamble = "1010000101000000"

    for bit in preamble:
        output[i] = int(bit)
        i = i+1

    for bit in message_1:
        if bit == "0":
            output[i] = 0
            output[i+1] = 1
        if bit == "1":
            output[i] = 1
            output[i+1] = 0
        print(output[i])
        i = i+2


    i = 2000 # second message will be at 2000

    for bit in preamble:
        output[i] = int(bit)
        i = i+1

    for bit in message_2:
        if bit == "0":
            output[i] = 0
            output[i+1] = 1
        if bit == "1":
            output[i] = 1
            output[i+1] = 0
        
        i = i+2

    for i in range(len(output)):
        output [i] += random.random() * noise


    print(type(output), output, output[516:526])

    output.tofile(filename)