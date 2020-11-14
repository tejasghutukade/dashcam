import serial
import pynmea2
import subprocess
import datetime
# subprocess.call('sudo systemctl stop gpsd.socket' , shell=True)
# subprocess.call('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock',shell=True)

SERIAL_PORT = "/dev/ttyS0"
running = True

# In the NMEA message, the position gets transmitted as:
# DDMM.MMMMM, where DD denotes the degrees and MM.MMMMM denotes
# the minutes. However, I want to convert this format to the following:
# DD.MMMM. This method converts a transmitted string to the desired format
def formatDegreesMinutes(coordinates, digits):
    
    parts = coordinates.split(".")

    if (len(parts) != 2):
        return coordinates

    if (digits > 3 or digits < 2):
        return coordinates
    
    left = parts[0]
    right = parts[1]
    degrees = str(left[0:-2])
    minutes = str(right[:3])

    return degrees + "." + minutes

# This method reads the data from the serial port, the GPS dongle is attached to,
# and then parses the NMEA messages it transmits.
# gps is the serial port, that's used to communicate with the GPS adapter
def getPositionData(gps):
    data = gps.readline()    
    
    message = data[0:6]
    if (message == "$GPRMC"):
        # GPRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        msg = pynmea2.parse(data)
        #dt = datetime.utcfromtimestamp(msg.timestamp)
        print(msg)
        print(msg.latitude)
        print(msg.lat_dir)
        print(msg.longitude)
        print(msg.lon_dir)
        parts = data.split(",")
        if parts[2] == 'V':
            # V = Warning, most likely, there are no satellites in view...
            print("GPS receiver warning")
        else:
            # Get the position data that was transmitted with the GPRMC message
            # In this example, I'm only interested in the longitude and latitude
            # for other values, that can be read, refer to: http://aprs.gids.nl/nmea/#rmc
            longitude = formatDegreesMinutes(parts[5], 3)
            latitude = formatDegreesMinutes(parts[3], 2)
            print("Your position: lon = " + str(longitude) + ", lat = " + str(latitude))
    else:
        # Handle other NMEA messages and unsupported strings
        pass

print("Application started!")
gps = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 0.5)

while running:
    try:
        getPositionData(gps)
    except KeyboardInterrupt:
        running = False
        gps.close()
        print("Application closed!")
    except:
        # You should do some error handling here...
        print("Application error!")