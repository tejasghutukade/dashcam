import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import datetime
import json
import os
import serial
from gps import *
import subprocess
import pysftp
from wifiConnect import Finder

subprocess.call('sudo systemctl stop gpsd.socket' , shell=True)
subprocess.call('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',shell=True)

dataLogFile = 'dataLog.json'

lengthOfVideo = 60
frameRate = 30

myHostname = "10.130.247.140"
myUsername = "pi"
myPassword = "aatracking"

mediaStorageLocation = '../../media/pi/aatstorage/'


def uploadCallback(a,b):
    print("\r"+str(a/1000000) + "Mb uploaded of " + str(b/1000000)+"MB",end='', flush=True)

def uploadFiles():
    print("u have 5 seconds to turn on the ignition")
    time.sleep(5)
    server_name = "OakOne"
    password = "ganesha2301"
    interface_name = "wlan0" # i. e wlp2s0  
    F = Finder(server_name=server_name,password=password,interface=interface_name)
    counter = 0
    response = F.run()
    while (response == False):
        counter += 1
        if(counter < 60):
            time.sleep(2)
            print('waiting for a second to try again')
            response = F.run()
        else:
            break

    if (response==True) : 
        print("Starting Upload")
        a_file = open(dataLogFile, "r") # read dataLog File
        json_object = json.load(a_file)
        a_file.close()
        videoFiles = json_object['videoFiles']
        _videoFiles = videoFiles
        
        with pysftp.Connection(host=myHostname,username=myUsername,password=myPassword) as sftp:
            cnt = 0
            for _file in videoFiles:
                if os.path.exists(_file):
                    print("starting upload -" + _file)
                    remoteFilepath = mediaStorageLocation + _file
                    localFilepath = _file
                    #del _videoFiles[cnt]
                    sftp.put(localFilepath,remoteFilepath,uploadCallback)
                    os.remove(_file)
                    print("Uploaded File " + _file)

            myfiles= os.listdir("./")
            print(myfiles)
            for __file in myfiles:            
                if(".h264" in __file):
                    print(__file)
                    remoteFilepath = mediaStorageLocation + __file
                    localFilepath = __file
                    sftp.put(localFilepath,remoteFilepath)
                    print("uploaded file -" + _file)      

        sftp.close()
        json_object['videoFiles'] = _videoFiles
        a_file = open(dataLogFile, "w")
        json.dump(json_object, a_file,indent = 4)
        a_file.close() 
        return True
    else :
        return False


def getPositionData(gps):
    nx = gpsd.next()    
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
    storageLeft = getStorageleft()
    timestamp = int(time.time())    
    fname =    'video_'+str(timestamp)+'.h264'
    
    a_file = open(dataLogFile, "r") # read dataLog File
    json_object = json.load(a_file)
    a_file.close()
    videoFiles = json_object['videoFiles']
    if storageLeft < 1:
        if os.path.exists(videoFiles[0]):
            os.remove(videoFiles[0])
        
        del videoFiles[0]
        #delete file
    videoFiles.append(fname)
    
    json_object['videoFiles'] = videoFiles
    a_file = open(dataLogFile, "w")
    json.dump(json_object, a_file,indent = 4)
    a_file.close() 
    filename = '/home/pi/cameraProject/'+fname
    
    return filename

if os.path.exists(dataLogFile):
    pass
else:

    data = {  
        'videoFiles': []
    }
    with open(dataLogFile, 'w') as outfile:  
        json.dump(data, outfile)


gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

storageLeft = getStorageleft()

shouldStart = True
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN)
GPIO.setup(18,GPIO.OUT,initial = GPIO.HIGH)
GPIO.setup(24,GPIO.OUT,initial = GPIO.HIGH)
print("GPIO 18 set to high")

try:
    ignition = GPIO.input(17)    
    print("Ignition - " + str(ignition))

    if (shouldStart):
        camera = PiCamera()
        path = '/'
        st = os.statvfs(path)

        with open('/home/pi/cameraProject/cameraConfig.json') as json_file:
            config = json.load(json_file)
            camera.resolution = (config['resolution']['x'],config['resolution']['y'])
            lengthOfVideo = config['interval'] * 60
            frameRate = config['framerate']

        # camera.resolution = (800,600)
        now = datetime.datetime.now()
        camera.annotate_text = now.strftime('%Y-%m-%dT%H:%M:%S')
        
        camera.framerate = frameRate
        count = 0
        while ignition: #While Ignition Is on
            
            ignition = GPIO.input(17) # Check for ignition 

            timestamp = int(time.time())    
            filename = getFilename()
            print('Starting - ' + filename)
            camera.start_preview(alpha=200)
            camera.start_recording(filename)

            for i in range(lengthOfVideo):
                position = getPositionData(gpsd)
                now = datetime.datetime.now()
                camera.annotate_text = now.strftime('%Y-%m-%dT%H:%M:%S') + " " + position
                time.sleep(1)
                ignition = GPIO.input(17) # Check for ignition 
                if(ignition==False):
                    break
                
            camera.stop_preview()
            camera.stop_recording()
            print('Finished - ' + filename)
            st = os.statvfs(path)

        #Handle Upload
        isUpolad = uploadFiles()        
        GPIO.output(18,GPIO.LOW)

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
   print("Keyboard interrupt")
   GPIO.cleanup() 

except Exception  as e:
   print(e) 

finally:
   print("clean up") 
   GPIO.cleanup()

