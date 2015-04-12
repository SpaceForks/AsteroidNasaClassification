from common import *
from lib.parse_ALCDEF import parse_file as parse_ALCDEF_file

import pandas as pd
import json

class ALCDEFOutputSpec(TraitedSpec):
    csv_filepath = traits.File()
    json_filepath = traits.File()
    
class ALCDEFConversionTask(BaseInterface):
    input_spec = SimpleFileInputSpec
    output_spec = ALCDEFOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['json_filepath'] = self._json_filepath
        outputs['csv_filepath'] = self._csv_filepath
        return outputs

    def _run_interface(self, runtime):
        out = parse_ALCDEF_file(self.inputs.filepath)
                
        self._json_filepath = os.path.join(os.getcwd(), 'output.json')
        with open(self._json_filepath, 'w') as ofile:
            ofile.write(json.dumps(out))

        self._csv_filepath = os.path.join(os.getcwd(), 'output.csv')
        concat = []
        for entry in out:
            df = pd.DataFrame(entry['data'],
                              columns=['date', 'magnitude', 'error_margin', 'airmass'])
            concat.append(df)
        df_out = pd.concat(concat)
        df_out.to_csv(self._csv_filepath, index=False)
                
        return runtime


if __name__ == '__main__':

    import argparse
    from glob import glob
    from os.path import join as pjoin
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='the lightcurve extracted directory')
    args = parser.parse_args()

    if not args.directory or not os.path.exists(args.directory):
        parser.print_help()

        print('''
        example call: python %s -d path/to/ALCDEF

        runs workflow on the dir
        '''% __file__)
        sys.exit()

    file_list = glob(pjoin(args.directory, '*.txt'))[:10]
    
    nInputFileList = pe.Node(interface = util.IdentityInterface(fields = ['input_filepath']), name = 'input_file_list')
    nInputFileList.iterables = ('input_filepath', file_list)
    
    nALCDEFConversion = pe.Node(interface = ALCDEFConversionTask(), name='alcdef_conversion')
    
    nDataSink = pe.Node(interface=nio.DataSink(parameterization=False), name='datasink')
    nDataSink.inputs.base_directory = '/tmp/asteroid-datasink'
    
    wf = pe.Workflow(name='lightcurve_workflow')
    wf.config['execution']['crashdump_dir'] = 'crashdump'
    # change me
    wf.base_dir = '/tmp/wf-asteroid'
    
    # substitutions for datasink
    def make_substitution(input_filepath):
        import os.path as p
        filename_root = p.splitext(p.split(input_filepath)[1])[0]
        return [("output", filename_root)]

    wf.connect([
        (nInputFileList, nALCDEFConversion, [('input_filepath', 'filepath')]),
        (nALCDEFConversion, NodePrinter.create(), [('json_filepath', 'input')]),
        (nALCDEFConversion, NodePrinter.create(), [('csv_filepath', 'input')]),

        (nInputFileList, nDataSink, [(("input_filepath", make_substitution), "substitutions")]),
        
        (nALCDEFConversion, nDataSink, [('json_filepath', 'json')]),
        (nALCDEFConversion, nDataSink, [('csv_filepath', 'csv')]),
        ])
    wf.write_graph()
    res = wf.run()


