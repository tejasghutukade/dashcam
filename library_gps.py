from gps import *
import time
import subprocess

subprocess.call('sudo systemctl stop gpsd.socket' , shell=True)
subprocess.call('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',shell=True)

running = True

def getPositionData():
    nx = gpsd.next()
    # print(nx)
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "Unknown")
        longitude = getattr(nx,'lon', "Unknown")
        speed = getattr(nx,'speed',"Unknown")
        time = getattr(nx,'time',"Unknown")
        alt = getattr(nx,'alt',"Unknown")
        print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude)+", speed ="+ str(speed) + ", time = " + str(time) + ", alt = " + str(alt))

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

try:
    print("Application started!")
    while True:
        getPositionData()
        time.sleep(2)

except (KeyboardInterrupt):
    running = False
    print("Applications closed!")