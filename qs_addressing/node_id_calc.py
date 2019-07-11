#!/usr/bin/env python3

import sys
import os
import re
import math
import platform
import string
import collections
import time

'''
#define NODEID(x, y, port, dev) \                                           
        ((((u32)(x) << 6) & 0x000001C0) | (((u32)(y)<< 3) & 0x00000038) | \ 
        (((u32)(port) << 2) & 0x00000004) | ((u32)(dev) & 0x00000003))      

  y
|     +-------+  P=1
|     |___|_d_|
|     |   |   |
|     +-------+
|   P=0  (x, y)
| 
---------------- x
X, Y : cross point node x,y                          
P: 0: left bottom corner, 1: right top corner        
Z: 0: left HNF, 1: right HNF                          

'''

class pError(Exception):
  pass

def nodeid_enc(x, y, p, d):
  nodeid = (x << 6) & 0x000001C0 | \
           (y << 3) & 0x00000038 | \
           (p << 2) & 0x00000004 | \
           d & 0x00000003
  return nodeid

def nodeid_dec(nodeid):
  x = (nodeid & 0x000001C0) >> 6
  y = (nodeid & 0x00000038) >> 3 
  p = (nodeid & 0x00000004) >> 2
  d = nodeid & 0x00000003
  return x,y,p,d

def main():
  print ('Mesh nodeid helper:')

  if len(sys.argv) < 3:
    print('syntax:\n\t'+sys.argv[0]+' enc x y port dev')
    print('\t'+sys.argv[0]+' dec nodeid')
    sys.exit(-1)

  encode = sys.argv[1]
  if re.search(r'^e', encode):
    print('calc nodeid')
    x = int(sys.argv[2])
    y = int(sys.argv[3])
    port = int(sys.argv[4])
    dev = int(sys.argv[5])
    nodeid = nodeid_enc(x, y, port, dev)
    print('nodeid={nodeid}'.format(nodeid=nodeid))
  elif re.search(r'^d', encode):
    print('decode')
    nodeid = int(sys.argv[2])
    x, y, port, dev = nodeid_dec(nodeid)
    print('x={x} y={y} port={port} dev={dev}'.format(**locals()))
  else:
    raise pError('Unsupported operation')

if __name__ == '__main__':
    main()
