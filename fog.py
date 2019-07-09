#!/usr/bin/env python
# -*- coding: utf-8 -*


#TODO:
#
# compute gyro rate and temp
# handle exceptions 

# DONE
#
# find the first message byte
# compute checksum

import serial
import time 


class Fog():

    def __init__(self, port='/dev/ttyS0', baudrate=9600, stopbits=1, parity='N', timeout=10, verbose = True):
        self.device = serial.Serial(port,baudrate)
        self.timeout = timeout
        self.verbose = verbose

    def twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val           

    def get_sample(self):
        """Low-level message receiving"""
        while True: # add here timeout exception
            buff = bytearray(self.device.read())
            if buff[0] & 0x80:
                buffer = bytearray(self.device.read(7))
                if self.verbose:
                    print "buffer size:" + str(len(buffer)) 
                break
                
        # compute checksum
        received_checksum = (buff[0] & 0x7f) << 1
        received_checksum |= (buffer[0] >> 6) & 1

        if self.verbose:
            print "received checksum: " + str(received_checksum)

        checktemp = ((buffer[0] & 0x3f)<<2) | (buffer[1]>>5)
        checksum = checktemp
        # B7..B0
        checktemp = ((buffer[1] & 0x1f)<<3) | (buffer[2]>>4)
        checksum += checktemp
        # C7..C0
        checktemp = ((buffer[2] & 0xf)<<4) | (buffer[3]>>3)
        checksum += checktemp
        # T7..T0
        checktemp = ((buffer[3] & 7)<<5) | (buffer[4]>>2)
        checksum += checktemp
        # R15..R8
        checktemp = ((buffer[4] & 3)<<6) | (buffer[5]>>1)
        checksum += checktemp
        # R8..R0
        checktemp = ((buffer[5] & 1)<<7) | buffer[6]
        checksum += checktemp               
        checksum = ~checksum + 1
        # mask checksum to 16bits integer
        checksum = checksum & 0xff

        if self.verbose:
            print "computed checksum: " + str(checksum)

        # Built-In Test
        built_in_test = (buffer[2] >> 4) & 1
        print built_in_test #handle BIT error

        # calc temperature message 
        raw_temp = ((buffer[3] & 7) << 5)
        raw_temp |= (buffer[4] >> 2) & 0x1f

        #calc angle rate
    
        angle_rate = ((buffer[4] & 3) << 14) | ((buffer[5] & 0x7f) << 7) | (buffer[6] & 0x7f)
        angle_rate = angle_rate & 0xFFFFFFFF

        if angle_rate & 0x8000:
            angle_rate |= 0xFFFF0000
            
        else:
            angle_rate &= 0x0000FFFF      

        angle_rate = angle_rate & 0xFFFFFFFF
        angle_rate = self.twos_comp(angle_rate, 32)
        
        angle_rate = angle_rate * 0.000305 
        if self.verbose:
            print "angle: " + str(angle_rate)                       

        return angle_rate

def main():
    fog = Fog('/dev/ttyS0')
    while True:
        fog.get_sample()


if __name__ == '__main__':main()