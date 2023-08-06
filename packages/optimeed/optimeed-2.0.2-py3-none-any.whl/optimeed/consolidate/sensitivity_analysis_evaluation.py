from optimeed.core import printIfShown, SHOW_WARNING
import traceback


def evaluate(inputs):
    x, theDevice, theMathsToPhys, theCharacterization, list_of_optimization_variables, index = inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5]
    """Main evaluation function"""
    output = dict()
    output["device"] = theDevice
    output["x"] = x
    output["index"] = index

    theMathsToPhys.fromMathsToPhys(x, theDevice, list_of_optimization_variables)
    # noinspection PyBroadException
    try:
        theCharacterization.compute(theDevice)
        output["success"] = True
    except Exception:
        printIfShown("An error in characterization. Bypassing it to continue execution. Error :" + traceback.format_exc(), SHOW_WARNING)
        output["success"] = False
    return output
