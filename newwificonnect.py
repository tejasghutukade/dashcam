import os
import subprocess
import time



if __name__ == "__main__":
    p1 = subprocess.Popen("sudo systemctl stop dnsmasq", shell=True)
    p1.wait()
    print("stop dnsmasq")
    #time.sleep(2)
    p2 = subprocess.Popen("sudo systemctl stop hostapd", shell=True)
    p2.wait()
    print("stop hostapd")
    #time.sleep(2)
    p3 = subprocess.Popen("sudo dhclient -r", shell=True)
    p3.wait()
    print("stop dhclient -r")
    #time.sleep(2)
    p4 = subprocess.Popen("sudo systemctl restart dhcpcd", shell=True)
    p4.wait()
    print("stop restart dhcpcd")
    #time.sleep(2)
    p5 = subprocess.Popen("sudo wpa_supplicant -B -i wlan0 -c wpa_supplicant_WHE-BELL.conf", shell=True)
    p5.wait()
    print("stop connect wpasupplicant")
    #time.sleep(2)
    
