#!/bin/env python

"""
Copyright (C) 2018  Martin Brodbeck <martin@brodbeck-online.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import signal
import subprocess
from systemd import journal
import time

SLEEP_SECONDS = 5
CPU_TEMP_ON_THRESHOLD = 65
DISK_TEMP_ON_THRESHOLD = 39
CPU_TEMP_OFF_THRESHOLD = 45
DISK_TEMP_OFF_THRESHOLD = 32


class SignalHandler(object):
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


class FanManager(object):
    def __init__(self):
        self.fan_switch = "n/a"

    def get_hdd_temps(self):
        temps = []
        cmd = subprocess.Popen(
            r'''lsblk -d | awk '/^sd/ {printf "/dev/%s\n", $1}' ''', shell=True, stdout=subprocess.PIPE)
        for line in cmd.stdout:
            disk = line.decode('utf8').strip('\n')
            cmd = subprocess.Popen('smartctl -a ' + disk + ' -d sat | grep "Temp" | ' +
                                   r'''awk '{printf "%s\n", $10}' ''', shell=True, stdout=subprocess.PIPE)
            for line in cmd.stdout:
                temps.append(int(line.decode('utf8').strip('\n')))
        return temps

    def get_cpu_temps(self):
        temps = []
        for i in range(0, 5):
            cmd = subprocess.Popen('cat /sys/class/thermal/thermal_zone' +
                                   str(i) + '/temp', shell=True, stdout=subprocess.PIPE)
            temp = cmd.communicate()[0].decode('utf8').strip('\n')
            temp = int(temp) / 1000
            temps.append(temp)
        return temps

    def handle_fan(self):
        cpu_temps = self.get_cpu_temps()
        hdd_temps = self.get_hdd_temps()
        fan_on_cpu = any(temp > CPU_TEMP_ON_THRESHOLD for temp in cpu_temps)
        fan_on_hdd = any(temp > DISK_TEMP_ON_THRESHOLD for temp in hdd_temps)
        if (fan_on_cpu or fan_on_hdd) and not self.fan_switch == "on":
            journal.send("Turning the system fan on.")
            self.fan_on()
            self.fan_switch = "on"
        fan_off_cpu = all(temp < CPU_TEMP_OFF_THRESHOLD for temp in cpu_temps)
        fan_off_hdd = all(temp < DISK_TEMP_OFF_THRESHOLD for temp in hdd_temps)
        if (fan_off_cpu and fan_off_hdd) and not self.fan_switch == "off":
            journal.send("Turning the system fan off.")
            self.fan_off()
            self.fan_switch = "off"

    def fan_on(self):
        subprocess.run(['i2cset', '-y', '1', '0x60', '0x05', '0x00'])

    def fan_off(self):
        subprocess.run(['i2cset', '-y', '1', '0x60', '0x05', '0x05'])


if __name__ == '__main__':
    sig_handler = SignalHandler()
    fan_manager = FanManager()

    while(True):
        if sig_handler.kill_now:
            fan_manager.fan_off()
            break
        fan_manager.handle_fan()
        time.sleep(SLEEP_SECONDS)
