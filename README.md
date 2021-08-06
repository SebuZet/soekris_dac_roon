# Roon volume control endpoint for Soekris R2R DAC

This is a Roon extension for controlling volume on your Soekris R2R DAC from roon application

### Installation
 1. Go to home folder (eg. /home/pi)
 2. Download script to folder
 3. Edit script according to your configuration (by defulat script is using RS232 port on /dev/ttyUSB0)
 4. Install python (if needed)
 5. Install roonapi and dam1021 modules
 6. Launch roon application
    * Go to Preferences/Extensions and enable "Soekris R2R DAC Volume Controller" extension
    * Go to audio device settings and change volume settings to "Soekris R2R DAC Volume Controller: dam1021"

```sh
cd /home/pi
wget https://raw.githubusercontent.com/SebuZet/soekris_dac_roon/main/soekris_dac_roon.py
sudo pip3 install roonapi dam1021
```

### Launch plugin at system start
Open /etc/rc.local with your favouite editor (eg. sudo vi /etc/rc.local) :) and add following line before 'exit 0':

python3 /home/pi/soekris_dac_roon.py &

### Requirements
 * Soekris R2R DAC :)
 * rs232 connection between your soekris DAC and raspberry pi
 * Roon application with server
