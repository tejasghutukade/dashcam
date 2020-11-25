
import time
import os
from wifiConnect import Finder


if __name__ == "__main__":
    # Server_name is a case insensitive string, and/or regex pattern which demonstrates
    # the name of targeted WIFI device or a unique part of it.
    server_name = "OakOne"
    password = "ganesha2301"
    interface_name = "wlan0" # i. e wlp2s0  
    
   
    F = Finder(server_name=server_name,
               password=password,
               interface=interface_name)
    response = F.run()
    while (response == False):
        time.sleep(1)
        print('waiting for a second to try again')
        response = F.run()
        