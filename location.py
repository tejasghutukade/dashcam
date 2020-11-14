import gpsd-json



def getPosition(gps):
    nx=gpsd.next()
    if nx['class'] == 'TPV':
        latitude = getattr(nx, 'lat', "Unknown")
        longitude = getattr(nx, 'lan', "Unknown")
        print("Your Position : lon = " + str(longitude) + ", lat =" + str(latitude))