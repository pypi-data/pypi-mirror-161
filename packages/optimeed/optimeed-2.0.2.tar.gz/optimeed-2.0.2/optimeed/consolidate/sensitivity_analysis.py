from SALib.analyze import sobol
from optimeed.core import SaveableObject, AutosaveStruct, create_unique_dirname, SHOW_INFO, order_lists, printIfShown, Performance_ListDataStruct
from typing import List
from .sensitivity_analysis_evaluation import evaluate
from optimeed.core import SingleObjectSaveLoad
import numpy as np
from optimeed.core import getPath_workspace
from optimeed.optimize import Real_OptimizationVariable
from multiprocessing import Pool

import math
import os


class SensitivityResults(SaveableObject):
    paramsToEvaluate: List[float]
    success: bool
    index: int

    def __init__(self):
        self.paramsToEvaluate = [0.0]
        self.device = None
        self.success = False
        self.index = 0

    def add_data(self, params, device, success, index):
        self.device = device
        self.success = success
        self.paramsToEvaluate = params
        self.index = index

    def get_additional_attributes_to_save(self):
        return ["device"]


class SensitivityParameters(SaveableObject):
    list_of_optimization_variables: List[Real_OptimizationVariable]
    param_values: List[List[float]]

    def __init__(self, param_values, list_of_optimization_variables, theDevice, theMathsToPhys, theCharacterization):
        """
        These are the parameters t
        :param list_of_optimization_variables: list of OptiVariables that are analyzed
        :param theDevice: /
        :param theMathsToPhys: /
        :param theCharacterization: /"""
        self.theDevice = theDevice
        self.theMathsToPhys = theMathsToPhys
        self.theCharacterization = theCharacterization
        self.list_of_optimization_variables = list_of_optimization_variables
        self.param_values = param_values

    def get_device(self):
        return self.theDevice

    def get_M2P(self):
        return self.theMathsToPhys

    def get_charac(self):
        return self.theCharacterization

    def get_optivariables(self):
        return self.list_of_optimization_variables

    def get_paramvalues(self):
        return self.param_values

    def get_additional_attributes_to_save(self):
        return ["theDevice", "theMathsToPhys", "theCharacterization"]


def get_sensitivity_problem(list_of_optimization_variables):
    """
    This is the first method to use. Convert a list of optimization varisbles to a SALib problem

    :param list_of_optimization_variables: List of optimization variables
    :return: SALib problem
    """
    num_vars = len(list_of_optimization_variables)
    names = list()
    bounds = list()

    for variable in list_of_optimization_variables:
        if isinstance(variable, Real_OptimizationVariable):
            names.append(variable.get_attribute_name())
            bounds.append([variable.get_min_value(), variable.get_max_value()])
        else:
            raise TypeError("Optimization variable must be of real type to perform this analysis")
    problem = {'num_vars': num_vars, 'names': names, 'bounds': bounds}
    return problem


def evaluate_sensitivities(theSensitivityParameters: SensitivityParameters,
                           numberOfCores=2, studyname="sensitivity", indices_to_evaluate=None):
    """
    Evaluate the sensitivities

    :param theSensitivityParameters: class`~SensitivityParameters`
    :param numberOfCores: number of core for multicore evaluation
    :param studyname: Name of the study, that will be the subfolder name in workspace
    :param indices_to_evaluate: if None, evaluate all param_values, otherwise if list: evaluate subset of param_values defined by indices_to_evaluate
    :return: collection of class`~SensitivityResults`
    """
    myDataStruct = Performance_ListDataStruct()
    foldername = create_unique_dirname(os.path.join(getPath_workspace(), studyname))

    SingleObjectSaveLoad.save(theSensitivityParameters, os.path.join(foldername, "sensitivity_params.json"))
    # Start saving
    autosaveStruct = AutosaveStruct(myDataStruct, filename="{}/sensitivity".format(foldername))
    autosaveStruct.start_autosave(timer_autosave=60*5)

    param_values = theSensitivityParameters.get_paramvalues()
    try:
        param_values = param_values.tolist()
    except AttributeError:
        pass

    if indices_to_evaluate is None:
        indices = list(range(len(param_values)))
    else:
        indices = indices_to_evaluate
        param_values = [param_values[index] for index in indices_to_evaluate]

    # create jobs
    jobs = []
    for index, params in zip(indices, param_values):
        jobs.append([params, theSensitivityParameters.get_device(), theSensitivityParameters.get_M2P(),
                     theSensitivityParameters.get_charac(), theSensitivityParameters.get_optivariables(), index])

    pool = Pool(numberOfCores)
    nb_to_do = len(param_values)
    nb_done = 0
    permutations= list()
    for output in pool.imap_unordered(evaluate, jobs):
        result = SensitivityResults()
        result.add_data(output["x"], output["device"], output["success"], output["index"])
        myDataStruct.add_data(result)
        permutations.append(output["index"])
        nb_done += 1
        printIfShown("did {} over {}".format(nb_done, nb_to_do), SHOW_INFO)

    # save results
    autosaveStruct.stop_autosave()

    myDataStruct.reorder(permutations=permutations)
    autosaveStruct.save()

    pool.close()
    pool.join()
    return myDataStruct


