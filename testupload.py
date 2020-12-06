import pysftp
import os

command = "sudo nslookup aatuploadserver | tail -2 | head -1 | awk '{print $2}'"
result = os.popen(command)

ipaddress = list(result)
if ipaddress:
    print(ipaddress[0].strip())

myHostname = "192.168.10.188"
myUsername = "pi"
myPassword = "aatracking"

myfiles= os.listdir("./cameraProject/")
#print(list(myfiles))

if os.path.exists('./video_1601221500s.h264'):
    print("file exist")
else:
    print("file doesn not exist")

# for y in range(10):
#     for i in range(10):    
#         if(i == 5):
#             print("5 found breaking now")
#             break
#         print(i)
#cnopts = pysftp.CnOpts()
#cnopts.hostkeys = None
#with pysftp.Connection(host=myHostname,username=myUsername,password=myPassword,cnopts=cnopts) as sftp:
#
for _file in myfiles:
    print(_file)
#        if(".h264" in _file):
#            print(_file)
#            remoteFilepath = '../../media/pi/aatstorage/'+ _file
#            localFilepath = _file
            #sftp.put(localFilepath,remoteFilepath)
            #print("uploaded file -" + _file)                                
    
