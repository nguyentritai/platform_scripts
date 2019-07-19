#!/usr/bin/env python3

import sys
import os
import re
import math
#import sknobs
import platform
import string
import collections
import time
#import commands

'''
syntax:
	./addr_routing.py <Memory system address>

Decoding address:
SA (system addr)  -> MA (memory address - continous) -> linear address  -> device adderss
                                                        after shuttered 

'''


"order: row rank bank column bytes"
byte_bits=3
col_bits=10
row_bits=16
bank_bits=4
rank_bits=1

mcu_mask=0xFF
bank_hashing=1

'''
DV: Mesh programming for HNF hashing
Address HNF hashing <-------> HNFNodeid based on SNF mode or MCU mask

 if (snf_mode == 1 || snf_mode == 2 || snf_mode == 4 || snf_mode==6 || snf_mode == 8 || snf_vector == 1 || snf_vector == 17 || snf_vector == 51 || snf_vector == 119 || snf_vector ==255) begin
    case(select[3:0])
      'd0  : return `HNF0_NID12;
      'd1  : return `HNF2_NID140;
      'd8  : return `HNF4_NID332;
      'd9  : return `HNF6_NID460;
      'd2  : return `HNF8_NID20;
      'd3  : return `HNF10_NID148;
      'd10 : return `HNF12_NID340;
      'd11 : return `HNF14_NID468;
      'd4  : return `HNF16_NID28;
      'd5  : return `HNF18_NID156;
      'd12 : return `HNF20_NID348;
      'd13 : return `HNF22_NID476;
      'd6  : return `HNF24_NID36;
      'd7  : return `HNF26_NID164;
      'd14 : return `HNF28_NID356;
      'd15 : return `HNF30_NID484;
      default: assert(0);
    endcase
  end
  else if (snf_vector == 16 || snf_vector == 240 || snf_vector == 15) begin
    case(select[3:0])
      'd0  : return `HNF0_NID12;
      'd1  : return `HNF2_NID140;
      'd2  : return `HNF4_NID332;
      'd3  : return `HNF6_NID460;
      'd4  : return `HNF8_NID20;
      'd5  : return `HNF10_NID148;
      'd6  : return `HNF12_NID340;
      'd7  : return `HNF14_NID468;
      'd8  : return `HNF16_NID28;
      'd9  : return `HNF18_NID156;
      'd10 : return `HNF20_NID348;
      'd11 : return `HNF22_NID476;
      'd12 : return `HNF24_NID36;
      'd13 : return `HNF26_NID164;
      'd14 : return `HNF28_NID356;
      'd15 : return `HNF30_NID484;
      default: assert(0);
    endcase
  end


'''

