#!/usr/bin/env python3

#
# SECDED ECC calculator for debugging DRAM ECC
# ./ecc_cal.py <64-bit data in hex>


import sys

def linear_xor(input):
  out = 0
  while input != 0:
    out ^=  (input & 1)
    input >>= 1
  return out

# Recursively partition the bits and do a dict lookup
xor_4b = {0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 1, 9: 0, 10: 0, 11: 1, 12: 0, 13: 1, 14: 1, 15: 0}
def xor_div(input, len):
  if input == 0:
    return 0
  if len == 4:
    return xor_4b[input]
  len >>= 1
  return xor_div(input & ((1 << len) - 1), len) ^ xor_div(input >> len, len)

ECC_MASK = [ 
#        64......56......48......40......32......24......16.......8.......0
#         |       |       |       |       |       |       |       |       |
         0b1011010011001011001011001101001011000100101100010010110010110111, # bit[0]
         0b0101010101010101010101010101010101001001010100100101010101011011, # bit[1]
         0b0110011001100110100110011001100110010010011001001001101001101101, # bit[2]
         0b0111100001111000111000011110000111100011100010001110001110001110, # bit[3]
         0b0111111110000000111111100000000111111100000011110000001111110000, # bit[4]
         0b1000000000000000111111111111111000000000000011111111110000000000, # bit[5]
         0b0000000000000000111111111111111111111111111100000000000000000000, # bit[6]
         0b1111111111111111000000000000000000000000000000000000000000000000  # bit[7]         
]

def calculate_ecc(data):
  ecc = 0
  for i in range(len(ECC_MASK)):
    #ecc |= xor_div(data & ECC_MASK[i], 64) << i
    ecc |= linear_xor(data & ECC_MASK[i]) << i
  return ecc

if __name__ == "__main__":
  data = int(sys.argv[1], 16)
  ecc = calculate_ecc(data);
  print('ECC for data={data:016x} ecc={ecc:02x}'.format(data=data, ecc=ecc))
  sys.exit(0)
