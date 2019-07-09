from fog import Fog, FogException
import numpy as np

def main():
    fog = Fog('/dev/ttyS0')
    angles = np.array([])
    filter_value = 0.1
    while True:
        try:
            angle = fog.get_sample()
            if abs(fog.get_sample()) < filter_value:
                angle = 0
            angles = np.append(angles,angle)
        except KeyboardInterrupt:
            break
        abs_angle = np.trapz(angles,dx=2)
        print "abs angle: " + str(abs_angle)        

if __name__=='__main__' : main()