'''
QS has 32 HN-Fs (HW). The hash selects the HN-F, which then picks the closest SN-F/DMC (SW)
  select [0] = (6^11^16^...^46) 
  select [1] = (7^12^17^...^47) 
  select [2] = (8^13^18^...^43) 
  select [3] = (9^14^19^...^44) 
  select [4] = (10^15^20^...^45) 
HN-F SAM maps select[4:0] to actual node IDs in the mesh. In HN-F CAL mode, the HN-Fs are in pairs and 
select[3:0] is used to address the 16 pairs while select[4] is used to target the device in the pair.
So we order the list select[4] then 1..3 so [4] is used to select the device in the HNF

X, Y : cross point node x,y
P: 0: left bottom corner, 1: right top corner
Z: 0: left HNF, 1:right HNF

Example of 8 SNFs and 32 HNFs
Address 	Address Hash	HNF Selected [X,Y,P,Z]
0x8000_0000	0b00001		[2,1,1,0]	[0,1,0]
0x8000_0040	0b00000		[0,1,1,0]	[0,1,0]
0x8000_0080	0b00011		[2,2,1,0]	[0,2,0]
0x8000_00c0	0b00010		[0,2,1,0]	[0,2,0]
0x8000_0100	0b00101		[2,3,1,0]	[0,3,0]
0x8000_0140	0b00100		[0,3,1,0]	[0,3,0]
0x8000_0180	0b00111		[2,4,1,0]	[0,4,0]
0x8000_01c0	0b00110		[0,4,1,0]	[0,4,0]
0x8000_0200	0b01001		[7,1,1,0]	[7,1,0]
0x8000_0240	0b01000		[5,1,1,0]	[7,1,0]
0x8000_0280	0b01011		[7,2,1,0]	[7,2,0]
0x8000_02c0	0b01010		[5,2,1,0]	[7,2,0]
0x8000_0300	0b01101		[7,3,1,0]	[7,3,0]
0x8000_0340	0b01100		[5,3,1,0]	[7,3,0]
0x8000_0380	0b01111		[7,4,1,0]	[7,4,0]
0x8000_03c0	0b01110		[5,4,1,0]	[7,4,0]
0x8000_0400	0b10001		[2,1,1,1]	[0,1,0]
0x8000_0440	0b10000		[0,1,1,1]	[0,1,0]
0x8000_0480	0b10011		[2,2,1,1]	[0,2,0]
0x8000_04c0	0b10010		[0,2,1,1]	[0,2,0]
0x8000_0500	0b10101		[2,3,1,1]	[0,3,0]
0x8000_0540	0b10100		[0,3,1,1]	[0,3,0]
0x8000_0580	0b10111		[2,4,1,1]	[0,4,0]
0x8000_05c0	0b10110		[0,4,1,1]	[0,4,0]
0x8000_0600	0b11001		[7,1,1,1]	[7,1,0]
0x8000_0640	0b11000		[5,1,1,1]	[7,1,0]
0x8000_0680	0b01011		[7,2,1,1]	[7,2,0]
0x8000_06c0	0b01010		[5,2,1,1]	[7,2,0]
0x8000_0700	0b01101		[7,3,1,1]	[7,3,0]
0x8000_0740	0b01100		[5,3,1,1]	[7,3,0]
0x8000_0780	0b11111		[7,4,1,1]	[7,4,0]
0x8000_07c0	0b11110		[5,4,1,1]	[7,4,0]
'''
HNF32_SELECT = [
#               48......40......32......24......16.......8.......0
#                |       |       |       |       |       |       |
                0b010000100001000010000100001000010000100001000000, # select[0]
                0b100001000010000100001000010000100001000010000000, # select[1]
                0b000010000100001000010000100001000010000100000000, # select[2]
                0b000100001000010000100001000010000100001000000000, # select[3]
                0b001000010000100001000010000100001000010000000000, # select[4]
               ]

'''
Map HNF address hash value to HNFNODEID
'''
mcu_mask_snf_mode1 = [0x01, 0x02, 0x04, 0x08, 0x06, 0x11, 0x33, 0x77, 0xFF]
hnf_addr_hash_2_xy_snf_mode1 = {0: 0x01, 1: 0x21, 2: 0x02, 3: 0x22,
		                 4: 0x03, 5: 0x23, 6: 0x04, 7: 0x24,
		                 8: 0x51, 9: 0x71, 10: 0x52, 11: 0x72,
		                 12: 0x53, 13: 0x73, 14: 0x54, 15: 0x74} 

mcu_mask_snf_mode2 = [0x10, 0xf0, 0x0f]
hnf_addr_hash_2_xy_mode2 = {0: 0x01, 1: 0x21, 2: 0x51, 3: 0x71,
	                 4: 0x02, 5: 0x22, 6: 0x52, 7: 0x72,
	                 8: 0x03, 9: 0x23, 10: 0x53, 11: 0x73,
	                 12: 0x04, 13: 0x24, 14: 0x54, 15: 0x74} 

xy_2_hnfpair = {0x01: 0, 0x21: 1, 0x51: 2, 0x71: 3,
		0x02: 4, 0x22: 5, 0x52: 6, 0x72: 7,
		0x03: 8, 0x23: 9, 0x53: 10, 0x73: 11,
		0x04: 12, 0x24: 13, 0x54: 14, 0x74: 15}

def popcount(i):
    i = i - ((i >> 1) & 0x55555555)
    i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
    return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24

