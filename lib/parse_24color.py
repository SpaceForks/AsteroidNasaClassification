'''
ad-hoc parser for PDS3
specifically those from http://sbn.psi.edu/pds/resource/24color.html

example usage:
python parse_24color.py EAR_A_DBP_3_RDR_24COLOR_V2_1
'''
import sys

from glob import glob
from os.path import join as pjoin, split as psplit, splitext as psplitext
import pandas as pd
from StringIO import StringIO

# pip install ply astropy
# pip install https://github.com/mkelley/pds3/archive/v0.1.0.zip
# import pds3
# pds3.read_label(filepath) ...
# does not actually parse successfully this dataset! so we go ad-hoc :-(

import re
p_indent = re.compile('^\s+')

def get_indent_level(line):
    m = p_indent.match(line)
    return m and len(m.group(0)) or 0

def parse_line(line):
    spl = [part.strip() for part in line.split('=', 1)]
    key = spl[0]
    return key, len(spl) > 1 and spl[1] or None

def parse_label_string(text):
    rtn = {}

    idx = 0
    line_list = text.splitlines()
    lastkey = None
    while idx < len(line_list):
        line = line_list[idx]
        idx += 1
        if not line.strip(): continue
        key, val = parse_line(line)

        if   key == 'END':
            pass
        elif key == 'OBJECT':
            indent_level = get_indent_level(line)
            
            subbuf = []
            while idx < len(line_list):
                idx += 1
                subline = line_list[idx]
                subkey, subval = parse_line(subline)
                if (subval == val and subkey == 'END_OBJECT') \
                      or subkey == 'END':
                    break
                else:
                    subbuf.append(subline)
            dd = parse_label_string('\n'.join(subbuf))
            if val not in rtn:
                rtn[val] = []
            rtn[val].append(dd)
            
        else:
            if '=' in line:
                rtn[key] = val
                lastkey = key
            else:
                rtn[lastkey] += line.strip()
    return rtn
    

if __name__ == '__main__':
    DATA_DIR = sys.argv[-1]

    for lbl_filepath in glob(pjoin(DATA_DIR, 'data', 'data4', '*.lbl')):

        dlbl = parse_label_string(open(lbl_filepath).read())

        tab_filepath = pjoin(psplit(lbl_filepath)[0], dlbl['^TABLE'].strip('"'))
        sio = StringIO(open(tab_filepath).read())
        tab = pd.read_table(sio, sep='\s+', header=None)
        sio.close()

        ncol = int(dlbl['TABLE'][0]['COLUMNS'])
        tab.columns = [col['NAME'].strip('"') for col in dlbl['TABLE'][0]['COLUMN']]

        print tab.head()
        break
