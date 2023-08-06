from abc import ABCMeta, abstractmethod


# Proper usage: set numberOfOptimisationParameters first ! then lower/upper then time then objective then compute :)
class AlgorithmInterface(metaclass=ABCMeta):
    """Interface for the optimization algorithm"""

    @abstractmethod
    def initialize(self, initialVectorGuess, listOfOptimizationVariables):
        """
        This function is called once parameters can't be changed anymore, before "get_convergence".

        :param initialVectorGuess: list of variables that describe the initial individual
        :param listOfOptimizationVariables: list of :class:`optimeed.optimize.optiVariable.OptimizationVariable`
        :return:
        """

    @abstractmethod
    def compute(self):  # Launch the optimization
        """
        Launch the optimization

        :return: vector of optimal variables
        """
        pass

    @abstractmethod
    def set_evaluationFunction(self, evaluationFunction, callback_on_evaluation, numberOfObjectives, numberOfConstraints):
        """
        Set the evaluation function and all the necessary callbacks

        :param evaluationFunction: check :meth:`~optimeed.optimize.optimizer.evaluateObjectiveAndConstraints`
        :param callback_on_evaluation: check :meth:`~optimeed.optimize.optimizer.callback_on_evaluation`. Call this function after performing the evaluation of the individuals
        :param numberOfObjectives: int, number of objectives
        :param numberOfConstraints: int, number of constraints
        """
        pass

    @abstractmethod
    def set_maxtime(self, maxTime):  # Maximum time for the optimization
        """Set maximum optimization time (in seconds)"""
        pass

    @abstractmethod
    def get_convergence(self):
        """
        Get the convergence of the optimization

        :return: :class:`~optimeed.optimize.optiAlgorithms.convergence.interfaceConvergence.InterfaceConvergence`
        """
        pass

    def reset(self):
        self.__init__()
