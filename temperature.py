from fog import Fog
from fog import FogMessage as fm
from fog import FogException

def main():
    fog = Fog('/dev/ttyS0')

    while True: 
        try:
            men1 = fm(fog.get_sample())
            men2 = fm(fog.get_sample())
            temp = men1.get_temp(men2)
            print "Temperature: "+str(temp)+"C"
        except KeyboardInterrupt:
            break
        except FogException:
            print "an error ocurred with your sensor :("

if __name__=="__main__":main()