def analyse_sobol_create_array(theSensitivityParameters: SensitivityParameters, objectives):
    """
    Create readible result array, ordered by decreasing sobol indices.

    :param theSensitivityParameters: class:`SensitivityParameters`
    :param objectives: array-like of objective
    :return: tuples of STR, for S1 and ST
    """
    problem_SALib = get_sensitivity_problem(theSensitivityParameters.get_optivariables())
    Si = sobol.analyze(problem_SALib, np.array(objectives))

    nb_params = len(theSensitivityParameters.get_optivariables())
    _, ordered_S1 = order_lists(Si['S1'], list(range(nb_params)))
    _, ordered_ST = order_lists(Si['ST'], list(range(nb_params)))
    ordered_S1.reverse()
    ordered_ST.reverse()

    def format_array(indices, prefix):
        theStr = ''
        theStr += '─' * 120 + '\n'
        theStr += "{:^12}{:^14}{:^25}{:<}".format(*["Rank (" + prefix + ")", "Sobol value", "+- 95% conf", "Param name"]) + '\n'
        theStr += '─' * 120 + '\n'
        for i, map_index in enumerate(indices):
            row = [i + 1, Si[prefix][map_index], Si[prefix + '_conf'][map_index], theSensitivityParameters.get_optivariables()[map_index].get_attribute_name()]
            theStr += "{:^12}{:^14.3f}{:^25.3f}{}".format(*row) + '\n'
        theStr += '─' * 50 + '\n'
        theStr += "{:^12}{:^14.3f}{:^25}{:<}".format("SUM", sum(Si[prefix]), "", "") + '\n'
        return theStr

    S1_array = format_array(ordered_S1, "S1")
    ST_array = format_array(ordered_ST, "ST")
    print(S1_array)
    print(ST_array)
    return S1_array, ST_array


def analyse_sobol_convergence(theSensitivityParameters: SensitivityParameters, objectives, stepsize=1):
    """
    Create dictionary for convergence plot

    :param theSensitivityParameters: class:`SensitivityParameters`
    :param objectives: array-like of objective
    :return: Dictionary
    """
    problem_SALib = get_sensitivity_problem(theSensitivityParameters.get_optivariables())
    opti_variables = theSensitivityParameters.get_optivariables()
    nb_params = len(opti_variables)

    max_nb_step = math.floor(len(objectives) / (2*nb_params + 2))

    outputs = list()
    steps = list(range(1, max_nb_step, stepsize))
    for sample_size in steps:
        printIfShown("Doing {} over {}".format(sample_size, max_nb_step))
        outputs.append(sobol.analyze(problem_SALib, np.array(objectives[0:sample_size*(2*nb_params+2)])))

    outputs_dict = dict()
    for i in range(nb_params):
        outputs_dict[i] = {'S1': [output['S1'][i] for output in outputs],
                           'ST': [output['ST'][i] for output in outputs],
                           'step': steps,
                           'name': opti_variables[i].get_attribute_name()}
    return outputs_dict


