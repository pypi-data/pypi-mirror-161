from optimeed.core import printIfShown, SHOW_WARNING, text_format
from typing import List, Dict


class Base_Option:
    def __init__(self, name, based_value, choices=None):
        self.name = name
        self.value = based_value
        self.choices = choices
        if self.choices is None:
            self.choices = list()

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def set_value(self, value):
        self.value = value

    def get_choices(self):
        return self.choices


class Option_bool(Base_Option):
    name: str
    value: bool

    def set_value(self, value):
        self.value = bool(value)

    def get_choices(self):
        return [True, False]


class Option_str(Base_Option):
    name: str
    value: str

    def set_value(self, value):
        self.value = str(value)


class Option_int(Base_Option):
    name: str
    value: int

    def set_value(self, value):
        self.value = int(value)


class Option_float(Base_Option):
    name: str
    value: float

    def set_value(self, value):
        self.value = float(value)


class Option_dict(Base_Option):
    name: str
    value: dict

    def set_value(self, value):
        self.value = dict(value)


class Option_class:
    options_bool: Dict[int, Option_bool]
    options_str: Dict[int, Option_str]
    options_int: Dict[int, Option_int]
    options_float: Dict[int, Option_float]
    options_dict: Dict[int, Option_dict]

    def __init__(self):
        """
        A high level class that provides means of managing options (and automatically saving them).
        Reinitializing children does not reinitialize options
        Restriction: option_get_value can not be used within a __init__ method.
        """
        if not hasattr(self, "initialized"):
            self.options_bool = dict()
            self.options_str = dict()
            self.options_int = dict()
            self.options_float = dict()
            self.options_dict = dict()
        self.initialized = True

    @staticmethod
    def get_option_attributes():
        return ["options_bool", "options_int", "options_float", "options_str", "options_dict"]

    def add_option(self, idOption, theOption):
        if type(idOption) is not int:
            raise TypeError("Wrong type for id Option")
        if isinstance(theOption, Option_bool):
            self.options_bool[idOption] = theOption
        elif isinstance(theOption, Option_str):
            self.options_str[idOption] = theOption
        elif isinstance(theOption, Option_int):
            self.options_int[idOption] = theOption
        elif isinstance(theOption, Option_float):
            self.options_float[idOption] = theOption
        elif isinstance(theOption, Option_dict):
            self.options_dict[idOption] = theOption
        else:
            printIfShown("Unvalid option type: {}".format(theOption), SHOW_WARNING)

    def get_option_name(self, idOption):
        for option in self._pack_options():
            if idOption in option:
                return option[idOption].get_name()

    def get_option_value(self, idOption):
        for option in self._pack_options():
            if idOption in option:
                return option[idOption].get_value()

    def set_option(self, idOption, value):
        for option in self._pack_options():
            if idOption in option:
                option[idOption].set_value(value)

    def _pack_options(self):
        return [getattr(self, option) for option in self.get_option_attributes()]

    def __str__(self):
        theStr = ''
        for option in self._pack_options():
            if len(option):
                theStr += text_format.BLUE + 'Options'
                for key in option:
                    theStr += '\n◦ {:<15}'.format(self.get_option_name(key)) + '\t-\t' + str(self.get_option_value(key))
                theStr += text_format.END + "\n"
        return theStr

