#!/usr/bin/env python
# -*- coding: utf-8 -*

import serial
import time 

class FogException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val           

class Fog():

    def __init__(self, port='/dev/ttyS0', baudrate=9600, stopbits=1, parity='N', timeout=10,verbose=False):

        self.device = serial.Serial(port, baudrate, timeout=timeout)
        self.timeout = timeout
        self.verbose = verbose

    def get_sample(self):
        """Low-level message receiving"""
    
        start = time.time()
        while (time.time()-start) < self.timeout: # add here timeout exception
            buff = bytearray(self.device.read())
            if len(buff) == 0:
                raise FogException('Unable to read sample from fog!')
            if buff[0] & 0x80:
                buffer = bytearray(self.device.read(7))
                if self.verbose:
                    print "buffer size:" + str(len(buffer)) 
                break
        
        # compute checksum
        received_checksum = (buff[0] & 0x7F) << 1
        received_checksum |= (buffer[0] >> 6) & 1

        if self.verbose:
            print "received checksum: " + str(received_checksum)

        checktemp = ((buffer[0] & 0x3F)<<2) | (buffer[1]>>5)
        checksum = checktemp
        # B7..B0
        checktemp = ((buffer[1] & 0x1F)<<3) | (buffer[2]>>4)
        checksum += checktemp
        # C7..C0
        checktemp = ((buffer[2] & 0xF)<<4) | (buffer[3]>>3)
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
        checksum = checksum & 0xFF

        if checksum != received_checksum:
            raise FogException('Error when validating checksum.')
        if self.verbose:
            print "computed checksum: " + str(checksum)

        # Built-In Test
        built_in_test = (buffer[2] >> 4) & 1
        if self.verbose:
            print "built in test bit: "+ str(built_in_test) #handle BIT error
        if not built_in_test:
            raise FogException('Built in test failed.')

        # calc temperature message 
        raw_temp = ((buffer[3] & 7) << 5)
        raw_temp |= (buffer[4] >> 2) & 0x1F
        if self.verbose:
            print "raw temperature: " + str(raw_temp)

        #calc angle rate
        angle_rate = ((buffer[4] & 3) << 14) | ((buffer[5] & 0x7f) << 7) | (buffer[6] & 0x7f)
        angle_rate = angle_rate & 0xFFFFFFFF

        #sign extension
        if angle_rate & 0x8000:
            angle_rate |= 0xFFFF0000
        else:
            angle_rate &= 0x0000FFFF      

        angle_rate = angle_rate & 0xFFFFFFFF
        angle_rate = twos_comp(angle_rate, 32)
        angle_rate = angle_rate * 0.000305 

        if self.verbose:
            print "angle: " + str(angle_rate)                       

        return checksum, received_checksum, built_in_test, raw_temp, angle_rate

    def get_angle(self):
        """wrapper to retrieve angle reading"""
        return self.get_sample()[4]
        
class FogMessage():
    """class to handle Fog messages"""
    def __init__(self, sample):
        self.checksum = sample[0]
        self.received_checksum = sample[1]
        self.built_in_test = sample[2]
        self.raw_temp = sample[3]
        self.angle_rate = sample[4]

    def get_temp(self,another_sample):
        """method to retrieve temperature readings from two samples"""
        if self.raw_temp & 0x80 and not another_sample.raw_temp & 0x80:
            msg1 = self
            msg2 = another_sample
        elif not self.raw_temp & 0x80 and another_sample & 0x80: 
            msg1 = another_sample
            msg2 = self
        else:
            pass 
            #error
        temp = msg1.raw_temp & 0x7f
        temp |= (msg2.raw_temp & 0x1f) << 7

        #sign extension
        if temp & 0x800:
            temp |= 0xF000
        else:
            temp &= 0x0FFF
        temp = twos_comp(temp, 16)
        temp = temp * 0.05
        return temp
                
    def __str__(self):
        return "Checksum: " + str(self.checksum) + "\nReceived Checksum: " + str(self.received_checksum)\
        +"\nBuilt in test: " + str(self.built_in_test)+"\nRaw temperature: " + str(self.raw_temp)\
        +"\nAngle Rate: " + str(self.angle_rate)    


def main():
    fog = Fog('/dev/ttyS0',verbose=True)
    while True:
        message = FogMessage(fog.get_sample())
        print message
        

if __name__ == '__main__' : main()