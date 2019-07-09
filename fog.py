#!/usr/bin/env python
# -*- coding: utf-8 -*


#TODO:
#
# compute checksum
# compute gyro rate and temp
# handle exceptions 

# DONE
#
# find the first message byte


import serial
import time 

class Fog():

    def __init__(self, port='/dev/ttyS0', baudrate=9600, stopbits=1, parity='N', timeout=10):
        self.device = serial.Serial(port,baudrate)
        self.timeout = timeout
        self.checksum = 0
    

    def get_sample(self):
        """Low-level message receiving"""
        while True: # add here timeout exception
            if bytearray(self.device.read())[0] & 0x80:
                print "Houston we got a message!"
                buffer = bytearray(self.device.read(7))
                break
        # compute checksum
                                      
                        
def main():
    fog = Fog('/dev/ttyS0')
    fog.get_sample()


if __name__ == '__main__':main()