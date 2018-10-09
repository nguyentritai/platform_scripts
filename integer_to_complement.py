#!/usr/bin/python                                    
# syntax:
#        integer_to_complement.py <val> 

import sys
                                                     
def tohex(val, nbits):                               
    return hex((val + (1 << nbits)) % (1 << nbits))  
                                                     
if __name__ == "__main__":                           
    print "Convert Integer: %s <=> Two's complement Hex (32-bit): %s" % (sys.argv[1], tohex(int(sys.argv[1]), 32))
