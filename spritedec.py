
#
# bmp code stolen from https://stackoverflow.com/questions/8729459/how-do-i-create-a-bmp-file-with-pure-python
#

import struct
from bitbuffer import BufferBitstreamReader, BitstreamReadOrder

class Bitmap():
    def __init__(s, width, height):
        s._bfType = 19778 # Bitmap signature
        s._bfReserved1 = 0
        s._bfReserved2 = 0
        s._bcPlanes = 1
        s._bcSize = 12
        s._bcBitCount = 24
        s._bfOffBits = 26
        s._bcWidth = width
        s._bcHeight = height
        s._bfSize = 26+s._bcWidth*3*s._bcHeight
        s.clear()


    def clear(s):
        s._graphics = [(0,0,0)]*s._bcWidth*s._bcHeight


    def setPixel(s, x, y, color):
        if isinstance(color, tuple):
            if x<0 or y<0 or x>s._bcWidth-1 or y>s._bcHeight-1:
                raise ValueError('Coords out of range')
            if len(color) != 3:
                raise ValueError('Color must be a tuple of 3 elems')
            s._graphics[y*s._bcWidth+x] = (color[2], color[1], color[0])
        else:
            raise ValueError('Color must be a tuple of 3 elems')


    def write(s, file):
        with open(file, 'wb') as f:
            f.write(struct.pack('<HLHHL', 
                        s._bfType, 
                        s._bfSize, 
                        s._bfReserved1, 
                        s._bfReserved2, 
                        s._bfOffBits)) # Writing BITMAPFILEHEADER
            f.write(struct.pack('<LHHHH', 
                        s._bcSize, 
                        s._bcWidth, 
                        s._bcHeight, 
                        s._bcPlanes, 
                        s._bcBitCount)) # Writing BITMAPINFO
            for px in s._graphics:
                f.write(struct.pack('<BBB', *px))
            for i in range((4 - ((s._bcWidth*3) % 4)) % 4):
                f.write(struct.pack('B', 0))

#
# this bit's original
#

def _read16be(file_handle):
    return struct.unpack(">H", file_handle.read(2))[0]

def _bitplane_to_matrix(bitplane: bytes,
                        bytes_per_line: int,
                        y_pixels: int):

    lines = []

    bitbuffer = BufferBitstreamReader(bitplane, BitstreamReadOrder.L_TO_R)

    for _ in range(y_pixels):
        line = []
        for __ in range(bytes_per_line * 8):
            line.append(bitbuffer.read_bit())
        lines.append(line)

    return lines
    

BLACK = (0,0,0)
WHITE = (255,255,255)

# https://en.wikipedia.org/wiki/Enhanced_Graphics_Adapter
EGA_COLORS = [
    (0x00, 0x00, 0x00), # 0
    (0x00, 0x00, 0xAA), # 1
    (0x00, 0xAA, 0x00), # 2
    (0x00, 0xAA, 0xAA), # 3
    (0xAA, 0x00, 0x00), # 4
    (0xAA, 0x00, 0xAA), # 5
    (0xAA, 0x55, 0x00), # 6
    (0xAA, 0xAA, 0xAA), # 7
    (0x55, 0x55, 0x55), # 8
    (0x55, 0x55, 0xFF), # 9
    (0x55, 0xFF, 0x55), # A
    (0x55, 0xFF, 0xFF), # B
    (0xFF, 0x55, 0x55), # C
    (0xFF, 0x55, 0xFF), # D
    (0xFF, 0xFF, 0x55), # E
    (0xFF, 0xFF, 0xFF), # F
]

def _decode_spritesheet(file_handle):
    num_sprites = _read16be(file_handle)

    for i in range(num_sprites):
        print(f"sprite loc: {file_handle.tell():04x}")
        x_pixels = _read16be(file_handle)
        y_pixels = _read16be(file_handle)
        c = _read16be(file_handle)

        print(f"sprite {i}: {x_pixels}x{y_pixels}")

        bytes_per_line = (x_pixels >> 3) + (1 if (x_pixels & 7) != 0 else 0)

        # number of bytes to read
        bitplane_size = bytes_per_line * y_pixels

        # read the bitplanes
        plane_a = bytearray(file_handle.read(bitplane_size))
        plane_b = bytearray(file_handle.read(bitplane_size))
        plane_c = bytearray(file_handle.read(bitplane_size))
        plane_d = bytearray(file_handle.read(bitplane_size))
        plane_e = bytearray(file_handle.read(bitplane_size))

        # decode to matrices in the order the game does
        matrices = [
            _bitplane_to_matrix(plane_e, (bytes_per_line*8), bytes_per_line, y_pixels), # alpha
            _bitplane_to_matrix(plane_a, (bytes_per_line*8), bytes_per_line, y_pixels), 
            _bitplane_to_matrix(plane_b, (bytes_per_line*8), bytes_per_line, y_pixels), 
            _bitplane_to_matrix(plane_c, (bytes_per_line*8), bytes_per_line, y_pixels), 
            _bitplane_to_matrix(plane_d, (bytes_per_line*8), bytes_per_line, y_pixels), 
        ]

        pixels_bmp = Bitmap((bytes_per_line*8), y_pixels)
        alpha_bmp  = Bitmap((bytes_per_line*8), y_pixels)
        for y in range(y_pixels):
            for x in range(x_pixels ):
                pixel = (matrices[1][y][x] << 0) | \
                        (matrices[2][y][x] << 1) | \
                        (matrices[3][y][x] << 2) | \
                        (matrices[4][y][x] << 3)
                
                color = EGA_COLORS[pixel]
                mask  = WHITE if matrices[0][y][x] != 0 else BLACK
                pixels_bmp.setPixel(x, (y_pixels-1)-y, color)
                alpha_bmp.setPixel(x, (y_pixels-1)-y, mask)

        pixels_bmp.write(f"private/spritesheet_{i}_pixels.bmp")
        alpha_bmp.write(f"private/spritesheet_{i}_alpha.bmp")
