'''
        example call: python pypeline_lightcurve.py -p ALCDEF

        runs workflow on the dir... generates csv
'''
from common import *
from lib.parse_ALCDEF import parse_file as parse_ALCDEF_file

from StringIO import StringIO

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
    import os
    from os.path import join as pjoin
    
    # preprocessing: read various lightcurve data, output unified structures (csv)
    wf_preproc = pe.Workflow(name='lightcurve_workflow')
    wf_preproc.config['execution']['crashdump_dir'] = 'crashdump'
    # change me
    wf_preproc.base_dir = '/tmp/wf-asteroid'
    
    nDataSink = pe.Node(interface=nio.DataSink(parameterization=False), name='datasink')
    nDataSink.inputs.base_directory = '/tmp/asteroid-datasink'

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--alcdef', help='the ALCDEF zipfile or its extracted directory')
    args = parser.parse_args()
    
    if args.alcdef:
        if os.path.isdir(args.alcdef):
            file_list = glob(pjoin(args.alcdef, '*.txt'))[:10]
        elif args.alcdef.endswith('.zip'):
            import tempfile
            import zipfile
            import tempfile
            import os
            from os.path import join as pjoin

            output_dir = tempfile.mkdtemp()
            print('zip file given. inflating to %s...' % (output_dir))

            zf = zipfile.ZipFile(args.alcdef, 'r')
            file_list = []
            for info in zf.infolist():
                output_filepath = output_dir + info.filename
                with open(output_filepath, 'wb') as ofile:
                    ofile.write(zf.read(info.filename))
                file_list.append(output_filepath)
    
        print('{} files found.'.format(len(file_list)))

        nInputFileList = pe.Node(interface = util.IdentityInterface(fields = ['input_filepath']), name = 'input_file_list')
        nInputFileList.iterables = ('input_filepath', file_list)

        nALCDEFConversion = pe.Node(interface = ALCDEFConversionTask(), name='alcdef_conversion')

        # substitutions for datasink
        def make_substitution(input_filepath):
            import os.path as p
            filename_root = p.splitext(p.split(input_filepath)[1])[0]
            return [("output", p.join('ALCDEF', filename_root))]

        wf_preproc.connect([
            (nInputFileList, nALCDEFConversion, [('input_filepath', 'filepath')]),
            (nInputFileList, nDataSink, [(("input_filepath", make_substitution), "substitutions")]),

            # (nALCDEFConversion, nDataSink, [('json_filepath', 'json')]),
            (nALCDEFConversion, nDataSink, [('csv_filepath', 'csv')]),
            ])

    wf_preproc.connect([
        (nInputFileList, NodePrinter.create(), [('input_filepath', 'input')]),
        ])

    wf_preproc.write_graph()
    res = wf_preproc.run()


