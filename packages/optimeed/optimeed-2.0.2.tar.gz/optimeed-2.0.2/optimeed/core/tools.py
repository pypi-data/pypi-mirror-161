import ast
import inspect
import operator
import os
import re
import sys

import numpy as np

from optimeed.core.commonImport import *

_workspace_path = os.path.abspath(os.getcwd() + '/Workspace')


class text_format:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WHITE = '\033[30m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def software_version():
    MAJOR = 1.0
    MINOR = 0.0
    return MAJOR * 10 + MINOR


# # Find an expression delimited by begin_char and end_char in theStr, and apply transformation replace_function
# ex: find_and_replace('{', '}', 2*{x}, lambda str_in: str_in + "*2") returns 2*x*2
def find_and_replace(begin_char, end_char, theStr, replace_function):
    regex = '\\' + begin_char + '([^}]+)' + '\\' + end_char
    split_str = re.split(regex, theStr)  # Replace chars are even
    new_str = ''
    for i in range(len(split_str)):
        if i % 2:
            new_str += str(replace_function(split_str[i]))
        else:
            new_str += str(split_str[i])
    return new_str


def create_unique_dirname(dirname):
    base_dir = dirname
    index = 0
    while os.path.isdir(dirname):
        dirname = base_dir + "_" + str(index)
        index += 1
    os.makedirs(os.path.abspath(dirname))
    return dirname


def applyEquation(objectIn, s):
    """
    Apply literal expression based on an object

    :param objectIn: Object
    :param s: literal expression. Float variables taken from the object are written between {}, int between []. Example: s="{x}+{y}*2" if x and y are attributes of objectIn.
    :return: value (float)
    """
    str_eq = find_and_replace("{", "}", s, lambda attr_in: "({})".format(float(rgetattr(objectIn, attr_in))))
    str_eq = find_and_replace("[", "]", str_eq, lambda attr_in: "({})".format(int(rgetattr(objectIn, attr_in))))
    return eval(str_eq)


def arithmeticEval(s):
    node = ast.parse(s, mode='eval')
    binOps = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg
    }

    def _eval(in_node):
        if isinstance(in_node, ast.Expression):
            return _eval(in_node.body)
        elif isinstance(in_node, ast.Str):
            return in_node.s
        elif isinstance(in_node, ast.Num):
            return in_node.n
        elif isinstance(in_node, ast.BinOp):
            return binOps[type(in_node.op)](_eval(in_node.left), _eval(in_node.right))
        elif isinstance(in_node, ast.Name):
            return float('inf')
        elif isinstance(in_node, ast.UnaryOp):
            return binOps[type(in_node.op)](_eval(in_node.operand))
        else:
            raise TypeError('Unsupported type {}'.format(in_node))

    return _eval(node.body)


def isNonePrintMessage(theObject, theMessage, show_type=SHOW_INFO):
    if theObject is None:
        printIfShown(theMessage, show_type)
        return True
    return False


def getPath_workspace():
    """Get workspace path (i.e., location where optimeed files will be created). Create directory if doesn't exist."""
    if not os.path.exists(_workspace_path):
        os.makedirs(_workspace_path)
    return _workspace_path


def setPath_workspace(thePath):
    """Set workspace path (i.e., location where optimeed files will be created)"""
    global _workspace_path
    _workspace_path = os.path.abspath(os.path.expandvars(os.path.expanduser(thePath)))


def getLineInfo(lvl=1):
    filename = os.path.relpath(inspect.stack()[lvl][1], os.getcwd())
    line = inspect.stack()[lvl][2]
    method = inspect.stack()[lvl][3]
    return filename, method, line


def printIfShown(theStr, show_type=SHOW_DEBUG, isToPrint=True, appendTypeName=True, end='\n'):
    if isToPrint:
        try:
            sys.stdout.isatty()
            if show_type == SHOW_WARNING:
                colourBegin = text_format.YELLOW  # yellow
                if appendTypeName:
                    colourBegin += 'Warning: '
            elif show_type == SHOW_ERROR:
                colourBegin = text_format.RED
                if appendTypeName:
                    colourBegin += 'ERROR: '
            elif show_type == SHOW_INFO:
                colourBegin = text_format.BLUE
                if appendTypeName:
                    colourBegin += 'Info: '
            elif show_type == SHOW_DEBUG:
                colourBegin = text_format.WHITE
                if appendTypeName:
                    colourBegin += 'Debug: '
            else:
                colourBegin = ''
            colourEnd = '' if colourBegin == '' else '\033[0m'
        except AttributeError:  # Not the original stdout that has not implemented that function :) :) :)
            colourBegin = ''
            colourEnd = ''

        if show_type in SHOW_CURRENT:
            if SHOW_LOGS in SHOW_CURRENT:
                file, method, line = getLineInfo(2)
                logstr = "\t[File: {}, Line: {}, Method: {}]".format(file, line, method)
            else:
                logstr = ""
            print(colourBegin + str(theStr) + colourEnd + logstr, end=end)
    return


