import copy
import os
from abc import abstractmethod
from multiprocessing import Pool, cpu_count

import numpy as np

from optimeed.core import Option_class, Option_int
from optimeed.core.collection import ListDataStruct, AutosaveStruct
from optimeed.core.tools import getPath_workspace, rsetattr, rgetattr


class Parametric_Collection(ListDataStruct):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def __str__(self):
    #     return super().__str__() +\
    #            text_format.DARKCYAN + '\nSWEEP PARAMETER:\n' + text_format.END +\
    #            indentParagraph(str(self.analysed_attribute), 1) +\
    #            text_format.DARKCYAN + '\nBASE DATA:\n' + text_format.END + indentParagraph(str(self.reference_data), 1)

    @staticmethod
    def get_extension():
        return '.colp'


class Parametric_parameter:
    """Abstract class for a parametric parameter"""

    def __init__(self, analyzed_attribute, reference_device):
        """
        :param analyzed_attribute: Analyzed attribute of the device
        :param reference_device: reference device
        """
        self.analyzed_attribute = analyzed_attribute
        self.reference_device = reference_device

    @abstractmethod
    def get_values(self):
        pass

    def get_reference_device(self):
        return self.reference_device

    def get_analyzed_attribute(self):
        return self.analyzed_attribute


class Parametric_minmax(Parametric_parameter):
    def __init__(self, analyzed_attribute, reference_device, minValue, maxValue, is_relative=False, npoints=10):
        """
        Parametric between boundaries min and max.
        :param minValue: Minimum value to use
        :param maxValue: Maximum value to use
        :param is_relative: if values are relative: multiplication factor based on current reference attribute value
        :param npoints: number of points to evaluate between range
        """
        super().__init__(analyzed_attribute, reference_device)
        self.is_relative = is_relative
        self.values = np.linspace(minValue, maxValue, npoints)

    def get_values(self):
        values = self.values
        if self.is_relative:
            reference_value = rgetattr(self.get_reference_device(), self.get_analyzed_attribute())
            for i in range(len(values)):
                values[i] *= reference_value
        return self.values


class Parametric_analysis(Option_class):
    NUMBER_OF_CORES = 1

    def __init__(self, theParametricParameter, theCharacterization, filename_collection=None, autosave=False):
        super().__init__()
        if filename_collection is None:
            self.filename_collection = "Param_{}".format(theParametricParameter.get_analyzed_attribute())
        else:
            self.filename_collection = filename_collection

        self.theCharacterization = theCharacterization
        self.theParametricParameter = theParametricParameter

        self.autosave = autosave
        self.my_autosave = None

        self.add_option(self.NUMBER_OF_CORES, Option_int("Number of cores used in evaluation", 1))

    def run(self):
        """Instantiates input arguments for analysis"""

        # Set devices to evaluate
        values = self.theParametricParameter.get_values()
        listOfDevices = list()
        for value in values:
            device = copy.deepcopy(self.theParametricParameter.get_reference_device())
            rsetattr(device, self.theParametricParameter.get_analyzed_attribute(), value)
            listOfDevices.append(device)

        # Collections out:
        theCollection_out = self.initialize_output_collection()

        # Simulates
        pool = Pool(min(cpu_count(), self.get_option_value(self.NUMBER_OF_CORES)))
        for device in pool.imap_unordered(self.evaluate, listOfDevices):
            theCollection_out.add_data(device)

        if self.my_autosave is not None:
            self.my_autosave.stop_autosave()
            self.my_autosave.save()
            self.my_autosave = None

        return theCollection_out

    def evaluate(self, theDevice):
        self.theCharacterization.compute(theDevice)
        return theDevice

    def initialize_output_collection(self):

        theCollection_out = Parametric_Collection()
        if self.autosave:
            filename = os.path.join(getPath_workspace(), self.filename_collection + theCollection_out.get_extension())
            self.my_autosave = AutosaveStruct(theCollection_out, filename)
            self.my_autosave.start_autosave(60)

        return theCollection_out
