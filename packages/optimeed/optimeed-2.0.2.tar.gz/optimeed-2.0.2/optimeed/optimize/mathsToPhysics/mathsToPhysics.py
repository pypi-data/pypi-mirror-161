from .interfaceMathsToPhysics import InterfaceMathsToPhysics
# from optimeed.core import printIfShown, SHOW_WARNING


class MathsToPhysics(InterfaceMathsToPhysics):
    """Dummy yet powerful example of maths to physics.
    The optimization variables are directly injected to the device"""
    def __init__(self):
        super().__init__()

    def fromMathsToPhys(self, xVector, theDevice, theOptimizationVariables):
        if len(xVector) != len(theOptimizationVariables):
            raise ValueError("In mathsToPhysics: length vectors and optimization variables are not the same")

        for i in range(len(xVector)):
            theOptimizationVariables[i].do_MathsToPhys(xVector[i], theDevice)

    def fromPhysToMaths(self, theDevice, theOptimizationVariables):
        x01 = [None]*len(theOptimizationVariables)
        for i, optimizationVariable in enumerate(theOptimizationVariables):
            x01[i] = optimizationVariable.get_PhysToMaths(theDevice)
        return x01

    def __str__(self):
        return "Dummy maths to physics"