def universalPath(thePath):
    return os.path.abspath(thePath)


def add_suffix_to_path(thePath, suffix):
    head, tail = os.path.split(thePath)
    base_name, extension = os.path.splitext(tail)
    newPath = head + '/' + base_name + suffix + extension
    return newPath


def get_object_attrs(obj):
    try:
        return obj.__dict__
    except AttributeError:
        dico = {}
        try:
            for attr in obj.__slots__:
                dico[attr] = getattr(obj, attr)
        except AttributeError:
            pass
        # return {attr: getattr(obj, attr) for attr in obj.__slots__}
        return dico


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')  # ex: "a.b.c" -> pre = a.b, ; post = c

    if pre:
        obj_returned = rgetattr(obj, pre)  # , checkIndices=False)
    else:
        obj_returned = obj

    splitted = post.split('[')
    index_end_list = []
    char_begin = attr
    if len(splitted) > 1:
        char_begin = splitted[0]
        for i in range(1, len(splitted)):
            index_end_list.append(splitted[i].replace(']', '').replace("'", ''))

    if len(index_end_list):
        curr_nested_obj = obj_returned
        for index in range(len(index_end_list) - 1):
            try:
                curr_nested_obj = curr_nested_obj[index_end_list[index]]
            except (KeyError, TypeError, IndexError):
                curr_nested_obj = curr_nested_obj[int(index_end_list[index])]

        try:
            getattr(curr_nested_obj, char_begin)[index_end_list[-1]] = val
        except (KeyError, TypeError, IndexError):
            getattr(curr_nested_obj, char_begin)[int(index_end_list[-1])] = val
    else:
        setattr(obj_returned, post, val)


def rgetattr(obj, attr):
    """
    Recursively get an attribute from object. Extends getattr method

    :param obj: object
    :param attr: attribute to get
    :return:
    """
    attributes = attr.split('.')
    curr_object = obj
    for attribute in attributes:
        # Get end parentheses
        list_indices = []
        splitted = attribute.split('[')
        if not splitted:
            splitted = [attribute]

        curr_object = getattr(curr_object, splitted[0])
        if len(splitted) > 1:
            for i in range(1, len(splitted)):
                list_indices.append(splitted[i].replace(']', '').replace("'", ''))

        for item in list_indices:
            try:
                curr_object = curr_object[item]
            except (KeyError, TypeError, IndexError):
                curr_object = curr_object[int(item)]
    return curr_object


def indentParagraph(text_in, indent_level=1):
    rowsP = text_in.split("\n")
    if rowsP[-1] == '':
        rowsP = rowsP[0:-1]
    Pout = ''
    space = ''
    for i in range(indent_level):
        space += '\t'
    for element in rowsP:
        Pout += space + element + '\n'
    return Pout


# def from_scattered_to_surf(dataX, dataY, dataZ, nPoints):
#     X = np.arange(min(dataX), max(dataX), (max(dataX)-min(dataX))/nPoints)
#     Y = np.arange(min(dataY), max(dataY), (max(dataY)-min(dataY))/nPoints)
#     X, Y = np.meshgrid(X, Y)
#     Z = griddata((dataX, dataY), dataZ, (X, Y), method='linear')
#     return X, Y, Z


def truncate(theStr, truncsize):
    return theStr[:truncsize] + (theStr[truncsize:] and '..')


def get_recursive_attrs(theObject, max_recursion_level=2):
    def _all_attr(_theObject, _max_recursion_level, curr_level, prefix=""):
        temp = vars(_theObject)
        list_attributes = []
        object_keys = list()
        variable_keys = list()
        list_keys = list()

        for _attribute in temp:
            _theObject = temp[_attribute]
            if getattr(_theObject, '__dict__', None) is not None:
                object_keys.append(_attribute)
            else:
                if isinstance(_theObject, list):
                    list_keys.append(_attribute)
                else:
                    variable_keys.append(_attribute)
        for _attribute in variable_keys:
            list_attributes.append("{}{}".format(prefix, _attribute))

        for _attribute in list_keys:
            theList = temp[_attribute]

            for i, item in enumerate(theList):
                prefix_list = "{}{}[{}]".format(prefix, _attribute, i)
                list_attributes.append(prefix_list)

                if getattr(item, '__dict__', None) is not None:  # Object
                    list_attributes += _all_attr(item, _max_recursion_level, curr_level + 1, prefix="{}.".format(prefix_list))

        if curr_level >= _max_recursion_level:
            return list_attributes
        else:
            for key in object_keys:
                _theObject = temp[key]
                list_attributes += _all_attr(_theObject, _max_recursion_level, curr_level + 1, prefix="{}.".format(key))
        return list_attributes
    return _all_attr(theObject, max_recursion_level, 0)


