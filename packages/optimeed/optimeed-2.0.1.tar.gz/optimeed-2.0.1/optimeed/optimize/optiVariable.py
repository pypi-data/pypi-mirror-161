from optimeed.core.tools import text_format, rsetattr, rgetattr, printIfShown, SHOW_WARNING


class OptimizationVariable:
    """Contains information about the optimization of a variable"""
    attributeName: str

    def __init__(self, attributeName):
        """Instantiates the opti variable

        :param attributeName: name of the attribute to optimize
        """
        self.attributeName = attributeName

    def get_attribute_name(self):
        """Return the attribute to set"""
        return self.attributeName

    def add_prefix_attribute_name(self, thePrefix):
        """Used for nested object, lower the name by prefix. Example: R_ext becomes (thePrefix).R_ext"""
        self.attributeName = "{}.{}".format(thePrefix, self.get_attribute_name())

    def get_PhysToMaths(self, deviceIn):
        """Convert the initial value of the variable contained in the device to optimization variable value

        :param deviceIn: :class:`~optimeed.InterfaceDevice.InterfaceDevice`
        :return: value of the corresponding optimization variable
        """
        return rgetattr(deviceIn, self.get_attribute_name())

    def do_MathsToPhys(self, variableValue, deviceIn):
        """Apply the value to the device"""
        rsetattr(deviceIn, self.get_attribute_name(), variableValue)

    def __str__(self):
        return "Name: {:^25s} ".format(text_format.GREEN + self.attributeName + text_format.END)


class Real_OptimizationVariable(OptimizationVariable):
    """Real (continuous) optimization variable. Most used type"""
    val_min: float
    val_max: float

    def __init__(self, attributeName, val_min, val_max):
        """
        Instantiates the opti variable

        :param attributeName: name of the attribute to optimize
        :param val_min: minimal value of the optimization variable
        :param val_max: maximal value of the optimization variable
        """
        super().__init__(attributeName)
        self.val_min = val_min
        self.val_max = val_max

    def get_min_value(self):
        return self.val_min

    def get_max_value(self):
        return self.val_max

    def get_PhysToMaths(self, deviceIn):
        value = super().get_PhysToMaths(deviceIn)
        if not self.get_min_value() <= value <= self.get_max_value():
            printIfShown("Initial individual breaks design space boundaries: {}."
                         " The problem has been solved by using middle interval value".format(self.get_attribute_name()), SHOW_WARNING)
            return (self.get_min_value() + self.get_max_value())/2
        return value

    def do_MathsToPhys(self, value, deviceIn):
        super().do_MathsToPhys(float(value), deviceIn)

    def __str__(self):
        return '{} Real variable | Min Value: {:>5s} \t Max Value: {:<15s}  \n'.format(str(super().__str__()), str(self.get_min_value()), str(self.get_max_value()))


class Binary_OptimizationVariable(OptimizationVariable):
    """Boolean (True/False) optimization variable."""

    def get_PhysToMaths(self, deviceIn):
        return bool(super().get_PhysToMaths(deviceIn))

    def do_MathsToPhys(self, value, deviceIn):
        super().do_MathsToPhys(bool(value), deviceIn)

    def __str__(self):
        return '{} Binary variable |  \n'.format(str(super().__str__()))


class Integer_OptimizationVariable(OptimizationVariable):
    """Integer variable, in [min_value, max_value]"""

    val_min: int
    val_max: int

    def __init__(self, attributeName, val_min, val_max):
        """
        Instantiates the opti variable

        :param attributeName: name of the attribute to optimize
        :param val_min: minimal value of the optimization variable
        :param val_max: maximal value of the optimization variable
        """
        super().__init__(attributeName)
        self.val_min = val_min
        self.val_max = val_max

    def get_min_value(self):
        return self.val_min

    def get_max_value(self):
        return self.val_max

    def get_PhysToMaths(self, deviceIn):
        value = super().get_PhysToMaths(deviceIn)
        if not self.get_min_value() <= value <= self.get_max_value():
            printIfShown("Initial individual breaks design space boundaries: {}."
                         " The problem has been solved by using middle interval value".format(self.get_attribute_name()), SHOW_WARNING)
            return int((self.get_min_value() + self.get_max_value()) / 2)
        return value

    def do_MathsToPhys(self, value, deviceIn):
        super().do_MathsToPhys(int(value), deviceIn)

    def __str__(self):
        return '{} Integer variable | Min Value: {:>5s} \t Max Value: {:<15s}  \n'.format(str(super().__str__()), str(self.get_min_value()), str(self.get_max_value()))
