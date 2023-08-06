from .characterization import Characterization
from .mathsToPhysics import MathsToPhysics
from .optiAlgorithms import MultiObjective_GA
from optimeed.core import SaveableObject
from optimeed.core import printIfShown, SHOW_DEBUG
from optimeed.core.commonImport import SHOW_INFO, SHOW_WARNING
import traceback
import time
import copy
import math

default = dict()
default['M2P'] = MathsToPhysics()
default['Charac'] = Characterization()
default['Algo'] = MultiObjective_GA()


class OptimizerSettings(SaveableObject):
    def __init__(self, theDevice, theObjectives, theConstraints, theOptimizationVariables, theOptimizationAlgorithm=None, theMathsToPhysics=None, theCharacterization=None):
        """
        Prepare the optimizer for the optimization.

        :param theDevice: object of type  :class:`~optimeed.core.interfaceDevice.InterfaceDevice`
        :param theObjectives: list of objects of type :class:`~optimeed.optimize.objAndCons.interfaceObjCons.InterfaceObjCons`
        :param theConstraints: list of objects of type :class:`~optimeed.optimize.objAndCons.interfaceObjCons.InterfaceObjCons`
        :param theOptimizationVariables: list of objects of type :class:`~optimeed.optimize.optiVariable.OptimizationVariable`
        :param theOptimizationAlgorithm: list of objects of type :class:`~optimeed.optimize.optiAlgorithms.algorithmInterface.AlgorithmInterface`
        :param theMathsToPhysics: object of type :class:`~optimeed.optimize.mathsToPhysics.interfaceMathsToPhysics.InterfaceMathsToPhysics`
        :param theCharacterization: object of type :class:`~optimeed.optimize.characterization.interfaceCharacterization.InterfaceCharacterization`
        :return:
        """
        self.theDevice = theDevice
        self.theMathsToPhysics = theMathsToPhysics if theMathsToPhysics is not None else default['M2P']
        self.theCharacterization = theCharacterization if theCharacterization is not None else default['Charac']
        self.theObjectives = theObjectives
        self.theConstraints = theConstraints
        self.theOptimizationAlgorithm = theOptimizationAlgorithm if theOptimizationAlgorithm is not None else default['Algo']
        self.theOptimizationVariables = theOptimizationVariables

    def get_additional_attributes_to_save(self):
        return ["theDevice", "theMathsToPhysics", "theCharacterization", "theOptimizationAlgorithm"]

    def get_additional_attributes_to_save_list(self):
        return ["theObjectives", "theConstraints", "theOptimizationVariables"]

    def get_device(self):
        return self.theDevice

    def get_M2P(self):
        return self.theMathsToPhysics

    def get_charac(self):
        return self.theCharacterization

    def get_optivariables(self):
        return self.theOptimizationVariables

    def get_objectives(self):
        return self.theObjectives
    
    def get_constraints(self):
        return self.theConstraints

    def get_optialgorithm(self):
        return self.theOptimizationAlgorithm
    
    
