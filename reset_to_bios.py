#!/usr/bin/python                                    

import sys
import commands
                                                     
if __name__ == "__main__":                           
  cmd = "./sysinfo.py bmc | grep \"IP Address\" | awk -F\": \" '{print $2}'"
  bmc_ip = commands.getoutput(cmd)
  cmd = 'ipmitool -H ' + bmc_ip + ' -U ADMIN -P ADMIN -I lanplus chassis bootdev bios'
  s = commands.getoutput(cmd)
  print s 
  cmd = 'ipmitool -H ' + bmc_ip + ' -U ADMIN -P ADMIN -I lanplus chassis power reset'
  s = commands.getoutput(cmd)
  print s 

