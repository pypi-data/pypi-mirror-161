from abc import ABCMeta, abstractmethod


class InterfaceMathsToPhysics(metaclass=ABCMeta):
    """Interface to transform output from the optimizer to meaningful variables of the device"""

    @abstractmethod
    def fromMathsToPhys(self, xVector, theDevice, opti_variables):
        """
        Transforms an input vector coming from the optimization (e.g. [0.23, 4, False]) to "meaningful" variable (ex: length, number of poles, flag).

        :param xVector: List of optimization variables from the optimizer
        :param theDevice: :class:`~optimeed.InterfaceDevice.InterfaceDevice`
        :param opti_variables: list of :class:`~optimeed.optimize.OptimizationVariable.OptimizationVariable`
        """
        pass

    @abstractmethod
    def fromPhysToMaths(self, theDevice, opti_variables):
        """
        Extracts a mathematical vector from meaningful variable of the Device

        :param theDevice: :class:`~optimeed.InterfaceDevice.InterfaceDevice`
        :param opti_variables: list of :class:`~optimeed.optimize.OptimizationVariable.OptimizationVariable`
        :return: List of optimization variables
        """
        pass