class _Evaluator:
    """This is the main class that serves as evaluator. This class is NOT process safe (i.e., copy of it might be generated upon process call)"""

    def __init__(self, optimization_parameters: OptimizerSettings):
        # Variables defining an optimization problem
        self.theDevice = optimization_parameters.get_device()
        self.theMathsToPhysics = optimization_parameters.get_M2P()
        self.theCharacterization = optimization_parameters.get_charac()
        self.theObjectives = optimization_parameters.get_objectives()
        self.theConstraints = optimization_parameters.get_constraints()
        self.theOptimizationVariables = optimization_parameters.get_optivariables()
        self.startingTime = None

    def start(self):
        self.startingTime = time.time()

    def evaluate(self, x):
        """
        Evaluates the performances of device associated to entrance vector x. Outputs the objective function and the constraints,
        and other data used in optiHistoric.

        This function is NOT process safe: "self." is a FORK in multiprocessing algorithms.
        It means that the motor originally contained in self. is modified only in the fork, and only gathered by reaching the end of the fork.

        :param x: Input mathematical vector from optimization algorithm
        :return: dictionary, containing objective values (list of scalar), constraint values (list of scalar), and other info (motor, time)
        """
        copyDevice = copy.copy(self.theDevice)
        self.theMathsToPhysics.fromMathsToPhys(x, copyDevice, self.theOptimizationVariables)

        characterization_failed = False
        # noinspection PyBroadException
        try:
            self.theCharacterization.compute(copyDevice)
        except Exception:
            characterization_failed = True
            printIfShown("An error in characterization. Set objectives to inf. Error :" + traceback.format_exc(), SHOW_WARNING)

        nbr_of_objectives = len(self.theObjectives)
        objective_values = [float('inf')]*nbr_of_objectives

        nbr_of_constraints = len(self.theConstraints)
        constraint_values = [float('inf')] * nbr_of_constraints

        if not characterization_failed:
            for i in range(nbr_of_objectives):
                # noinspection PyBroadException
                try:
                    objective_values[i] = self.theObjectives[i].compute(copyDevice)
                    if math.isnan(objective_values[i]):
                        objective_values[i] = float('inf')
                except Exception:
                    objective_values[i] = float('inf')
                    printIfShown("An error in objectives. inf value has been set to continue execution. Error:" + traceback.format_exc(), SHOW_DEBUG)

            for i in range(nbr_of_constraints):
                # noinspection PyBroadException
                try:
                    constraint_values[i] = self.theConstraints[i].compute(copyDevice)
                except Exception:
                    constraint_values[i] = float('inf')
                    printIfShown("An error in constraints. NaN value has been set to continue execution. Error:" + traceback.format_exc(), SHOW_DEBUG)

        valuesToReturn = dict()
        valuesToReturn["params"] = x
        valuesToReturn["device"] = copyDevice
        valuesToReturn["time"] = time.time()-self.startingTime
        valuesToReturn["objectives"] = objective_values
        valuesToReturn["constraints"] = constraint_values
        return valuesToReturn  # objective_values, constraint_values

    def reevaluate_solutions(self, x_solutions):
        resultsdevices = [None] * len(x_solutions)
        for i, x_solution in enumerate(x_solutions):
            self.theMathsToPhysics.fromMathsToPhys(x_solution, self.theDevice, self.theOptimizationVariables)
            self.theCharacterization.compute(self.theDevice)
            resultsdevices[i] = copy.deepcopy(self.theDevice)
        return resultsdevices


def run_optimization(optimization_parameters: OptimizerSettings, opti_historic, max_opti_time_sec=10):
    """
    Perform the optimization.

    :return: list of the best optimized devices, convergence information
    """

    evaluator = _Evaluator(optimization_parameters)
    theOptimizationAlgorithm = optimization_parameters.get_optialgorithm()

    # Initialize opti algorithms
    opti_historic.start(optimization_parameters)
    evaluator.start()

    initialVectorGuess = evaluator.theMathsToPhysics.fromPhysToMaths(evaluator.theDevice, evaluator.theOptimizationVariables)

    theOptimizationAlgorithm.set_maxtime(max_opti_time_sec)
    theOptimizationAlgorithm.set_evaluationFunction(evaluator.evaluate, opti_historic.log_after_evaluation, len(evaluator.theObjectives), len(evaluator.theConstraints))
    # Initialize the algorithm
    theOptimizationAlgorithm.initialize(initialVectorGuess, evaluator.theOptimizationVariables)

    # Get track of convergence
    convergence = theOptimizationAlgorithm.get_convergence()
    opti_historic.set_convergence(convergence)

    # Start optimization
    printIfShown("Performing optimization", SHOW_INFO)
    x_solutions = theOptimizationAlgorithm.compute()
    printIfShown("Optimization ended", SHOW_INFO)

    # Manage results
    success, best_devices = opti_historic.get_best_devices_without_reevaluating(x_solutions)
    if not success:
        printIfShown("Could not retrieve best devices from database ... Reevaluating", SHOW_INFO)
        best_devices = evaluator.reevaluate_solutions(x_solutions)

    # Set results and save
    opti_historic.set_results(best_devices)
    opti_historic.save()

    return best_devices, convergence