# Recursively partition the bits and do a dict lookup
xor_4b = {0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 1, 9: 0, 10: 0, 11: 1, 12: 0, 13: 1, 14: 1, 15: 0}
def xor_div(input, len):
  #print ('input ' + str(hex(input) + ' ' + str(len)))
  if input == 0:
    return 0
  if len == 4:
    return xor_4b[input]
  len >>= 1
  return xor_div(input & ((1 << len) - 1), len) ^ xor_div(input >> len, len)

def steer(sa):
  '''
  Hash to the HN-F and then steer to the closet MCU. Should be able to compute the XOR of all bit selects at the same time
  as they are in 5-bit chunks (e.g. XOR [10:6], [15:11],... [47:43]). 
  '''
  addr_hash = 0
  for i in range(len(HNF32_SELECT)):
      addr_hash |= xor_div(sa & HNF32_SELECT[i], 64) << i
  print ('addr hash=0b{addr_hash:05b} '.format(**locals()))
  hnf_pair_select_id = addr_hash & 0xF 
  cal = (addr_hash & 0x10) >> 4
  if mcu_mask in mcu_mask_snf_mode1:
    hnf_addr_hash_2_xy = hnf_addr_hash_2_xy_snf_mode1
  elif mcu_mask in mcu_mask_snf_mode2:
    hnf_addr_hash_2_xy = hnf_addr_hash_2_xy_snf_mode2
  else:
    raise MemgenError('Unsupported MCU mask ({mcu_mask:02x})!'.format(**locals()))

  xy = hnf_addr_hash_2_xy[hnf_pair_select_id]
  xp = (xy >> 4) & 0xF 
  yp = xy & 0xF
  hnf_pair_id = xy_2_hnfpair[xy] 
  print ('hnf pair id={hnf_pair_id:01d} cal={cal:01d} ({xp:01d},{yp:01d})'.format(**locals()))
  print ('HNF Selected: [x, y, port, cal_mode] = [{xp:01d}, {yp:01d}, 1, {cal:01d}]'.format(**locals()))

def sa2ma(sa):
  """
    Translates SA (system address) to MA (memory address) bit 31 and 39 are the relevant ones for
    regions at 0x0000 8000 0000 (2GB) and 0x0080 8000 0000
  """
  # MA[39]    = SA[40]
  # MA[38:32] = SA[38:32]
  # MA[31]    = SA[31] & SA[39]
  # MA[30:0]  = SA[30:0]

  # Simple remapping is probably faster
  if sa < 0x100000000:
    return sa - 0x80000000
  if sa >= 0x8080000000:
    return sa - 0x8000000000
  raise MemgenError('SA {sa:x} outside of valid range!'.format(sa=sa))

def set_bit32(cur, start, count):
  v = cur
  for i in range(0, 31):
    if (i < start):
      continue
    if (i > start + count):
      break
    v |= (1 << i)
  return v

