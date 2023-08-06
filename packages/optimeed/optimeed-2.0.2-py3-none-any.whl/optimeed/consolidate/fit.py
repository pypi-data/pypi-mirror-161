from optimeed.optimize.optiAlgorithms import MultiObjective_GA as OptimizationAlgorithm
from optimeed.optimize import run_optimization, Real_OptimizationVariable, InterfaceObjCons, OptimizerSettings, OptiHistoric
import numpy as np


class _Device:
    def __init__(self, fitFunction, nbArgs):
        self.functionArgs = [0.0]*nbArgs
        self.fitFunction = fitFunction


class _Objective(InterfaceObjCons):
    def __init__(self, x_data, y_data, fitCriterion):
        self.x_data = x_data
        self.y_data = y_data
        self.fitCriterion = fitCriterion

    def compute(self, theDevice):
        return self.fitCriterion(theDevice.fitFunction, theDevice.functionArgs, self.x_data, self.y_data)


def leastSquare(function, functionArgs, x_data, y_data):
    """
    Least square calculation (sum (y-ŷ)^2)

    :param function: Function to fit
    :param functionArgs: Arguments of the function
    :param x_data: x-axis coordinates of data to fit
    :param y_data: y-axis coordinates of data to fit
    :return: least squares
    """
    return np.sum((y_data - function(x_data, *functionArgs)) ** 2)


def r_squared(function, functionArgs, x_data, y_data):
    """
    R squared calculation

    :param function: Function to fit
    :param functionArgs: Arguments of the function
    :param x_data: x-axis coordinates of data to fit
    :param y_data: y-axis coordinates of data to fit
    :return: R squared
    """
    return -(1 - (np.sum((y_data - function(x_data, *functionArgs)) ** 2))/(np.sum((y_data - np.mean(y_data)) ** 2)))


def do_fit(fitFunction, x_data, y_data, *args, fitCriterion=leastSquare):
    """
    Main method to fit a function

    :param fitFunction: the function to fit (link to it)
    :param x_data: x-axis coordinates of data to fit
    :param y_data: y-axis coordinates of data to fit
    :param args: for each parameter: [min, max] admissible value
    :param fitCriterion: fit criterion to minimize. Default: least square
    :return: [arg_i_optimal, ...], y estimated, error.
    """
    print(args)
    theDevice = _Device(fitFunction, len(args))
    theAlgo = OptimizationAlgorithm()

    optimizationVariables = list()
    for i, minmax in enumerate(args):
        optimizationVariables.append(Real_OptimizationVariable('functionArgs[{}]'.format(i), *minmax))  #

    listOfObjectives = [_Objective(x_data, y_data, fitCriterion)]
    listOfConstraints = []

    theOptiParameters = OptimizerSettings(theDevice, listOfObjectives, listOfConstraints, optimizationVariables, theOptimizationAlgorithm=theAlgo)
    theOptiHistoric = OptiHistoric(optiname="fit", autosave=False, create_new_directory=False, performance_datastruct=False)

    resultsOpti, convergence = run_optimization(theOptiParameters, theOptiHistoric, max_opti_time_sec=3)

    y_est = fitFunction(x_data, *resultsOpti[0].functionArgs)

    return resultsOpti[0].functionArgs, y_est, y_data-y_est
