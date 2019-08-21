#!/usr/bin/env python
# -*- coding: utf-8 -*

from fog import Fog
from fog import FogMessage as fm
from fog import FogException

"""
Example program to show how to use Fog and FogMessage Classes
"""

def main():
    fog = Fog('/dev/ttyS0') 

    while True: 
        try:
            """
            to get temperature readings we need to get 2 consecutive messages from Fog.
            """
            men1 = fm(fog.get_sample())
            print "First message Angle: " + str(men1.angle_rate)
            men2 = fm(fog.get_sample())
            print "Second message Angle: " + str(men2.angle_rate)
            temp = men1.get_temp(men2) # get_temp needs a adjacent message as argument, order doesn't matter
            print "Temperature: "+str(temp)+"C"
        except KeyboardInterrupt:
            break
        except FogException:
            print "an error ocurred with your sensor :("

if __name__=="__main__":main()