def mc_addr_inf(ma):
  '''
  Hashing enabled && mcu > 1, strip out SA based on the number of MCUs using 16 HN-Fs:
  1 None
  2 [7]
  4 [8, 7]
  8 [9, 8, 7]
  '''
  num_mc = popcount(mcu_mask)
  if num_mc == 1:
    lnr_addr = ma
  elif num_mc == 2:
    lnr_addr = (((ma >> (7 + 1))) << 7) | (ma & ((1 << 7) - 1))
  elif num_mc == 4:
    lnr_addr = (((ma >> (8 + 1))) << 7) | (ma & ((1 << 7) - 1))
  elif num_mc == 8:
    lnr_addr = (((ma >> (9 + 1))) << 7) | (ma & ((1 << 7) - 1))

  print('lnr_addr (memory addr after shuttered)={lnr_addr:010x}'.format(**locals()))

  byte_bit_idx = 0
  byte_bits_mask = set_bit32(0, 0, byte_bits)
  byte = (lnr_addr >> byte_bit_idx) & byte_bits_mask
  print('byte: ' + hex(byte))

  col_bit_idx = byte_bit_idx + byte_bits
  col_bits_mask = set_bit32(0, 0, col_bits)
  col = (lnr_addr >> col_bit_idx) & col_bits_mask
  print('col: ' + hex(col))

  bank_bit_idx = col_bit_idx + col_bits
  bank_bits_mask = set_bit32(0, 0, bank_bits)
  bank = (lnr_addr >> bank_bit_idx) & bank_bits_mask

  rank_bit_idx = bank_bit_idx + bank_bits
  rank_bits_mask = set_bit32(0, 0, rank_bits)
  rank = (lnr_addr >> rank_bit_idx) & rank_bits_mask
  print('rank: ' + hex(rank))

  row_bit_idx = rank_bit_idx + rank_bits
  row_bits_mask = set_bit32(0, 0, row_bits)
  row = (lnr_addr >> row_bit_idx) & row_bits_mask
  print('row={row:04x}'.format(**locals()))


  # now that the address is decoded, implement bank hashing if enabled                                                                 
  '''
  bank hashing is enabled
  8 banks:                                                                                                                             
   hashed_bank_address[3:0] = {1’b0, decoded_bank_address[2:0] ^ row_address[2:0] ^                                                   
   row_address[5:3] ^ row_address[8:6] ^ row_address[11:9]}                                                                           
  16 banks:                                                                                                                            
   hashed_bank_address[3:0] = decoded_bank_address[3:0] ^ row_address[3:0] ^ row_address[7:4] ^ row_address[11:8] ^ row_address[15:12]
 
  '''
  # 8-bank hashing using 3 bank bits
  hashed_bank_addr = bank
  if bank_hashing:
    if bank_bits == 3:
      hashed_bank_addr = (bank & 0x7) ^ \
                      (row & 0x7) ^ \
                      ((row>>3) & 0x7) ^ \
                      ((row>>6) & 0x7) ^ \
                      ((row>>9) & 0x7)
  # 16-bank hashing using 4 bank bits                                                                                                  
    elif bank_bits == 4:                                                                              
      hashed_bank_addr = (bank & 0xf) ^ \
                      (row & 0xf) ^ \
                      ((row>>4) & 0xf) ^ \
                      ((row>>8) & 0xf) ^ \
                      ((row>>12) & 0xf)

  bank = hashed_bank_addr                                                                                            
  bg = (bank >> 2) & 0x3
  ba = bank & 0x3
  print('bank: {bank:01x} (bg: {bg:01x}, ba {ba:01x})'.format(bank=bank, bg=bg, ba=ba))

  # decoded addr order row[33:18] rank[17] bank[16:13] column[12:3] byte[2:0]
  # DDR4 device address order bank {ba, bg} - row - col
  dev_bank = bg | (ba << 2)
  dev_addr = dev_bank << (col_bits + row_bits) |\
             row << col_bits | col
  print('dev addr={dev_addr:010x}'.format(**locals()))
  
# Current support only DRAM address
def main():
  print ('Address routing:')
  print ('---------------------------------------')
  print ('Configuration: mcu_mask={mcu_mask:02x} Bank hashing={bank_hashing:01d}'.format(mcu_mask=mcu_mask, bank_hashing=bank_hashing))
  sa = sys.argv[1]
  ma = sa2ma(int(sa, 16))
  print ('system addr: {sa:s} memory addr: {ma:010x}'.format(**locals()))
  mc_addr_inf(ma)

  print ('')
  steer(int(sa, 16))

'''
populated SPD used:
  col bits: 10
  row bits: 16
  bank bits: 4
  rank bits: 1 

31-28 27-24 23-20 19-16 15-12 11-8 7-4 3-0
system address -> mem address
8 MCs:
  2:0        - bytes
  3:7, 11:15 - CAS
  16:19      - BANK
  20         - RANK
  21:36      - ROW (which gets us to 128GB total memory)

1 MC:
  2:0        - bytes
  3:12       - CAS
  13:16      - BANK
  17         - RANK
  18:33      - ROW (which gets us to 16GB total memory)

'''

if __name__ == '__main__':
    main()