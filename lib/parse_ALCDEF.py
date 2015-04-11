import os
import jdcal
from glob import glob

def parse_file(input_filepath):
    output = []
    with open(input_filepath) as ifile:
        buf = []
        d = {}
        
        state = None
        for line in [ln.strip() for ln in ifile.readlines()]:
            if   line.startswith('STARTMETADATA'):
                state = 'METADATA'
                continue
            elif line.startswith('ENDMETADATA'):
                state = 'DATA'
                continue
            elif line.startswith('ENDDATA'):
                state = None
                d['data'] = buf
                output.append(d)
                d = {}
                buf = []
                continue
            
            if   state == 'METADATA':
                key, val = line.split('=', 1)
                d[key] = val
            elif state == 'DATA':
                julian_date, magnitude, error_margin, airmass = line.split('=')[1].split('|')
                year = int(julian_date[:2])*10e4
                day = float(julian_date[2:])
                buf.append([jdcal.jd2gcal(year, day), float(magnitude), float(error_margin), float(airmass)])
            else:
                raise Exception('unknown state! typo?')


if __name__ == '__main__':
    filepath = '/tmp/ALCDEF/ALCDEF_100085_1992UY4_20150407_221242.txt'
    out = parse_file(filepath)


    import sys
    if '-json' in sys.argv:
        import json
        print json.dumps(out)
