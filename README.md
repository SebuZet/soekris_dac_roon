### Installation
 - Go to home folder (eg. /home/pi)
 - Download script to folder
 - Install python (if needed)
 - Install roonapi and dam1021 modules

```sh
cd /home/pi
wget https://raw.githubusercontent.com/SebuZet/soekris_dac_roon/main/soekris_dac_roon.py
sudo pip3 install roonapi dam1021
```

### Launch plugin at system start
Open /etc/rc.local with your favouite editor (eg. sudo vi /etc/rc.local) :) and add following line before 'exit 0':

python3 /home/pi/soekris_dac_roon.py &
