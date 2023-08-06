from abc import ABCMeta, abstractmethod


class InterfaceCharacterization(metaclass=ABCMeta):
    """Interface for the evaluation of a device"""

    @abstractmethod
    def compute(self, theDevice):
        """
        Action to perform to characterize (= compute the objective function) of the device.

        :param theDevice: the device to characterize
        """
        pass

    def __str__(self):
        return "Characterization - No name given"
