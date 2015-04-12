'''
        example call: python %s -d ~/Dropbox/devsync/dataproc/data/smass_catalog/data
        example call: python pypeline_spectra.py -p EAR_A_DBP_3_RDR_24COLOR_V2_1

        runs workflow on the dir
'''% __file__

from common import *
from lib.parse_24color import parse_label_string as parse_pds3_24color_label_string 
from StringIO import StringIO

class Classifier1Task(SingleIOTask):
    def _run_interface(self, runtime):
        
        d = Classifier1.clean_data(Classifier1.smass_text_file_to_dataframe(self.inputs.filepath))
        res = Classifier1.classify(d.wavelength, d.flux)
        
        self._output_filepath = os.path.join(os.getcwd(), 'output.json')
        with open(self._output_filepath, 'w') as ofile:
            ofile.write(json.dumps(res))
        return runtime


from lib import SMASS
import matplotlib.pyplot as plt

class PlotCurveTask(SingleIOTask):
    def _run_interface(self, runtime):
        d = SMASS.smass_text_file_to_dataframe(self.inputs.filepath)
        plot = d.plot(kind='scatter', marker='.', x='wavelength', y='flux')

        self._output_filepath = os.path.join(os.getcwd(), 'output.png')
        plt.savefig(self._output_filepath)
        return runtime



class PDS324OutputSpec(TraitedSpec):
    csv_filepath = traits.File()
    json_filepath = traits.File()
    
class PDS324ColorConversionTask(BaseInterface):
    input_spec = SimpleFileInputSpec
    output_spec = PDS324OutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        for trait_name in outputs.keys():
            outputs[trait_name] = getattr(self, '_%s'%trait_name)
        return outputs
    
    def _run_interface(self, runtime):
        dlbl = parse_pds3_24color_label_string(open(self.inputs.filepath).read())
        
        tab_filepath = pjoin(psplit(self.inputs.filepath)[0], dlbl['^TABLE'].strip('"'))
        sio = StringIO(open(tab_filepath).read())
        tab = pd.read_table(sio, sep='\s+', header=None)
        sio.close()
        
        ncol = int(dlbl['TABLE'][0]['COLUMNS'])
        tab.columns = [col['NAME'].strip('"') for col in dlbl['TABLE'][0]['COLUMN']]
        
        self._json_filepath = os.path.join(os.getcwd(), 'output.json')
        # with open(self._json_filepath, 'w') as ofile:
        #     ofile.write(json.dumps(out))
        
        self._csv_filepath = os.path.join(os.getcwd(), 'output.csv')
        tab.to_csv(self._csv_filepath, index=False)
        return runtime




if __name__ == '__main__':

    ### recursively retrieve the smass_catalog data files
    from glob import glob
    import os
    import fnmatch
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='where to search for smass files')
    parser.add_argument('-p', '--pds3_24color', help='PDS3 24 color extracted directory')
    args = parser.parse_args()

    wf = pe.Workflow(name='spectra_workflow')
    wf.config['execution']['crashdump_dir'] = 'crashdump'
    # change me
    wf.base_dir = '/tmp/wf-asteroid'
    
    nDataSink = pe.Node(interface=nio.DataSink(parameterization=False), name='datasink')
    nDataSink.inputs.base_directory = '/tmp/asteroid-datasink'


    if args.directory and os.path.exists(args.directory):

        BASE_DIR = os.path.expanduser(args.directory)

        file_list = [os.path.join(dirpath, f)
                     for dirpath, dirnames, files in os.walk(BASE_DIR)
                     for f in fnmatch.filter(files, '*.txt')]

        ### interpolation is broken now. run with subset
        file_list = file_list[12:13]

        nInputFileList = pe.Node(interface = util.IdentityInterface(fields = ['input_filepath']), name = 'input_file_list')
        nInputFileList.iterables = ('input_filepath', file_list)

        nClassifier1Task = pe.Node(interface = Classifier1Task(), name='classifier_1')
        nPlotCurveTask = pe.Node(interface = PlotCurveTask(), name='curveplotter_1')

        wf.connect([
            # (nInputFileList, NodePrinter.create(), [('input_filepath', 'input')]),
            (nInputFileList, nClassifier1Task, [('input_filepath', 'filepath')]),
            (nInputFileList, nPlotCurveTask, [('input_filepath', 'filepath')]),
            # (nClassifier1Task, NodePrinter.create(), [('filepath', 'input')]),

            (nClassifier1Task, nDataSink, [('filepath', 'result')]),
            ])


    elif args.pds3_24color:

        file_list = glob(pjoin(args.pds3_24color, 'data', 'data4', '*.lbl'))
        file_list = file_list[:3]
        nInputFileList = pe.Node(interface = util.IdentityInterface(fields = ['input_filepath']), name = 'input_file_list')
        nInputFileList.iterables = ('input_filepath', file_list)

        nPDS324ColorConversionTask = pe.Node(interface = PDS324ColorConversionTask(), name='pds3_24color_conversion')

        # substitutions for datasink
        def make_substitution(input_filepath):
            import os.path as p
            filename_root = p.splitext(p.split(input_filepath)[1])[0]
            return [('output', p.join('PDS3_24COLOR', filename_root))]
        wf.connect([
            (nInputFileList, nPDS324ColorConversionTask, [('input_filepath', 'filepath')]),
            (nInputFileList, nDataSink, [(("input_filepath", make_substitution), "substitutions")]),

            (nPDS324ColorConversionTask, nDataSink, [('csv_filepath', 'csv')]),
            ])
    
    wf.write_graph()
    res = wf.run()


