import os
import jdcal
import datetime

def str_to_float_or_None(s):
    '''
    if empty string, return None, else float
    '''
    if len(s) is 0:
        return None
    else:
        return float(s)

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
                jyear = int(julian_date[:2])*10e4
                jday = float(julian_date[2:])
                year, month, day, secfrac = jdcal.jd2gcal(jyear, jday)
                date = datetime.datetime(year, month, day) + datetime.timedelta(0, secfrac*86400)
                buf.append([str(date), float(magnitude),
                            str_to_float_or_None(error_margin),
                            str_to_float_or_None(airmass),
                            ])
            else:
                raise Exception('unknown state %s! typo?' % (state))
    return output


if __name__ == '__main__':

    import sys
    import argparse
    from glob import glob
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='a directory or a text file')
    parser.add_argument('-o', '--output', help='a directory to output to, or -json, to print json to stdout')
    parser.add_argument('-t', '--type', help='output type: json or csv', default='csv')
    
    args = parser.parse_args()

    if any([args.input is None, args.output is None]):
        parser.print_help()

        print('''\
        example call: python parse_ALCDEF.py -i path/to/ALCDEF -o path/to/outputdir -t csv

        converts all files in path/to/ALCDEF to csv, and puts them in path/to/outputdir
''')
        sys.exit()

    if args.type == 'csv':
        import pandas as pd

    from os.path import join as pjoin, exists as pexists, split as psplit, splitext as psplitext
    if not pexists(args.output):
        os.mkdir(args.output)

    if args.input.endswith('.txt'):
        out = parse_file(args.input)
    elif pexists(args.input) and os.path.isdir(args.input):
        for input_filepath in glob(pjoin(args.input, '*.txt')):
            out = parse_file(input_filepath)
            filename = psplitext(psplit(input_filepath)[-1])[0]
            
            if   args.type == 'csv':
                output_filepath = pjoin(args.output, filename + '.csv')
                concat = []
                for entry in out:
                    df = pd.DataFrame(entry['data'], columns=['date', 'magnitude', 'error_margin', 'airmass'])
                    concat.append(df)
                
                df_out = pd.concat(concat)
                df_out.to_csv(output_filepath, index=False)
                print('wrote: %s' % output_filepath)
            elif args.type == 'json':
                output_filepath = pjoin(args.output, filename + '.json')
                with open(output_filepath, 'w') as ofile:
                    ofile.write(json.dumps(out))
                print('wrote: %s' % output_filepath)
            

