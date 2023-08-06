import time
from multiprocessing import Pool, cpu_count

from optimeed.core.tools import printIfShown, SHOW_INFO, SHOW_WARNING, indentParagraph
from optimeed.optimize.optiVariable import Binary_OptimizationVariable, Integer_OptimizationVariable, Real_OptimizationVariable
from optimeed.core import Option_class, Option_int, Option_str, Option_dict
from .algorithmInterface import AlgorithmInterface
from .convergence import EvolutionaryConvergence
# Platypus imports
from .platypus import FixedLengthArray, Generator, Solution
from .platypus.algorithms import NSGAIII, SPEA2, SMPSO, NSGAII, OMOPSO
from .platypus.core import Problem, TerminationCondition, nondominated, unique
from .platypus.evaluator import Evaluator, run_job
from .platypus.operators import CompoundOperator, SBX, HUX, PM, BitFlip
from .platypus.types import Real, Integer, Binary


class MyProblem(Problem):
    """Automatically sets the optimization problem"""

    def __init__(self, theOptimizationVariables, nbr_objectives, nbr_constraints, evaluationFunction):
        super(MyProblem, self).__init__(len(theOptimizationVariables), nbr_objectives, nbr_constraints)

        # Convert types of optimization variables
        for i in range(len(self.types)):
            optimizationVariable = theOptimizationVariables[i]
            if type(optimizationVariable) is Real_OptimizationVariable:
                self.types[i] = Real(optimizationVariable.get_min_value(), optimizationVariable.get_max_value())
            elif type(optimizationVariable) is Integer_OptimizationVariable:
                self.types[i] = Integer(optimizationVariable.get_min_value(), optimizationVariable.get_max_value())
            elif type(optimizationVariable) is Binary_OptimizationVariable:
                self.types[i] = Binary(1)
            else:
                raise ValueError("Optimization variable not managed with this algorithm")

        self.evaluationFunction = evaluationFunction
        self.constraints[:] = "<=0"
        self.directions = FixedLengthArray(nbr_objectives, self.MINIMIZE)

    def evaluate(self, solution):
        x = solution.variables[:]
        returnedValues = self.evaluationFunction(x)

        for i in range(len(returnedValues["objectives"])):
            solution.objectives[i] = returnedValues["objectives"][i]
        for i in range(len(returnedValues["constraints"])):
            solution.constraints[i] = returnedValues["constraints"][i]

        solution.junk = returnedValues  # NEW VARIABLE ADDED


class MyGenerator(Generator):
    """Population generator to insert initial individual"""

    def __init__(self, initialVectorGuess):
        super(MyGenerator, self).__init__()
        self.initialVectorGuess = initialVectorGuess
        self.inserted_initialVector = False

    def generate(self, problem):
        solution = Solution(problem)
        if not self.inserted_initialVector:
            solution.variables = [x.encode(self.initialVectorGuess[i]) for i, x in enumerate(problem.types)]
            self.inserted_initialVector = True
        else:
            solution.variables = [x.rand() for x in problem.types]
        return solution


class MaxTimeTerminationCondition(TerminationCondition):
    def __init__(self, maxTime):
        super(MaxTimeTerminationCondition, self).__init__()
        self.maxTime = maxTime
        self.startingTime = None

    def initialize(self, algorithm):
        self.startingTime = time.time()

    def shouldTerminate(self, algorithm):
        return time.time() - self.startingTime > self.maxTime


class ConvergenceTerminationCondition(TerminationCondition):
    def __init__(self, minrelchange_percent=0.1, nb_generation=15):
        super(ConvergenceTerminationCondition, self).__init__()
        self.minrelchange = minrelchange_percent
        self.nb_generation = nb_generation

    def initialize(self, algorithm):
        pass

    def shouldTerminate(self, algorithm):
        convergence = algorithm.archive.conv
        if convergence.last_step() <= self.nb_generation:
            return False
        try:
            curr_hypervolume, _ = convergence.get_hypervolume(convergence.get_pareto_at_step(convergence.last_step()))
            last_hypervolume, _ = convergence.get_hypervolume(convergence.get_pareto_at_step(convergence.last_step() - self.nb_generation))
            rel_change = abs((curr_hypervolume - last_hypervolume)/curr_hypervolume * 100)  # percent
            printIfShown("Current hypervolume: {} Before hypervolume: {} Rel Change: {}".format(curr_hypervolume, last_hypervolume, rel_change), SHOW_INFO)
            if rel_change < self.minrelchange:
                printIfShown("terminating because converged !", SHOW_INFO)
            return rel_change < self.minrelchange
        except (IndexError, ZeroDivisionError):
            return False


