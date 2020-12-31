import os
import pysftp
from pathlib import Path


class Upload:
    def __init__(self, *args, **kwargs):
        self.myHostname = kwargs['myHostname']
        self.myUsername = kwargs['myUsername']
        self.myPassword = kwargs['myPassword']
        self.media_storage = kwargs['mediaStorageLocation']
        self.main_dict = {}
        self.home = str(Path.home())+"/cameraProject/"
        self.local_file_path = kwargs['local_file_path']
        #self.sftp = pysftp.Connection(host=myHostname, username=myUsername, password=myPassword)
        self.readFilesandUpload()

    def readFilesandUpload(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        print("**************************** hostkeys none")
        with pysftp.Connection(host=self.myHostname, username=self.myUsername, password=self.myPassword, cnopts=cnopts) as sftp:
            print("=========================> pysftp connection successfull")
            myfiles = os.listdir(self.home)
            for __file in myfiles:
                print(__file)
                if(".h264" in __file):
                    print(__file)
                    remoteFilepath = mediaStorageLocation + __file
                    localFilepath = self.home + __file
                    sftp.put(localFilepath, remoteFilepath,
                             self.uploadCallback)
                    os.remove(self.home+__file)
                    print("\nuploaded file -" + __file)
            print("file upload successfull")
            sftp.close()

    def uploadCallback(self, a, b):
        print("\r"+str(a/1000000) + "Mb uploaded of " +
              str(b/1000000)+"MB", end='', flush=True)

    def closeConnection(self):
        self.sftp.close()


if __name__ == "__main__":
    myHostname = "aatuploadserver.local"
    myUsername = "pi"
    myPassword = "aatracking"
    mediaStorageLocation = '../../media/pi/aatstorage/'
    local_file_path = './'
    U = Upload(myHostname=myHostname, myUsername=myUsername, myPassword=myPassword,
               mediaStorageLocation=mediaStorageLocation, local_file_path=local_file_path)
    U.readFilesandUpload()
