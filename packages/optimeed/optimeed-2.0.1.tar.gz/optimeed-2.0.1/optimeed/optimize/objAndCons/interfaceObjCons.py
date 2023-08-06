from abc import ABCMeta, abstractmethod


class InterfaceObjCons(metaclass=ABCMeta):
    """Interface class for objectives and constraints. The objective is to MINIMIZE and the constraint has to respect VALUE <= 0"""

    @abstractmethod
    def compute(self, theDevice):
        """
        Get the value of the objective or the constraint. The objective is to MINIMIZE and the constraint has to respect VALUE <= 0

        :param theDevice: Input device that has already been evaluated
        :return: float.
        """
        pass

    def get_name(self):
        return "Objective (or constraint)"

    def __str__(self):
        return self.get_name()
