import os.path
import signal
import sys 
import time
import serial
import uuid
import json
from roonapi import RoonDiscovery, RoonApi

appinfo = {
        "extension_id": "com.sebuzet.soekris_volume_extension",
        "display_name": "Soekris R2R DAC Volume Controller",
        "display_version": "1.1.0",
        "publisher": "SebuZet",
        "email": "zetowy@gmail.com",
        "website": "https://github.com/SebuZet/soekris_dac_roon",
    }

class dam1021roon:

    def __init__(self, device, roon, id, name):
        self.device = device
        self.ser = self.create_serial_device()
        self.roon = roon
        self.id = id
        self.last_volume = 0
        self.roon.register_volume_control(self.id, name, self.set_volume, 0, "number", 1, -80, 0)
        self.set_volume_cmd = 'V{:+03d}\r'
        self.loop = True

    def create_serial_device(self):
        return serial.Serial(self.device, 115200, timeout=0.25)

    def set_volume(self, control_key, event, data):
        if event == "set_mute":
            new_level = -99 if data else self.last_volume
            try:
                self.ser.write(self.set_volume_cmd.format(new_level))
                self.roon.update_volume_control(self.id, mute = True)
            except:
                import traceback
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                return
        elif event == "set_volume":
            new_level = data
            try:
                self.ser.write(self.set_volume_cmd.format(new_level).encode())
                self.roon.update_volume_control(self.id, volume = data, mute = False)
            except Exception:
                import traceback
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                return
            self.last_volume = data

    def cleanup(self):
        if self.loop:
            self.loop = False
       	    self.roon.stop()
            self.ser.close()
            return True
        else:
            return False

    def run_loop(self):
        while self.loop:
            x = 0
            try:
                x = self.ser.read()
            except:
                self.ser = self.create_serial_device()
            if x == 'V':
                try:
                    x = self.ser.read()
                except:
                    self.ser = self.create_serial_device()
                b = 10
            if x == '+' or x == '-':
                v = 0
                try:
                    v = b * int(self.ser.read()) + int(self.ser.read())
                except:
                    continue
                if x == '-':
                    v = v * -1
                if v == -99:
                    self.roon.update_volume_control(self.id, mute = True)
                else:
                    self.roon.update_volume_control(self.id, mute = False)
                    self.roon.update_volume_control(self.id, volume = v)
                    self.last_volume = v
            time.sleep(0.01)

def read_config(file_name):
    id = str(uuid.uuid4())
    if os.path.isfile(file_name):
        with open(file_name, encoding='utf-8') as f:
            json_data = json.load(f)
            if "id" in json_data:
                id = json_data["id"]
            if "token" in json_data and "core_id" in json_data:
                return json_data["token"], json_data["core_id"], id
    return None, None, id

def save_config(file_name, token, core_id, id):
    print("Save configuration")
    config = {}
    config["token"] = token
    config["core_id"] = core_id
    config["id"] = id
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(config, f)

def cleanup(signum, frame):
    print("cleaning up")
    if plugin:
        plugin.cleanup()
    sys.exit(signum)

for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, cleanup)

plugin = None
token = None
core_id = None
ctrl_id = None
config_file = os.path.dirname(sys.argv[0]) + '/soekris_dac_roon.json'
token, core_id, ctrl_id = read_config(config_file)
discover = RoonDiscovery(None)
servers = discover.all()
apis = [RoonApi(appinfo, None, server[0], server[1], False) for server in servers]

if not token or not core_id:
    auth_api = []
    while len(auth_api) == 0:
        print("Waiting for authorisation")
        time.sleep(1)
        auth_api = [api for api in apis if api.token is not None]

    api = auth_api[0]

    # This is what we need to reconnect
    core_id = api.core_id
    token = api.token
    save_config(config_file, token, core_id, ctrl_id)

print("Shutdown discovery")
discover.stop()
for api in apis:
    api.stop()

roon = RoonApi(appinfo, token, None, None, True, core_id)

plugin = dam1021roon('/dev/ttyUSB0', roon, ctrl_id, "dam1021")
plugin.run_loop()
