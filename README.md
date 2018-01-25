# cloudshell2-fan
Python script that turns the cloudshell2 fan on/off

## Requirements
* i2c-tools
* python (3.x)
* python-systemd
* smartmontools

## Installation
1. Copy the python script to /usr/bin/cloudshell2-fan, omitting the .py suffix  
   (or adopt the path to the python script the systemd file)
2. Copy the systemd file to /etc/systemd/system/
3. Start the service with `systemctl start cloudshell2-fan`

There will also be a Arch Linux AUR package (not finished yet).

## Misc
Of course you can adopt the script and for example change the temperature thresholds or the sleep duration.
