#!/usr/bin/env python2.7

import os
import commands
import platform
import sys
import string
import collections
import re
import time

def lpi_ctrl(ctl = 'on'):
    for cpu in range(0, 32):
        for state in [ '0', '1', '2', '3', '4', '5' ]:
            cpustate = '/sys/devices/system/cpu/cpu' + str(cpu) + '/cpuidle/state' + state + '/disable'
            cmd = 'cat ' + cpustate
            a = commands.getoutput(cmd)
            if ctl is 'off':
                if a is '1':
                    return
                cmd = 'echo 1 > ' + cpustate
            else:
                if a is '0':
                    return
                cmd = 'echo 0 > ' + cpustate
            commands.getoutput(cmd)
    # delay to make sure all RB registers accessible
    if ctl is 'off':
        time.sleep(3)

def main():
    lpi_ctrl(ctl = 'off')

if __name__ == '__main__':
    main()
