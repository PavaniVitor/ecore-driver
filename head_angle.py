from fog import Fog, FogException
import numpy as np
import keyboard

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
            # press z to clear angles list
            if keyboard.is_pressed('z'):
                angles = np.array([])
        except KeyboardInterrupt:
            break
        except FogException:
            print "Houston, we've had a problem."
            
        
        head_angle = np.trapz(angles,dx=2)
        print "heading angle: " + str(head_angle)        
            
if __name__=='__main__' : main()
