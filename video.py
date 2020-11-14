from picamera import PiCamera
import os
import time
import json


dataLogFile = 'dataLog.json'
configFile = '/home/pi/cameraProject/cameraConfig.json'
lengthOfVideo = 60
frameRate = 30

class RecordVideo:
    def __init__(self, *args, **kwargs):
        self.dataLogFile = kwargs['dataLogFile']
        self.configFile = kwargs['configFile']
        self.camera = PiCamera()
        self.lengthOfVideo = 180
        self.camera.framerate = 30
        self.camera.resolution = (800,600)
        self.camera.annotate_text = kwargs['annotate_text']
        if os.path.exists(dataLogFile):
            pass
        else:
            data = {  
                'videoFiles': []
            }
            with open(self.dataLogFile, 'w') as outfile:  
                json.dump(data, outfile)

        with open(self.configFile) as json_file:
            config = json.load(json_file)
            self.camera.resolution = (config['resolution']['x'],config['resolution']['y'])
            self.lengthOfVideo = config['interval'] * 60
            self.camera.frameRate = config['framerate']


    def getStorageleft(self):
        path = '/'
        st = os.statvfs(path)
        # free blocks available * fragment size
        bytes_avail = (st.f_bavail * st.f_frsize)
        gigabytes = bytes_avail / 1024 / 1024 / 1024
        
        return gigabytes

    def getFilename(self):
        storageLeft = self.getStorageleft()
        timestamp = int(time.time())    
        fname =    'video_'+str(timestamp)+'.h264'
        
        a_file = open(self.dataLogFile, "r") # read dataLog File
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

    def startVideo(self,annotate_text):
        self.camera.start_preview(alpha=200)
        filename = self.getFilename()
        self.camera.start_recording(filename)