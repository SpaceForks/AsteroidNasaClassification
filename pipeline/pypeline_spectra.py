from common import *

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




if __name__ == '__main__':

    ### recursively retrieve the smass_catalog data files
    from glob import glob
    import os
    import fnmatch
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='where to search for smass files')
    args = parser.parse_args()

    if not args.directory or not os.path.exists(args.directory):
        parser.print_help()

        print('''
        example call: python %s -d ~/Dropbox/devsync/dataproc/data/smass_catalog/data

        runs workflow on the dir
        '''% __file__)
        sys.exit()

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
    
    nDataSink = pe.Node(interface=nio.DataSink(), name='datasink')
    nDataSink.inputs.base_directory = '/tmp/asteroid-datasink'
    
    wf = pe.Workflow(name='spectra_workflow')
    wf.config['execution']['crashdump_dir'] = 'crashdump'
    # change me
    wf.base_dir = '/tmp/wf-asteroid'
    
    wf.connect([
        # (nInputFileList, NodePrinter.create(), [('input_filepath', 'input')]),
        (nInputFileList, nClassifier1Task, [('input_filepath', 'filepath')]),
        (nInputFileList, nPlotCurveTask, [('input_filepath', 'filepath')]),
        # (nClassifier1Task, NodePrinter.create(), [('filepath', 'input')]),
        
        (nClassifier1Task, nDataSink, [('filepath', 'result')]),
        ])
    wf.write_graph()
    res = wf.run()


