import os

class Finder:
    def __init__(self, *args, **kwargs):
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        self.main_dict = {}

    def run(self):
        command = """sudo iwlist wlan0 scan | grep -ioE 'ssid:"(.*{}.*)'"""
        result = os.popen(command.format(self.server_name))
        result = list(result)

        if "Device or resource busy" in result:
                return None
        else:
            ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]
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
        
        
    def connection(self, name):
        try:
            os.system("sudo nmcli d wifi connect {} password {}".format(name,self.password))
        except:
            raise
        else:
            return True