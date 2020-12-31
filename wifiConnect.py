import os
from pathlib import Path
import json


class Finder:
    def __init__(self, *args, **kwargs):
        self.interface_name = "wlan0"
        self.main_dict = {}
        self.skip = False
        self.home = str(Path.home())+"/cameraProject/"
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        check = self.searchForavailableWIFI(server_name=self.server_name)
        if check:
            if(os.path.exists(self.home + 'wifiConfig.json')):
                with open(self.home+'wifiConfig.json', 'rb') as json_file:
                    config = json.load(json_file)
                    settings = config["settings"]
                    self.interface_name = "wlan0"  # i. e wlp2s0
                    if settings:
                        for setting in settings:
                            self.server_name = setting["servername"]
                            self.password = setting["password"]
                            check = self.searchForavailableWIFI(
                                server_name=self.server_name)
                            if not check:
                                print(server_name + " WIFI found")
                                # self.run()
                                break
                            else:
                                print(server_name + " wifi not found")
        else:
            print("already connected to " + self.server_name)

    def run(self):
        checkCommand = "iwgetid -r"
        checkResult = os.popen(checkCommand)
        checkResult = list(checkResult)
        if checkResult:
            if self.server_name == checkResult[0].strip():
                print(checkResult)
                self.skip = True

        if self.skip == False:
            command = """sudo iwlist wlan0 scan | grep -ioE 'ssid:"(.*{}.*)'"""
            result = os.popen(command.format(self.server_name))
            result = list(result)

            if "Device or resource busy" in result:
                return None
            else:
                ssid_list = [item.lstrip('SSID:').strip('"\n')
                             for item in result]
                print("Successfully get ssids {}".format(str(ssid_list)))

            for name in ssid_list:
                try:
                    result = self.connection(name)
                    return result
                except Exception as exp:
                    print("Couldn't connect to name : {}. {}".format(name, exp))
                    return False
                else:
                    if result:
                        print("Successfully connected to {}".format(name))
                        return True
            return False
        else:
            print("Already Connected")
            return True

    def connection(self, name):
        try:
            os.system("sudo nmcli d wifi connect {} password {}".format(
                name, self.password))
        except:
            raise
        else:
            return True

    def searchForavailableWIFI(self, server_name):
        process = os.popen("sudo iw dev wlan0 scan | grep SSID")
        preprocessed = process.read()
        if(server_name in preprocessed):
            return False
        else:
            return True


if __name__ == "__main__":
    home = str(Path.home())
    interface_name = "wlan0"  # i. e wlp2s0
    server_name = "OakOne"
    password = "ganesha2301"
    F = Finder(server_name=server_name, password=password,
               interface=interface_name)
