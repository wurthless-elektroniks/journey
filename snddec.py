'''
Decode 1-bit PCM to 8-bit PCM
First two bytes are big-endian length of sound, followed by the sound in 1 bit PCM
'''

from argparse import ArgumentParser,RawTextHelpFormatter

def _init_argparser():
    argparser = ArgumentParser(formatter_class=RawTextHelpFormatter,
                               prog='snddec')
    
    argparser.add_argument("sndfile_in",
                           nargs='?',
                           help="Input 1-bit sound file (S.1, S.2, etc.)")
  
    argparser.add_argument("pcm_out",
                           nargs='?',
                           help="Output unsigned 8-bit PCM file")
    
    return argparser

def _convert_1bit_to_8bit(pcm: bytes):
    # assuming we skipped past the 2 byte header
    output = bytearray([])
    for b in pcm:
        for i in range(8):
            # speakerbits are read right to left
            output.append( 0xFF if (b >> i) & 1 != 0 else 0)

    return output

def main():
    argparser = _init_argparser()
    args = argparser.parse_args()

    if args.sndfile_in is None or args.pcm_out is None:
        print("must specify sound input and output files")
        return
    
    with open(args.sndfile_in, "rb") as f:
        f.seek(2, 0)
        pcm_out = _convert_1bit_to_8bit(f.read())
    
    with open(args.pcm_out, "wb") as f:
        f.write(pcm_out)

if __name__ == "__main__":
    main()
