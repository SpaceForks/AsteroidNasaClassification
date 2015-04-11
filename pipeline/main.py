'''
take a single scope python script and
attempt to convert it into a luigi Task
'''

import os
import shutil
from termcolor import colored
import time

import importlib

from luigi import six
import luigi

import json

import numpy as np
import pandas as pd

# 2to3 compat warning!!!
from StringIO import StringIO

import matplotlib.pyplot as plt

TMPDIR = '/tmp/blah'
DATA_SOURCE_DIR = os.path.expanduser('~/Dropbox/devsync/dataproc/data/smass_catalog')

METADATA_FILEPATH = os.path.expanduser('~/Dropbox/devsync/dataproc/data/smass_entry_list.json')



class LoadDemeoData(luigi.Task):

    def run(self):
        print(colored('Running Foo', 'cyan'))

    def requires(self):
        print(colored('*** RUNNING REQUIRES ***', 'white', 'on_green'))
        smass_entry_list = json.load(open(METADATA_FILEPATH))
        print(colored('DO RUN!', 'magenta'))
        for n, row in enumerate(smass_entry_list, start=1):
            print row[u'Name']
            for data_entry in row[u'data']:
                for data_file in data_entry[u'files']:
                    if data_file[u'type'].strip().startswith('tabulated'):
                        ## tabulated
                        yield DemeoToPlot(data_file[u'url'])
            break

class DemeoToPlot(luigi.Task):
    filepath = luigi.Parameter()
    
    def resolve_filepath(self, fpath):
        return os.path.join(DATA_SOURCE_DIR, fpath)
    
    def run(self):
        input_data_filepath = self.resolve_filepath(self.filepath)
        with self.output().open('w') as ofile:
            d = pd.read_table(input_data_filepath, sep=r'\s+', header=None, names=['wavelength', 'flux', 'ignore1', 'ignore2'])
            plot = d.plot(kind='scatter', marker='.', x='wavelength', y='flux')
            
            buf = StringIO()

            # cannot write directly to luigi's atomic_file
            plt.savefig(buf, format='png')
            buf.seek(0)
            ofile.write(buf.read())
            
        print('%s -- hello:%s\n' % (input_data_filepath, time.time()))

    def output(self):
        """
        Returns the target output for this task.
        :return: the target output for this task.
        :rtype: object (:py:class:`~luigi.target.Target`)
        """
        ofilepath = '%s/%s.png' % (TMPDIR, self.filepath)
        print(colored('INSIDE DemoToPlot; writing to: %s' % ofilepath, 'green'))
        return luigi.LocalTarget(ofilepath)


if __name__ == "__main__":
    if os.path.exists(TMPDIR): shutil.rmtree(TMPDIR)

    # if you have `luigid` running
    # luigi.run(['--task', 'Foo',], use_optparse=True)
    
    # or, without a central scheduler:
    luigi.run(['--task', 'LoadDemeoData', '--local-scheduler',], use_optparse=True)

    # or, specify everything from CLI, in which you should run it with something like
    # python main.py --local-scheduler Foo
    # luigi.run()
