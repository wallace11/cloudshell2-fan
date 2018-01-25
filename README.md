# cloudshell2-fan
Python script that turns the cloudshell2 fan on/off

## Requirements
* i2c-tools
* python (3.x)
* python-systemd
* smartmontools

## Installation (manually)
1. Copy the python script **cloudshell2-fan.py** to /usr/bin/cloudshell2-fan, omitting the .py suffix  
   (or adopt the path to the python script in cloudshell2-fan.service)
2. Copy the file **cloudshell2-fan.service** to /etc/systemd/system/
3. Start the service with `systemctl start cloudshell2-fan.service`

There will also be a Arch Linux AUR package (not finished yet).

## Misc
Of course you can adopt the script and for example change the temperature thresholds or the sleep duration.
