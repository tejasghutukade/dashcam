import subprocess

import time

#ifdown = subprocess.check_output('sudo ifconfig wlan0 down')

#time.sleep(30)

#ifup =subprocess.check_output('sudo ifconfig wlan0 up')

try:
    output = subprocess.check_output('sudo iwgetid',stderr=subprocess.STDOUT,shell=True)
    print(output)
    
except Exception  as e:
   print(e)
   output = ""
    

#print("OakOne" in str(output))

isConnected = "OakOne" in str(output)

print("is connected " + str(isConnected))

if(isConnected == False):
    newoutput = subprocess.check_output('sudo iwlist wlan0 scan|grep SSID',shell=True)
    print(newoutput)
    if("OakOne" in str(newoutput)):
        newnewoutput = subprocess.check_output('sudo iwconfig wlan0 essid OakOne key ganesha2301',shell=True)
        print(newnewoutput)


