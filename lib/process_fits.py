# pip install pyfits

import sys
import bz2
import pyfits
from os.path import splitext as psplitext

if __name__ == '__main__':
    input_filepath = sys.argv[-1] # e.g. 'frame-g-004570-4-0135.fits.bz2'
    output_filepath = psplitext(input_filepath)[0]

    bz2_file = bz2.BZ2File(input_filepath, 'rb')
    try:
        data = bz2_file.read()
        with open(output_filepath, 'wb') as ofile:
            ofile.write(data)
    finally:
        bz2_file.close()

    hdulist = pyfits.open(output_filepath)

