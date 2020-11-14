import os
import pysftp

class Upload:
    def __init__(self, *args, **kwargs):
        self.myHostname = kwargs['myHostname']
        self.myUsername = kwargs['myUsername']
        self.myPassword = kwargs['myPassword']
        self.media_storage = kwargs['mediaStorageLocation']
        self.main_dict = {}
        self.local_file_path = kwargs['local_file_path']
        self.sftp = pysftp.Connection(host=myHostname,username=myUsername,password=myPassword)            

    def readFilesandUpload(self):
        myfiles= os.listdir(self.local_file_path)
        if len(myfiles) > 0:
            for __file in myfiles:
                if(".h264" in __file):
                    remoteFilepath = self.media_storage + __file
                    localFilepath = __file
                    self.uploadFiles(localFilepath,remoteFilepath)

    def uploadCallback(self,a,b):
        print("\r"+str(a/1000000) + "Mb uploaded of " + str(b/1000000)+"MB",end='', flush=True)

    def uploadFiles(self,localFilepath,remoteFilepath):
        print(localFilepath)
        self.sftp.put(localFilepath,remoteFilepath,self.uploadCallback)
        os.remove(localFilepath)

    def closeConnection(self):
        self.sftp.close()


if __name__ == "__main__":
    myHostname = "10.130.247.140"
    myUsername = "pi"
    myPassword = "aatracking"
    mediaStorageLocation = '../../media/pi/aatstorage/'
    local_file_path = './'
    U = Upload(myHostname=myHostname,myUsername=myUsername,myPassword=myPassword,mediaStorageLocation=mediaStorageLocation,local_file_path=local_file_path)
    U.readFilesandUpload()