def str_all_attr(theObject, max_recursion_level):
    def set_attribute_color(strAttribute, level):
        if level == 0:
            color = text_format.BLUE + text_format.BOLD
        elif level == 1:
            color = text_format.GREEN
        else:
            color = text_format.DARKCYAN
        return color + strAttribute + text_format.END

    def _str_all_attr(_theObject, _max_recursion_level, curr_level):
        temp = vars(_theObject)
        theStr = ''
        object_keys = list()
        variable_keys = list()
        list_keys = list()
        truncsize = 99999999999999999999
        for key in temp:
            _theObject = temp[key]
            if getattr(_theObject, '__dict__', None) is not None:
                object_keys.append(key)
            else:
                if isinstance(_theObject, list):
                    list_keys.append(key)
                else:
                    variable_keys.append(key)
        for key in variable_keys:
            theVariable = temp[key]
            theStr += set_attribute_color(key, curr_level) + ' : ' + set_attribute_color(truncate(str(theVariable), truncsize), curr_level) + '\n'

        for key in list_keys:
            theList = temp[key]
            theStr += set_attribute_color(key, curr_level) + '\t:\t'
            for index, item in enumerate(theList):
                if getattr(item, '__dict__', None) is not None:
                    if index == 0:
                        theStr += '\n'
                    theStr += indentParagraph("Item " + str(index) + " -", 1)
                    theStr += indentParagraph(_str_all_attr(item, _max_recursion_level, curr_level + 1), 2)
                else:
                    theStr += truncate(str(item), truncsize) + ', '
                    if theStr.endswith('.., '):
                        break

            theStr += '\n'

        if curr_level >= _max_recursion_level:
            return theStr
        else:
            for key in object_keys:
                _theObject = temp[key]
                theStr += set_attribute_color(key, curr_level) + ":\n"
                theStr += indentParagraph(_str_all_attr(_theObject, _max_recursion_level, curr_level + 1), 1)
        return theStr

    return _str_all_attr(theObject, max_recursion_level, 0)


def get_2D_pareto(xList, yList, max_X=True, max_Y=True):
    coef_x = 1
    coef_y = 1
    if max_X:
        coef_x = -1
    if max_Y:
        coef_y = -1
    # assign all in new array and ignore values
    mapping = []
    coords = []
    for i in range(len(xList)):
        if not np.isnan(xList[i]) and not np.isnan(yList[i]):
            coords.append([coef_x * xList[i], coef_y * yList[i]])
            mapping.append(i)

    costs = np.array(coords)
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)  # Keep any point with a lower cost
            is_efficient[i] = True  # And keep self
    # Create new array
    newx = []
    newy = []
    indices = []
    for index, isPareto in enumerate(is_efficient):
        if isPareto:
            goodIndex = mapping[index]
            newx.append(xList[goodIndex])
            newy.append(yList[goodIndex])
            indices.append(goodIndex)
    return newx, newy, indices


def get_ND_pareto(objectives_list, are_maxobjectives_list=None):
    """
    Return the N-D pareto front

    :param objectives_list: list of list of objectives: example [[0,1], [1,1], [2,2]]
    :param are_maxobjectives_list: for each objective, tells if they are to be maximized or not: example [True, False]. Default: False
    :return: extracted_pareto, indices: list of [x, y, ...] points forming the pareto front, and list of the indices of these points from the base list.
    """
    numberOfObjectives = len(objectives_list[0])
    if are_maxobjectives_list is None:
        are_maxobjectives_list = [False] * numberOfObjectives

    coef_list = [-1 if isMaxObjective else 1 for isMaxObjective in are_maxobjectives_list]

    # assign all in new array and ignore values
    mapping = []
    coords = []

    for index_objective, objectives in enumerate(objectives_list):
        mustAdd = True
        for objective in objectives:
            if np.isnan(objective):
                mustAdd = False
        if mustAdd:
            coords.append([coef_list[i] * objectives[i] for i in range(numberOfObjectives)])
            mapping.append(index_objective)

    costs = np.array(coords)
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)  # Keep any point with a lower cost
            is_efficient[i] = True  # And keep self
    # Create new array
    extracted_pareto = list()
    indices = []
    for index, isPareto in enumerate(is_efficient):
        if isPareto:
            goodIndex = mapping[index]
            extracted_pareto.append(objectives_list[goodIndex])
            indices.append(goodIndex)
    return extracted_pareto, indices


def delete_indices_from_list(indices, theList):
    """
    Delete elements from list at indices
    :param indices: list
    :param theList: list
    """
    sorted_indices = list(dict.fromkeys(list(np.sort(indices))))
    sorted_indices.reverse()
    for index in sorted_indices:
        del theList[index]


def merge_two_dicts(dict1, dict2):
    z = dict1.copy()
    z.update(dict2)
    return z


def deep_sizeof(obj):
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        return size + sum(map(deep_sizeof, obj.keys())) + sum(map(deep_sizeof, obj.values()))
    if isinstance(obj, (list, tuple, set, frozenset)):
        return size + sum(map(deep_sizeof, obj))
    return size


def order_lists(ref_list, linked_list):
    return map(list, zip(*sorted(zip(ref_list, linked_list), key=lambda x: x[0])))

