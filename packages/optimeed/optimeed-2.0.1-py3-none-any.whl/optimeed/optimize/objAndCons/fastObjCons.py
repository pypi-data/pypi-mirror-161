from optimeed.core.tools import applyEquation
from .interfaceObjCons import InterfaceObjCons


class FastObjCons(InterfaceObjCons):
    """Convenience class to create an objective or a constraint very fast."""
    def __init__(self, constraintEquation, name=None):
        super().__init__()
        self.constraintEquation = constraintEquation
        self.name = name

    def compute(self, theDevice):
        return applyEquation(theDevice, self.constraintEquation)

    def get_name(self):
        if self.name is None:
            return self.constraintEquation
        return str(self.name)
