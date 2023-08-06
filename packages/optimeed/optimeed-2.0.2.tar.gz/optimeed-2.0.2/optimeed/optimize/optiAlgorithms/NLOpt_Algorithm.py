import nlopt
import numpy as np

from optimeed.core.tools import isNonePrintMessage, printIfShown, SHOW_ERROR, SHOW_WARNING, indentParagraph
from .algorithmInterface import AlgorithmInterface
from optimeed.optimize.optiVariable import Binary_OptimizationVariable, Integer_OptimizationVariable, Real_OptimizationVariable
from .convergence import EvolutionaryConvergence
from optimeed.core import Option_class, Option_int, Option_str


class ConvergenceManager:
    def __init__(self):
        self.objectives = []
        self.popSize = 0
        self.convergence = EvolutionaryConvergence()

    def add_point(self, newObj):
        self.objectives.append([newObj])
        if len(self.objectives) == self.popSize:
            self.convergence.set_curr_step(self.objectives, [[]]*len(self.objectives))
            self.objectives = []

    def set_pop_size(self, popSize):
        self.popSize = popSize


class NLOpt_Algorithm(AlgorithmInterface, Option_class):
    ALGORITHM = 0
    POPULATION_SIZE = 1

    def __init__(self):
        super().__init__()
        self.maxTime = None  # set by set_maxtime
        self.evaluationFunction = None  # set by set_evaluationFunction
        self.theDimensionalConstraints = None

        self.add_option(self.ALGORITHM, Option_str("Algorithm. Recommended local/global: LN_SBPLX/GN_CRS2_LM . Consult NLopt help page for more.", 'GN_CRS2_LM'))
        self.add_option(self.POPULATION_SIZE, Option_int("Size of the population (stochastic algorithms only)", 20))

        self.convManager = ConvergenceManager()
        self.curr_pop = 0

        self.initialVectorGuess = None
        self.listOfOptimizationVariables = None

    def initialize(self, initialVectorGuess, listOfOptimizationVariables):
        self.initialVectorGuess = initialVectorGuess
        self.listOfOptimizationVariables = listOfOptimizationVariables

    def compute(self):
        # Check if variables properly initialized, otherwise return
        notInit_message = " not initialized in NLOpt_Algorithm. Aborting optimization loop."
        if isNonePrintMessage(self.maxTime, "maxTime" + notInit_message, SHOW_ERROR):
            return
        if isNonePrintMessage(self.evaluationFunction, "evaluationFunction" + notInit_message, SHOW_ERROR):
            return
        if self.get_option_value(self.POPULATION_SIZE) <= len(self.initialVectorGuess):
            raise ValueError("Population size must be bigger than the number of parameters of this algorithm. Use options")

        self.convManager.set_pop_size(self.get_option_value(self.POPULATION_SIZE))
        # If everything exists: create nlopt and launch it
        numberOfOptimizationParameters = len(self.initialVectorGuess)
        theOptimizationAlgorithm = nlopt.opt(getattr(nlopt, self.get_option_value(self.ALGORITHM)), numberOfOptimizationParameters)

        theOptimizationAlgorithm.set_min_objective(self.evaluationFunction)
        theOptimizationAlgorithm.set_maxtime(float(self.maxTime))

        self.__set_optimizationVariables(self.listOfOptimizationVariables, theOptimizationAlgorithm)

        theOptimizationAlgorithm.set_population(int(self.get_option_value(self.POPULATION_SIZE)))
        return [theOptimizationAlgorithm.optimize(np.array(self.initialVectorGuess).astype(float))]

    @staticmethod
    def __set_optimizationVariables(listOfOptimizationVariables, theOptimizationAlgorithm):
        lowerBounds = []
        upperBounds = []
        for optimizationVariable in listOfOptimizationVariables:
            if type(optimizationVariable) is Real_OptimizationVariable:
                lowerBounds.append(optimizationVariable.get_min_value())
                upperBounds.append(optimizationVariable.get_max_value())
            elif type(optimizationVariable) is Integer_OptimizationVariable:
                printIfShown("Integer variables not natively supported by the optimization algorithm", SHOW_WARNING)
                lowerBounds.append(optimizationVariable.get_min_value())
                upperBounds.append(optimizationVariable.get_max_value())
            elif type(optimizationVariable) is Binary_OptimizationVariable:
                printIfShown("Boolean variables not natively supported by the optimization algorithm", SHOW_WARNING)
                lowerBounds.append(0)
                upperBounds.append(1)
            else:
                raise ValueError("Optimization algorithm not working with this kind of optimization variables")

        theOptimizationAlgorithm.set_lower_bounds(np.array(lowerBounds).astype(float))
        theOptimizationAlgorithm.set_upper_bounds(np.array(upperBounds).astype(float))

    def set_evaluationFunction(self, evaluationFunction, callback_on_evaluate, numberOfObjectives, _numberOfConstraints):
        if numberOfObjectives > 1:
            printIfShown("Optimization algorithm does not support true multiobjective. Using sum instead", SHOW_WARNING)

        def adapted_evaluationFunction(x_in, _grad):
            returnedValues = evaluationFunction(x_in)

            objs = returnedValues["objectives"]
            const = returnedValues["constraints"]
            sum_const = 0
            for constraint in const:
                if constraint > 0:
                    sum_const += constraint*7000

            callback_on_evaluate(returnedValues)
            objective = np.float(sum(objs) + sum_const)

            self.convManager.add_point(objective)
            return objective
        self.evaluationFunction = adapted_evaluationFunction

    def set_maxtime(self, maxTime):
        self.maxTime = maxTime

    def __str__(self):
        theStr = ''
        theStr += "NLOpt optimization library\n"
        theStr += indentParagraph(super().__str__(), indent_level=1)
        return theStr

    def get_convergence(self):
        return self.convManager.convergence
