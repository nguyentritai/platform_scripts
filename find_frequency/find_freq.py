#!/usr/bin/env python2.7                          
                                                  
import os                                         
import commands
import platform                                   
import sys                                        
import string                                     
import collections                                
import re                                         
import time                                       

L1_LAT_CYCLES = 5.0

def print_cpufreq(l1_lat):
  cpufreq = round(1.0/(float(l1_lat)/L1_LAT_CYCLES), 2)
  print 'CPU frequency: ', cpufreq, 'GHz'

def main():
  # Change PM gorverner to performance to run at highest frequency
  cmd = 'cpupower frequency-set -g performance'                  
  s = commands.getoutput(cmd)                            
  print 'Detecting CPU frequency ... Be patient!'
  cmd = '../utils/lat_mem_rd -P1 1 64'
  s = commands.getoutput(cmd)                            
  ss = re.split('\n+', s)
  # Retrieve L1 latency (in nsec) at 15.6K data size
  for txt in ss:
    match = re.search(r'0.01562', txt)
    if match:
      l1_lat = match.string.split(' ')[1]
      print_cpufreq(l1_lat)
      exit()
  
  print "Can't detect CPU frequency"
  print s

if __name__ == '__main__':            
    main()
