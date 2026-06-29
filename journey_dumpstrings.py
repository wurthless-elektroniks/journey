'''
String dumper

11d3:055a is the main "print string" function.
This script dumps the strings by ID in that table for easy reference.
'''

import struct

def extract_cstring(data: bytes):
    str = bytearray(data.partition(b'\x00')[0])
    
    for i, c in enumerate(str):
        if c >= 0x80:
            str[i] = 0x20
    
    return str.decode('ascii')

with open("private/JOURNEY.EXE", "rb") as f:
    f.seek(0x124A0, 0)

    segment = f.read(0x10000)

    for i in range(0x100):
        offset = 0x00CC + (i*4)

        lo16, hi16 = struct.unpack("<HH", segment[offset:offset+4])
        if hi16 != 0x10CA:
            break
        
        strout = extract_cstring(segment[lo16:])

        print(f"{i:04x} - {strout}")
