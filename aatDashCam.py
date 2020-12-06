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


dataLogFile = 'dataLog.json'

lengthOfVideo = 60
frameRate = 30

myHostname = "192.168.10.188"
myUsername = "pi"
myPassword = "aatracking"

mediaStorageLocation = '../../media/pi/aatstorage/'

class AatDashCam:
    def __init__(self):
        print("this is init")
        #Inititalize GPS
        gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
        self.gpsd = gpsd
        #Fetch Intial Storage
        self.storageLeft = self.getStorageleft()
        
        #Initialize GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN)
        GPIO.setup(18,GPIO.OUT,initial = GPIO.HIGH) # HiGH for keeping the power ON
        GPIO.setup(24,GPIO.OUT,initial = GPIO.HIGH) # HIGH for LED to imdicate processing
        self.ignitionStatus = GPIO.input(17)
        self.ledON = True
        #Initialize camera
        self.camera = PiCamera()
        self.initDataLogFile()
        self.lengthOfVideo = 60 #in seconds
        print('Init Successfull')
        

    def intiCameraConfiguration(self):
        with open('/home/pi/cameraProject/cameraConfig.json') as json_file:
            print(json_file)
            config = json.load(json_file)
            
            self.camera.resolution = (config['resolution']['x'],config['resolution']['y'])
            self.lengthOfVideo = config['interval'] * 60
            frameRate = config['framerate']
            self.camera.framerate = frameRate

    def initDataLogFile(self):
        if os.path.exists(dataLogFile):
            pass
        else:
            data = {  
                'videoFiles': []
            }
            with open(dataLogFile, 'w') as outfile:  
                json.dump(data, outfile)

    def getStorageleft(self):
        path = '/'
        st = os.statvfs(path)
        # free blocks available * fragment size
        bytes_avail = (st.f_bavail * st.f_frsize)
        gigabytes = bytes_avail / 1024 / 1024 / 1024
        
        return gigabytes

    def getFilename(self):
        self.storageLeft = self.getStorageleft()
        timestamp = int(time.time())    
        fname =    'video_'+str(timestamp)+'.h264'
        
        a_file = open(dataLogFile, "r") # read dataLog File
        json_object = json.load(a_file)
        a_file.close()
        videoFiles = json_object['videoFiles']
        if self.storageLeft < 1:
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

    def getPositionData(self):
        try:
            nx = self.gpsd.next()    
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
                print(position)
            return position
        except BaseException  as e:
            print(str(e))
            subprocess.call('sudo systemctl stop gpsd.socket', shell=True)
            subprocess.call('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',shell=True)
            gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
            self.gpsd = gpsd
            print("re initilizing socket")
            return ""

    def run(self):
        try:
            #pos = self.getPositionData()
            #for i in range(100):
            #    print(str(pos))
            #    pos = self.getPositionData()
            #    time.sleep(1)
                
            if(self.ignitionStatus):
                while self.ignitionStatus:
                    self.ignitionStatus = GPIO.input(17) # Check for ignition            
                    print(str(self.ignitionStatus))
                    filename = self.getFilename()
                    self.camera.start_preview(alpha=200)
                    self.camera.start_recording(filename)
                    now = datetime.datetime.now()
                    self.camera.annotate_text = now.strftime('%Y-%m-%dT%H:%M:%S')
                    print(str(self.lengthOfVideo))
                    for i in range(self.lengthOfVideo):
                        position = self.getPositionData()
                        print(str(self.ignitionStatus))
                        now = datetime.datetime.now()
                        self.camera.annotate_text = now.strftime('%Y-%m-%dT%H:%M:%S') + " " + position
                        time.sleep(1)
                        self.ignitionStatus = GPIO.input(17) # Check for ignition  
                        if(self.ignitionStatus==False):
                            break
                        
                    self.camera.stop_preview()
                    self.camera.stop_recording()
                    print(str(self.ignitionStatus))

            isUploaded = self.startUploading()
            GPIO.output(18,GPIO.LOW)
        except Exception  as e:
            print(e)
        finally:
            print("clean up") 
            GPIO.cleanup()            
            #subprocess.call('sudo shutdown' , shell=True)

    def uploadCallback(self,a,b):
        print("\r"+str(b/1000000)+" MB " + " - " + str(a/1000000)+" MB" ,end='', flush=True)
        if self.ledON:
            GPIO.output(24,GPIO.LOW)
            self.ledON = False
        else:
            GPIO.output(24,GPIO.HIGH)
            self.ledON = True        

    def searchForavailableWIFI(self,server_name):
        process  = os.popen("sudo iw dev wlan0 scan | grep SSID")
        preprocessed = process.read()
        print(preprocessed)
        if(server_name in preprocessed):
            print(server_name +" wifi found")
            return False
        else:
            print(server_name + " Wifi not found")
            return True

    def startUploading(self):
        print("u have 5 seconds to turn on the ignition")
        time.sleep(5)

        interface_name = "wlan0" # i. e wlp2s0  
        server_name = "COMFAST_2G"
        password = "Martin123"
        checkwifi = self.searchForavailableWIFI(server_name)
        time.sleep(2)
        if checkwifi : 
            server_name = "COMFAST_5G"
            password = "Martin123"

        F = Finder(server_name=server_name,password=password,interface=interface_name)
        response = F.run()
        counter = 0
        while (response == False):
            counter += 1
            if(counter < 30):
                time.sleep(2)
                print('waiting for a second to try again')
                response = F.run()
            else:
                break
        if (response==True) :
            time.sleep(2)
            command = "sudo nslookup aatuploadserver | tail -2 | head -1 | awk '{print $2}'"
            result = os.popen(command)
            ipaddress = list(result)
            print(ipaddress)
            if ipaddress:
                #myHostname = str(ipaddress[0].strip())
                print(myHostname)
           
            
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            print("**************************** hostkeys none")
            with pysftp.Connection(host=myHostname,username=myUsername,password=myPassword,cnopts=cnopts) as sftp:
                print("=========================> pysftp connection successfull")
                myfiles= os.listdir("./home/pi/cameraProject/")
                for __file in myfiles:            
                    print(__file)
                    if(".h264" in __file):
                        print(__file)
                        remoteFilepath = mediaStorageLocation + __file
                        localFilepath = "./home/pi/cameraProject/"+ __file
                        sftp.put(localFilepath,remoteFilepath,self.uploadCallback)
                        os.remove("./home/pi/cameraProject/"+__file)
                        print("\nuploaded file -" + __file)
                print("file upload successfull")
                sftp.close()
                
            return True
        else:
            return False


if __name__ == "__main__":
    p1 = subprocess.Popen('sudo systemctl stop gpsd.socket' ,stdout=subprocess.PIPE, shell=True)
    p1.wait()
    p2 = subprocess.Popen('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',stdout=subprocess.PIPE,shell=True)
    p2.wait()

    aat = AatDashCam()
    aat.run()
