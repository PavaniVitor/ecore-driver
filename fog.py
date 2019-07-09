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

    def __init__(self, port='/dev/ttyS0', baudrate=9600, stopbits=1, parity='N', timeout=10):
        self.device = serial.Serial(port,baudrate)
        self.timeout = timeout

    

    def get_sample(self):
        """Low-level message receiving"""
        while True: # add here timeout exception
            buff = bytearray(self.device.read())
            if buff[0] & 0x80:
                print "Houston we got a message!"
                buffer = bytearray(self.device.read(7))
                print len(buffer) 
                break
        # compute checksum
        received_checksum = (buff[0] & 0x7f) << 1
        received_checksum |= (buffer[0] >> 6) & 1
        print received_checksum
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
        print checksum

        # Built-In Test
        built_in_test = (buffer[2] >> 4) & 1
        print built_in_test #handle BIT error

        # calc temperature message 
        raw_temp = ((buffer[3] & 7) << 5)
        raw_temp |= (buffer[4] >> 2) & 0x1f

                
                                           
def main():
    fog = Fog('/dev/ttyS0')
    for i in range(10):
        fog.get_sample()


if __name__ == '__main__':main()