class SeveralTerminationCondition(TerminationCondition):
    def __init__(self):
        super().__init__()
        self.listOfTerminationConditions = list()

    def initialize(self, algorithm):
        for terminationCondition in self.listOfTerminationConditions:
            terminationCondition.initialize(algorithm)

    def add(self, theTerminationCondition):
        if isinstance(theTerminationCondition, TerminationCondition):
            self.listOfTerminationConditions.append(theTerminationCondition)
        else:
            printIfShown("Invalid termination condition", SHOW_WARNING)

    def shouldTerminate(self, algorithm):
        return any([terminationCondition.shouldTerminate(algorithm) for terminationCondition in self.listOfTerminationConditions])


class MyMapEvaluator(Evaluator):
    def __init__(self, callback_on_evaluation):
        super().__init__()
        self.callback_on_evaluation = callback_on_evaluation

    def evaluate_all(self, jobs, **kwargs):
        outputs = [None] * len(jobs)
        for k, job in enumerate(jobs):
            outputs[k] = run_job(job)
            self.callback_on_evaluation(outputs[k].solution.junk)
            del outputs[k].solution.junk

        return outputs


class MyMultiprocessEvaluator(Evaluator):
    def __init__(self, callback_on_evaluation, numberOfCores):
        super().__init__()
        self.callback_on_evaluation = callback_on_evaluation
        self.pool = Pool(numberOfCores)

    def my_callback(self, output):
        self.callback_on_evaluation(output.solution.junk)
        del output.solution.junk

    def evaluate_all(self, jobs, **kwargs):
        outputs = [self.pool.apply_async(run_job, args=(job,), callback=self.my_callback) for job in jobs]
        return [output.get() for output in outputs]

    def close(self):
        printIfShown("Closing Pool", SHOW_INFO)
        self.pool.close()
        printIfShown("Waiting for all processes to complete", SHOW_INFO)
        self.pool.join()
        printIfShown("Pool closed", SHOW_INFO)


