import os
import subprocess

if __name__ == "__main__":
    p0 = subprocess.Popen("sudo killall wpa_supplicant", shell=True)
    p0.wait()
    p1 = subprocess.Popen("sudo systemctl restart dhcpcd", shell=True)
    p1.wait()
    print("stop systemctl restart dhcpcd")
    #time.sleep(2)
    p2 = subprocess.Popen("sudo ifconfig wlan0 192.168.4.0", shell=True)
    p2.wait()
    print("stop ifconfig wlan0 192.168.4.0")
    #time.sleep(2)
    p3 = subprocess.Popen("sudo systemctl restart dnsmasq", shell=True)
    p3.wait()
    print("stop restart dnsmasq")
    #time.sleep(2)
    p4 = subprocess.Popen("sudo systemctl restart hostapd", shell=True)
    p4.wait()
    print("stop rsystemctl restart hostapd")