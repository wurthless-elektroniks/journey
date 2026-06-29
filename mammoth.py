'''
Journey to the Center of the Mammoth

1. Put JOURNEY.EXE in private/
2. Run script
3. MAMMOTH.EXE will be produced
4. Put MAMMOTH.EXE in the Journey to the Center of the Earth folder
5. Run MAMMOTH.EXE in DOSBox
6. Enjoy
'''

import hashlib

# x86 instruction: callf to mammoth minigame
CALLF_MAMMOTH_MINIGAME      = bytes([0x9a, 0xcf, 0x0b, 0x9c, 0x08])

# callfs to other minigames - find and replace
CALLF_PTERODACTYLS_MINIGAME = bytes([0x9a, 0x05, 0x00, 0xf5, 0x0c])
CALLF_ROCKFALL_MINIGAME     = bytes([0x9a, 0xa1, 0x03, 0x8a, 0x06])
CALLF_CROCS_MINIGAME        = bytes([0x9a, 0x06, 0x00, 0x7a, 0x0d])

# calls play_sound with params 0x0b, 0x0e (alarm ticking noise)
# nop this sequence out for more optimal snoring
ALARMCLOCK_TICK = bytes([
    0xb8, 0x0e, 0x00,
    0x50,
    0xb8, 0x0b, 0x00,
    0x50,
    0x9a, 0x02, 0x00, 0x45, 0x00,
    0x83, 0xc4, 0x04
])

RANDOM_INJURY_PATTERN = bytes([
    0x80, 0x7e, 0xff, 0x00,
    0x75, 0x53,
    0x9a, 0x3c, # start of callf to random injury function
])

RANDOM_INJURY_STARTS_ROCKFALL_INSTEAD  = bytes([
    0x80, 0x7e, 0xff, 0x00,
    0x75, 0x53,
    0xeb, 0xb6, # jump up to run rockfall function instead (which should be patched to run mammoths)
])

def patch(exe, original, replaced):
    exe_before = exe
    exe = exe.replace(original, replaced)
    if exe_before == exe:
        raise RuntimeError("patch failed?")
    return exe


with open("private/JOURNEY.EXE", "rb") as f:
    exe = f.read()

for pattern in [ CALLF_PTERODACTYLS_MINIGAME, CALLF_ROCKFALL_MINIGAME, CALLF_CROCS_MINIGAME ]:
    exe = patch(exe, pattern, CALLF_MAMMOTH_MINIGAME)
    
# NOP these out
for pattern in [ ALARMCLOCK_TICK ]:
    exe = patch(exe, pattern, bytes([0x90] * len(pattern)))
    
exe = patch(exe, RANDOM_INJURY_PATTERN, RANDOM_INJURY_STARTS_ROCKFALL_INSTEAD)

# if True to cheat. should at least allow you to get through to the end
if False:
    PLAYER_DEAD_PATTERN = bytes([0x83, 0x3e, 0x8c, 0x69, 0x00, 0x7f, 0x03])
    PATCHED             = bytes([0x83, 0x3e, 0x8c, 0x69, 0x00, 0xeb, 0x03])
    exe = exe.replace(PLAYER_DEAD_PATTERN, PATCHED)

with open("private/MAMMOTH.EXE", "wb") as f:
    f.write(exe)