class MultiObjective_GA(AlgorithmInterface, Option_class):
    """Based on `Platypus Library <https://platypus.readthedocs.io/en/docs/index.html>`_.
    Workflow:
    Define what to optimize and which function to call with a :class:`Problem`
    Define the initial population with a :class:`Generator`
    Define the algorithm. As options, define how to evaluate the elements with a :class:`Evaluator`, i.e., for multiprocessing.
    Define what is the termination condition of the algorithm with :class:`TerminationCondition`. Here, termination condition is a maximum time.
    """
    DIVISION_OUTER = 0
    OPTI_ALGORITHM = 1
    NUMBER_OF_CORES = 2
    KWARGS_ALGO = 3

    def __init__(self):
        super().__init__()

        self.maxTime = None  # set by set_maxtime
        self.evaluationFunction = None  # set by set_max_objective
        self.callback_on_evaluation = None  # set by set_max_objective
        self.initialPopulation = None  # set by set_initial_population OR randomly generated (default)
        self.currentPopulation = None
        self.numberOfObjective = None
        self.numberOfConstraints = None
        self.theDimensionalConstraints = None

        self.terminationConditions = SeveralTerminationCondition()
        self.kwargs_opti_algorithm = dict()  # Additional kwargs opti_algorithm

        self.add_option(self.OPTI_ALGORITHM, Option_str("Optimization algorithm", 'NSGAII', choices=["NSGAII", "NSGAIII", "OMOPSO", "SPEA2", "SMPSO"]))
        self.add_option(self.NUMBER_OF_CORES, Option_int("Number of cores used in evaluation", 1))
        self.add_option(self.KWARGS_ALGO, Option_dict("Keywords arguments to send to the optimization algorithm", {}))

        self.algorithm = None

    def initialize(self, initialVectorGuess, listOfOptimizationVariables):
        """This function is called just before running optimization algorithm."""

        theProblem = MyProblem(listOfOptimizationVariables, self.numberOfObjective, self.numberOfConstraints, self.evaluationFunction)

        kwargs = {"generator": MyGenerator(initialVectorGuess), "convergence": EvolutionaryConvergence()}
        # Update evaluator for multiprocessing
        if self.get_option_value(self.NUMBER_OF_CORES) > 1:
            kwargs.update({"evaluator": MyMultiprocessEvaluator(callback_on_evaluation=self.callback_on_evaluation,
                                                                numberOfCores=min(cpu_count(), self.get_option_value(self.NUMBER_OF_CORES))
                                                                )})
        else:
            kwargs.update({"evaluator": MyMapEvaluator(callback_on_evaluation=self.callback_on_evaluation)})

        # Update variator if different types to optimize
        base_type = theProblem.types[0].__class__
        if not all([isinstance(t, base_type) for t in theProblem.types]):
            kwargs.update({"variator": CompoundOperator(SBX(), HUX(), PM(), BitFlip())})

        kwargs.update(self.get_option_value(self.KWARGS_ALGO))

        # Set optimization algorithm
        divisions_outer = int(30 * self.numberOfObjective)
        if self.get_option_value(self.OPTI_ALGORITHM) == 'SPEA2':
            algorithm = SPEA2(theProblem, **kwargs)
        elif self.get_option_value(self.OPTI_ALGORITHM) == 'SMPSO':
            algorithm = SMPSO(theProblem, **kwargs)
        elif self.get_option_value(self.OPTI_ALGORITHM) == 'OMOPSO':
            algorithm = OMOPSO(theProblem, epsilons=[0.05], **kwargs)
        elif self.get_option_value(self.OPTI_ALGORITHM) == 'NSGAII':
            algorithm = NSGAII(theProblem, **kwargs)  # self.get_option_value(self.DIVISION_OUTER))
        elif self.get_option_value(self.OPTI_ALGORITHM) == 'NSGAIII':
            algorithm = NSGAIII(theProblem, divisions_outer, **kwargs)  # self.get_option_value(self.DIVISION_OUTER))
        else:
            raise NotImplementedError("This algorithm has not been yet implemented {}".format(self.get_option_value(self.OPTI_ALGORITHM)))
        self.algorithm = algorithm

    def compute(self):
        self.terminationConditions.add(MaxTimeTerminationCondition(self.maxTime))
        self.algorithm.run(self.terminationConditions)

        self.algorithm.evaluator.close()

        def decode_solution_platypus(var_solutions, var_optimisations):
            my_solutions = [None] * len(var_solutions)
            for k, type_var in enumerate(var_optimisations):
                my_solutions[k] = type_var.decode(var_solutions[k])
            return my_solutions

        return [decode_solution_platypus(solution.variables, self.algorithm.problem.types) for solution in unique(nondominated(self.algorithm.result)) if solution.feasible]

    def set_evaluationFunction(self, evaluationFunction, callback_on_evaluation, numberOfObjectives, numberOfConstraints):
        self.evaluationFunction = evaluationFunction
        self.callback_on_evaluation = callback_on_evaluation
        self.numberOfObjective = numberOfObjectives
        self.numberOfConstraints = numberOfConstraints

    def set_maxtime(self, maxTime):
        self.maxTime = maxTime

    def __str__(self):
        theStr = ''
        theStr += "Platypus multiobjective library\n"
        theStr += indentParagraph(super().__str__(), indent_level=1)
        return theStr

    def get_convergence(self):
        """This function is called just before compute. Because the convergence is contained in opti algorithm, it must be created now."""
        return self.algorithm.convergence

    def add_terminationCondition(self, theTerminationCondition):
        self.terminationConditions.add(theTerminationCondition)

    def reset(self):
        terminationConditions = self.terminationConditions
        kwargs_opti_algorithm = self.kwargs_opti_algorithm
        super().reset()
        self.terminationConditions = terminationConditions
        self.kwargs_opti_algorithm = kwargs_opti_algorithm
