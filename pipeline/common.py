import os
from os.path import splitext as psplitext

from nipype.interfaces.traits_extension import traits # , File
from nipype.interfaces.base import (
    TraitedSpec, BaseInterface,
    CommandLineInputSpec, CommandLine,
)
import nipype.pipeline.engine as pe
from nipype.interfaces import utility as util

import nipype.interfaces.io as nio  

import sys
# HACK
sys.path.append('..')

import json
from lib import classify_curve as Classifier1

from termcolor import colored


### UTILITY
class NodePrinterInputSpec(TraitedSpec):
    input = traits.Any() #List()
class NodePrinterOutputSpec(TraitedSpec):
    output = traits.Any() #List()

class NodePrinter(BaseInterface):
    input_spec = NodePrinterInputSpec
    output_spec = NodePrinterOutputSpec
    _NODEPRINTER_COUNT = 0

    def _run_interface(self, runtime):
        print(colored("==========> PRINTER", "white", "on_red"))
        print(colored("%s\n" % self.inputs.input, "white", "on_blue"))
        runtime.returncode = 0
        return runtime

    def __init__(self, **inputs):
        super(NodePrinter, self).__init__(**inputs)
        self.__class__._NODEPRINTER_COUNT += 1

    def _list_outputs(self):
        try:
            print("input length: %s" % len(self.inputs.input))
        except TypeError:
            pass
        outputs = self.output_spec().get()
        outputs['output'] = self.inputs.input
        return outputs
    @staticmethod
    def create():
        return pe.Node(name = "NodePrinter%s" % NodePrinter._NODEPRINTER_COUNT, interface = NodePrinter(), overwrite = True)




### operational nodes
class SimpleFileInputSpec(TraitedSpec):                                                                                                 
    filepath = traits.File(mandatory = True)
class SimpleFileOutputSpec(TraitedSpec):
    filepath = traits.File()

class SingleIOTask(BaseInterface):
    input_spec = SimpleFileInputSpec
    output_spec = SimpleFileOutputSpec
    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['filepath'] = self._output_filepath
        return outputs

