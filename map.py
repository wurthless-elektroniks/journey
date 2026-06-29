
#
# bmp code stolen from https://stackoverflow.com/questions/8729459/how-do-i-create-a-bmp-file-with-pure-python
#

from struct import pack

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
      f.write(pack('<HLHHL', 
                   s._bfType, 
                   s._bfSize, 
                   s._bfReserved1, 
                   s._bfReserved2, 
                   s._bfOffBits)) # Writing BITMAPFILEHEADER
      f.write(pack('<LHHHH', 
                   s._bcSize, 
                   s._bcWidth, 
                   s._bcHeight, 
                   s._bcPlanes, 
                   s._bcBitCount)) # Writing BITMAPINFO
      for px in s._graphics:
        f.write(pack('<BBB', *px))
      for i in range((4 - ((s._bcWidth*3) % 4)) % 4):
        f.write(pack('B', 0))

#
# this bit's original
#

BLOCKER_COLOR = (0,0,0)
NEUTRAL_COLOR = (255, 255, 255)
DANGER_COLOR  = (255, 0, 0)
OCEAN_COLOR   = (0,0,255)
RUINS_COLOR   = (255,128,128)
BONES_COLOR   = (128,128,128)
SHROOMS_COLOR = (255,255,0)

STORM_COLOR   = (128,0,0)

WARPPOINT_COLOR = (0,255,0)

MAINMAP_COLORS = {
    0x0: NEUTRAL_COLOR,
    0x1: BLOCKER_COLOR,
    0x2: BLOCKER_COLOR,
    0x3: BLOCKER_COLOR, 
    0x4: OCEAN_COLOR,
    0x5: DANGER_COLOR,
    0x6: NEUTRAL_COLOR,
    0x7: NEUTRAL_COLOR,
    0x8: RUINS_COLOR,
    0x9: NEUTRAL_COLOR,
    0xA: BONES_COLOR,
    0xB: NEUTRAL_COLOR,
    0xC: DANGER_COLOR,
    0xD: DANGER_COLOR,
    0xE: SHROOMS_COLOR,
    0xF: NEUTRAL_COLOR,
}

LAKEMAP_COLORS = {
    0x0: NEUTRAL_COLOR,
    0x1: BLOCKER_COLOR,
    0x2: NEUTRAL_COLOR,
    0x3: RUINS_COLOR,   # because we're about to be there!
    0x4: STORM_COLOR,
    0x5: NEUTRAL_COLOR,
    0x6: OCEAN_COLOR,
    0x7: NEUTRAL_COLOR,
    0x8: NEUTRAL_COLOR,
    0x9: NEUTRAL_COLOR,
    0xA: NEUTRAL_COLOR,
    0xB: NEUTRAL_COLOR,
    0xC: NEUTRAL_COLOR,
    0xD: NEUTRAL_COLOR,
    0xE: NEUTRAL_COLOR,
    0xF: DANGER_COLOR, # crocodile minigame
}

MAIN_WARP_LOCATIONS = [
  (0x0B, 0x16), # starting position
  (0x0F, 0x2D), # after shrooms
  (0x2F, 0x31), # after bonezone
  (0x58, 0x32), # after lake
]

# x @ 0x692a, y @ 0x685e
LAKE_WARP_LOCATIONS = [
  (0x35 >> 1, 0x46 >> 1), # starting position
  (0x87 >> 1, 0x3C >> 1), # after geyser
]

with open("private/JOURNEY.EXE", "rb") as f:
    f.seek(0x16BFC, 0)
    gamemap = f.read(112 * 68)

    gamemap_bmp = Bitmap(112, 68)
    lakemap_bmp = Bitmap(112, 68)

    for y in range(68):
        for x in range(112):
            gamemap_cell = (gamemap[(y*112)+x] >> 4)
            gamemap_bmp.setPixel(x,67-y,MAINMAP_COLORS[gamemap_cell])

            lakemap_cell = (gamemap[(y*112)+x] & 0xF)
            lakemap_bmp.setPixel(x,67-y,LAKEMAP_COLORS[lakemap_cell])
  

    for x,y in MAIN_WARP_LOCATIONS:
      gamemap_bmp.setPixel(x,67-y,WARPPOINT_COLOR)

    for x,y in LAKE_WARP_LOCATIONS:
      lakemap_bmp.setPixel(x,67-y,WARPPOINT_COLOR)


    gamemap_bmp.write("gamemap.bmp")
    lakemap_bmp.write("lakemap.bmp")
