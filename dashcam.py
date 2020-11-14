import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import datetime
import json
import os
import serial
from gps import *
import subprocess


subprocess.call('sudo systemctl stop gpsd.socket' , shell=True)
subprocess.call('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',shell=True)

dataLogFile = '/home/pi/cameraProject/dataLog.json'

def where_json(file_name):
    return os.path.exists(file_name)


if where_json(dataLogFile):
    pass

else:

    data = {  
        'videoFiles': {}
    }
    with open(dataLogFile, 'w') as outfile:  
        json.dump(data, outfile)


# constants
interval = 3
resolutionx=640
resolutiony=720
framerate = 30
#intialize
camera = PiCamera()
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
GPIO.setmode(GPIO.BCM)


# get settings
with open('/home/pi/cameraProject/cameraConfig.json') as json_file:
        config = json.load(json_file)
        resolutionx = config['resolution']['x']
        resolutiony = config['resolution']['y']
        interval = config['interval']
        interval = interval * 60
        framerate = config['framerate']
        
# init gpio pins
GPIO.setup(17, GPIO.IN) # Ignition Status

GPIO.setup(18,GPIO.OUT,initial = GPIO.HIGH) #Power continuation Output High=KeepON, Low=SHutDown

#PIO.setup(24,GPIO.OUT,initial = GPIO.HIGH)
#GPIO.cleanup()



#inti camera
camera.resolution = (resolutionx,resolutiony)
camera.framerate = framerate
print("interval - " + str(interval))


#functions
def getPositionData(gps):
    nx = gpsd.next()
    print(nx)
    position = ""
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        speed = getattr(nx,'speed',"Unknown")
        time = getattr(nx,'time',"Unknown")
        alt = getattr(nx,'alt',"Unknown")
        position = "Your position: lon = " + str(longitude) + ", lat = " + str(latitude)+", speed ="+ str(speed) + ", time = " + str(time) + ", alt = " + str(alt)
    
    return position


def getStorageleft():
    path = '/'
    st = os.statvfs(path)
    # free blocks available * fragment size
    bytes_avail = (st.f_bavail * st.f_frsize)
    gigabytes = bytes_avail / 1024 / 1024 / 1024
    
    return gigabytes


def getFilename():
    timestamp = int(time.time())    
    filename = '/home/pi/cameraProject/video_'+str(timestamp)+'.h264'
    
    return filename


def getAnnotationText():
    position = getPositionData(gpsd)
    print(position)
    
    return position

def connectToWIFI():
    output = subprocess.check_output('sudo iwgetid',shell=True)
    isConnected = "OakOne" in str(output)
    if(isConnected == False):
        newoutput = subprocess.check_output('sudo iwlist wlan0 scan|grep SSID',shell=True)    
    
    if("OakOne 5G" in str(newoutput)):
        newnewoutput = subprocess.check_output('sudo iwconfig wlan0 essid OakOne key ganesha2301',shell=True)

# Logic
try : 
    #ignition = GPIO.input(17)
    ignition = False
    while ignition :
                
        #camera.start_preview(alpha=200)
        fname = getFilename()
        camera.start_recording(fname)

        for i in range(interval):
            #ignition = GPIO.input(17)
            ignition = True
            annot = getAnnotationText()
            camera.annotate_text = annot
            print("Ignition - " + str(ignition))
            time.sleep(1)
            if(not ignition):
                camera.stop_recording()
                break
                        
        camera.stop_recording()
    #camera.stop_preview()        
    print('Done Processing')
    #GPIO.output(24,GPIO.LOW) 
    #GPIO.output(18,GPIO.LOW)        
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
   print("Keyboard interrupt")
   #GPIO.cleanup()
   
except Exception  as e:
   print(e)
   #GPIO.cleanup()

finally:
   print("clean up") 
   GPIO.cleanup()

