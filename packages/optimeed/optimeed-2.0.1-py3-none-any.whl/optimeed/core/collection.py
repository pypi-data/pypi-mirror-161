import copy
import json
import os
from abc import abstractmethod, ABCMeta
from threading import Timer, Lock

from optimeed.core.tools import getPath_workspace
from .myjson import obj_to_json, json_to_obj, json_to_obj_safe, encode_str_json, decode_str_json, get_json_module_tree_from_dict, MODULE_TAG, CLASS_TAG
from .tools import indentParagraph, rgetattr, printIfShown, SHOW_WARNING, SHOW_DEBUG, SHOW_INFO, SHOW_ERROR, delete_indices_from_list
import re
import inspect
from shutil import rmtree
from math import floor, ceil
import linecache


class SingleObjectSaveLoad:
    @staticmethod
    def load(filename):
        with open(filename, "r") as f:
            return json_to_obj(json.load(f))

    @staticmethod
    def save(theObject, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(obj_to_json(theObject)))


class DataStruct_Interface(metaclass=ABCMeta):

    @abstractmethod
    def save(self, filename):
        """Save the datastructure to filename"""
        pass

    @abstractmethod
    def clone(self, filename):
        """Clone the datastructure to a new location"""
        pass

    @staticmethod
    @abstractmethod
    def load(filename, **kwargs):
        """Load the datastructure from filename"""
        pass

    @staticmethod
    def get_extension():
        """File extension used for datastructure"""
        return ".json"

    def __str__(self):
        return "DataStruct"


class ListDataStruct_Interface(DataStruct_Interface, metaclass=ABCMeta):
    @abstractmethod
    def add_data(self, data_in):
        pass

    @abstractmethod
    def get_data_at_index(self, index):
        pass

    @abstractmethod
    def get_data_generator(self):
        pass

    @abstractmethod
    def delete_points_at_indices(self, indices):
        """
        Delete several elements from the Collection

        :param indices: list of indices to delete
        """
        pass

    @abstractmethod
    def get_nbr_elements(self):
        """

        :return: the number of elements contained inside the structure
        """
        pass

    @abstractmethod
    def extract_collection_from_indices(self, theIndices):
        """
        Extract data from the collection at specific indices, and return it as new collection

        :param theIndices:
        :return: A new collection
        """
        pass

    @staticmethod
    def _recursive_apply_moduleTree(nestedTree, nestedObject, raiseError=False):
        for key in nestedTree:
            if key == CLASS_TAG or key == MODULE_TAG:
                try:
                    nestedObject[key] = nestedTree[key]
                except TypeError as e:
                    printIfShown("(following error when loading, might come from numpy elementary types or 'null' values) {}".format(nestedTree, e), SHOW_DEBUG)
                    if raiseError:
                        raise
            else:
                if isinstance(nestedObject, dict):
                    ListDataStruct._recursive_apply_moduleTree(nestedTree[key], nestedObject[key])

    @staticmethod
    def _jsondata_to_obj(item, theClass=None):
        return json_to_obj(item) if theClass is None else json_to_obj_safe(item, theClass)

    def get_list_attributes(self, attributeName):
        """
        Get the value of attributeName of all the data in the Collection

        :param attributeName: string (name of the attribute to get)
        :return: list
        """
        if not attributeName:
            return list()
        return [rgetattr(data, attributeName) for data in self.get_data_generator()]


class AutosaveStruct:
    """Structure that provides automated save of DataStructures"""

    def __init__(self, dataStruct, filename='', change_filename_if_exists=True):
        if not filename:
            self.filename = getPath_workspace() + '/default_collection'
        else:
            self.filename = os.path.abspath(filename)

        self.theDataStruct = dataStruct

        self.set_filename(self.filename, change_filename_if_exists)
        self.timer = None

    def __str__(self):
        return str(self.theDataStruct)

    def get_filename(self):
        """Get set filename"""
        return self.filename

    def set_filename(self, filename, change_filename_if_exists):
        """

        :param filename: Filename to set
        :param change_filename_if_exists: If already exists, create a new filename
        """
        if not filename.endswith(self.theDataStruct.get_extension()):
            filename += self.theDataStruct.get_extension()

        if change_filename_if_exists:
            curr_index = 1
            head, tail = os.path.split(filename)
            base_name = os.path.splitext(tail)[0]
            while os.path.exists(filename):
                filename = head + '/' + base_name + '_' + str(curr_index) + self.theDataStruct.get_extension()
                curr_index += 1
        self.filename = filename

    def stop_autosave(self):
        """Stop autosave"""
        if self.timer is not None:
            self.timer.cancel()

    def start_autosave(self, timer_autosave, safe_save=True):
        """Start autosave"""
        self.save(safe_save=safe_save)
        if timer_autosave > 0:
            self.timer = Timer(timer_autosave, lambda: self.start_autosave(timer_autosave, safe_save=safe_save))
            self.timer.daemon = True
            self.timer.start()

    def save(self, safe_save=True):
        """Save"""
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))

        if os.path.exists(self.filename) and safe_save:
            temp_file = self.filename + 'temp'
            self.theDataStruct.save(temp_file)
            try:
                os.replace(temp_file, self.filename)
            except FileNotFoundError:
                pass
        else:
            self.theDataStruct.save(self.filename)

    def get_datastruct(self):
        """Return :class:'~DataStruct_Interface'"""
        return self.theDataStruct

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["timer"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.timer = None


class ListDataStruct(ListDataStruct_Interface):
    _DATA_STR = "data"
    _COMPRESS_SAVE_STR = "module_tree"

    def __init__(self, compress_save=False):
        """
        Structure of data containing a single list of objects.

        :param compress_save: Set to True if all the data have the same class and module names, so that emitted file is more efficient
        """
        super().__init__()
        self.theData = list()
        self.compress_save = compress_save
        self.json_module_tree = ''

    def __len__(self):
        return self.get_length()

    def get_length(self):
        return len(self.theData)

    def clone(self, filename):
        self.save(filename)  # Same behaviour as save: all the memory is dumped

    def save(self, filename):
        """Save data using json format. The data to be saved are automatically detected, see :meth:`~optimeed.core.myjson.obj_to_json` """
        theStr = self._format_str_save()
        with open(filename, "w", encoding='utf-8') as f:
            f.write(theStr)

    def extract_collection_from_indices(self, indices):
        """Extract data from the collection at specific indices, and return it as new collection"""
        new_collection = ListDataStruct()
        for index in indices:
            new_collection.add_data(self.get_data_at_index(index))
        return new_collection

    def _format_str_save(self):
        """Save data using json format. The data to be saved are automatically detected, see :meth:`~optimeed.core.myjson.obj_to_json` """
        # Header
        theStr = "{\n"

        theStr += '\t"{}": \n{}'.format(ListDataStruct._DATA_STR, indentParagraph(self._format_data_lines(), 3))  # Core lines

        # if compress save: add module and class tree at end of file
        if self.compress_save:
            self._get_json_module_tree()
            theStr += '\t,"{}": {}\n'.format(ListDataStruct._COMPRESS_SAVE_STR, self.json_module_tree)
        theStr += "}"
        return theStr

    def _format_data_lines(self):
        # Format data as json object
        listStr = "[\n"
        has_previous_element = False
        for k, item in enumerate(self.get_data_generator()):
            obj_str = ""

            if has_previous_element:  # Add separator from previous element
                obj_str += ",\n"

            obj_str += "\t" + json.dumps(obj_to_json(item))
            # if compress save: remove all information relative to module and class
            if self.compress_save:
                obj_str = re.sub("\s*\"__module__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', obj_str)
                obj_str = re.sub("\s*\"__class__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', obj_str)

            listStr += obj_str

            has_previous_element = True
        listStr += "\n]"

        return listStr

    def _get_json_module_tree(self):
        if not self.json_module_tree and len(self.theData):
            new_module_tree = json.dumps(get_json_module_tree_from_dict(obj_to_json(self.theData[-1])))
            if len(new_module_tree) > len(self.json_module_tree):
                self.json_module_tree = new_module_tree

    @staticmethod
    def load(filename, theClass=None):
        """
        Load the file filename.

        :param filename: file to load
        :param theClass: optional. Can be used to fix unpickling errors.
        :return: self-like object
        """
        if filename:
            if not os.path.splitext(filename)[-1].lower():
                filename += ListDataStruct.get_extension()

            try:
                newStruct = ListDataStruct()
                with open(filename, 'r', encoding="utf-8", newline="\n") as f:
                    theDict = json.load(f)

                # If datastruct has been compressed,
                try:
                    theModuleTree = theDict[ListDataStruct._COMPRESS_SAVE_STR]
                    for item in theDict[ListDataStruct._DATA_STR]:
                        ListDataStruct._recursive_apply_moduleTree(theModuleTree, item)
                except KeyError:
                    pass

                if theClass is not None:
                    theData = [json_to_obj_safe(item, theClass) for item in theDict[ListDataStruct._DATA_STR]]
                else:
                    theData = [json_to_obj(item) for item in theDict[ListDataStruct._DATA_STR]]
                newStruct.set_data(theData)
                return newStruct
            # except TypeError as e:
            # printIfShown("{}, recommended to use theclass keyword in method load".format(e), SHOW_WARNING)
            except OSError:
                printIfShown("Could not read file ! " + filename, SHOW_WARNING)
            except EOFError:
                printIfShown("File empty ! " + filename, SHOW_WARNING)
        else:
            printIfShown("INVALID COLLECTION FILENAME: " + filename, SHOW_WARNING)

    def add_data(self, data_in):
        """Add a data to the list"""
        self.theData.append(copy.deepcopy(data_in))

    def get_data(self):
        """Get full list of datas"""
        printIfShown("get_data() deprecated! Please use get_data_at_index or get_data_generator whenever possible", SHOW_WARNING)
        inspect.stack()
        return self.theData

    def get_data_generator(self):
        """Get a generator to all the data stored"""
        for k in range(len(self)):
            yield self.get_data_at_index(k)

    def get_data_at_index(self, index):
        return self.theData[index]

    def set_data(self, theData):
        """Set full list of datas"""
        self.theData = theData

    def set_data_at_index(self, data_in, index):
        """Replace data at specific index"""
        self.theData[index] = data_in

    # def set_attribute_data(self, the_attribute, the_value):
    #     """Set attribute to all data"""
    #     for item in self.get_data():
    #         setattr(item, the_attribute, the_value)
    #
    # def set_attribute_equation(self, attribute_name, equation_str):
    #     """
    #     Advanced method to set the value of attribute_name from equation_str
    #
    #     :param attribute_name: string (name of the attribute to set)
    #     :param equation_str: formatted equation, check :meth:`~optimeed.core.CommonFunctions_Library.applyEquation`
    #     :return:
    #     """
    #     for item in self.get_data():
    #         setattr(item, attribute_name, applyEquation(item, equation_str))

    def reset_data(self):
        self.theData = list()

    def delete_points_at_indices(self, indices):
        """
        Delete several elements from the Collection

        :param indices: list of indices to delete
        """
        for index in sorted(indices, reverse=True):
            del self.theData[index]

    def merge(self, collection):
        """
        Merge a collection with the current collection

        :param collection: :class:`~optimeed.core.Collection.Collection` to merge
        """
        for item in collection.get_data():
            self.add_data(item)

    def get_nbr_elements(self):
        return len(self.theData)


theLock = Lock()


class Performance_ListDataStruct(ListDataStruct_Interface):
    _NBR_ELEMENTS = "nbr_elements"
    _STACK_SIZE = "stack_size"
    _COMPRESS_SAVE_STR = "module_tree"

    def __init__(self, stack_size=500):
        """
        This class is an extension to the classical :class:`ListDataStruct`.
        It is designed to be well suited to opimization: split huge files into smaller ones, efficient CPU usage, efficient RAM usage.

        :param stack_size: Number of elements to store on each file
        """
        super().__init__()
        self.compress_save = True
        self.data_buffer = list()
        self.curr_elements_in_last_file = 0
        self.curr_number_of_files = 1
        self.has_been_initialized = False
        self.stack_size = stack_size
        self.json_module_tree = ''
        self._mainfilename = ''

    def _initialize(self, filename):
        rmtree(self._get_subfolder_path(filename), ignore_errors=True)
        os.makedirs(self._get_subfolder_path(filename))
        self._mainfilename = filename
        self.has_been_initialized = True

    @staticmethod
    def _get_subfolder_path(main_filename):
        folder_main = os.path.dirname(main_filename)
        filename = os.path.basename(main_filename)
        sub_folder, _ = os.path.splitext(filename)
        sub_folder += '_datafiles'
        return os.path.join(folder_main, sub_folder)

    def _get_list_from_file(self, filenumber):
        for file in range(filenumber, self.curr_number_of_files):
            with open(self._get_path_from_filenumber(self._mainfilename, filenumber)) as f:
                return f.read().splitlines()

    @staticmethod
    def _get_path_from_filenumber(main_filename, filenumber):
        return os.path.join(Performance_ListDataStruct._get_subfolder_path(main_filename), "data_{}".format(filenumber))

    @staticmethod
    def split_list(numb_in_list, stack_size, thing_to_hash):
        # Returns [index_begin, index_end, lefts] to hash
        item_put_in_list = stack_size - numb_in_list
        item_still_to_be_put = len(thing_to_hash)
        max_number_to_put_in_list = min(item_still_to_be_put, item_put_in_list)
        hashed = [(0, max_number_to_put_in_list, numb_in_list + max_number_to_put_in_list)]
        if len(thing_to_hash) > item_put_in_list:
            returned_list = Performance_ListDataStruct.split_list(0, stack_size, thing_to_hash[item_put_in_list:])
            for k, item in enumerate(returned_list):
                index_begin_next, index_end_next, max_number_to_put_in_list = item
                mapped_index_begin = index_begin_next + item_put_in_list
                mapped_index_end = index_end_next + item_put_in_list
                returned_list[k] = (mapped_index_begin, mapped_index_end, max_number_to_put_in_list)
            hashed.extend(returned_list)
            return hashed
        return hashed

    def extract_collection_from_indices(self, indices):
        """Extract data from the collection at specific indices, and return it as new collection"""
        new_collection = Performance_ListDataStruct()
        new_collection.json_module_tree = self.json_module_tree

        for index in indices:
            new_collection.data_buffer.append(self._get_json_str_at_index(index))
        return new_collection

    def clone(self, filename):
        self.save(filename)  # Dump buffer to files
        theListDataCollection = self.load_as_listdatastruct(self._mainfilename)  # Recover files content
        theListDataCollection.clone(filename)  # Save it

    def _get_str_mainfile(self):
        theDict = {self._NBR_ELEMENTS: self.get_total_nbr_elements(False),
                   self._STACK_SIZE: self.stack_size,
                   self._COMPRESS_SAVE_STR: self.json_module_tree}
        return json.dumps(theDict, indent=4)

    def get_total_nbr_elements(self, count_unsaved=True):
        nbr_elements_full_files = max(0, self.stack_size * (self.curr_number_of_files-1))
        nbr_elements_last_file = self.curr_elements_in_last_file
        unsaved_elements = len(self.data_buffer) if count_unsaved else 0
        return nbr_elements_full_files + nbr_elements_last_file + unsaved_elements

    def add_data(self, theData):
        theDict = obj_to_json(theData)
        theStr = json.dumps(theDict)
        if self.compress_save:
            theStr = re.sub("\s*\"__module__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', theStr)
            theStr = re.sub("\s*\"__class__\" *: *(\"(.*?)\"(,|\s|)|\s*\{(.*?)\}(,|\s|))", '', theStr)
            self._save_moduletree(theDict)
        global theLock
        with theLock:
            self.data_buffer.append(theStr)

    def _save_moduletree(self, theDict):
        if not self.json_module_tree:
            if not theDict == "null":
                self.json_module_tree = json.dumps(get_json_module_tree_from_dict(theDict))

    def _map_index_to_file(self, index):
        filenumber = int(floor(index / self.stack_size))
        linenumber = index - filenumber * self.stack_size
        return filenumber, linenumber

    def _get_json_str_at_index(self, index, refresh_cache=False):
        """Internal method to return the json string at index"""
        if self.get_total_nbr_elements(count_unsaved=True) < index:
            raise IndexError
        elif index >= self.get_total_nbr_elements(count_unsaved=False):  # data in buffer
            json_str = self.data_buffer[index - self.get_total_nbr_elements(count_unsaved=False)]
        else:  # data in files
            filenumber, linenumber = self._map_index_to_file(index)
            filename = self._get_path_from_filenumber(self._mainfilename, filenumber)
            if refresh_cache:
                linecache.checkcache(filename)
            json_str = linecache.getline(filename, linenumber + 1).strip()  # Open file and retrieve specific line
        return json_str

    def reorder(self, permutations):
        """
        Reorder collection accordingly to permutations.
        E.G, list_of_indices = [0,3,2] with collection elems [0,2,1] => collection elems = [0,2,3]
        :param permutations:
        :return: /
        """
        nbr_elems = self.get_total_nbr_elements(count_unsaved=True)
        all_data_str = [""]*nbr_elems
        for index in range(nbr_elems):
            all_data_str[index] = self._get_json_str_at_index(index)

        indices, ordered_all_data_str = (list(t) for t in zip(*sorted(zip(permutations, all_data_str))))
        self.data_buffer = ordered_all_data_str
        self.curr_elements_in_last_file = 0
        self.curr_number_of_files = 1
        self.has_been_initialized = False

    def get_data_at_index(self, index, ignore_attributes=None, none_if_error=False):
        """

        Args:
            index: index to get
            ignore_attributes: ignore attributes to deserialize (list)

        Returns:

        """
        try:
            json_str = self._get_json_str_at_index(index)
            if not json_str:
                json_str = self._get_json_str_at_index(index, refresh_cache=True)

            item = json.loads(json_str)
            ListDataStruct._recursive_apply_moduleTree(json.loads(self.json_module_tree), item, raiseError=none_if_error)

            if ignore_attributes is not None:
                for attribute in ignore_attributes:
                    item.pop(attribute, None)
        except TypeError:
            return None
        return json_to_obj(item)

    # LOAD/SAVES
    def save(self, filename):
        global theLock
        with theLock:
            if not len(self.data_buffer):
                return

            if not self.has_been_initialized:
                self._initialize(filename)

            # Hash data to write
            splitlists = self.split_list(self.curr_elements_in_last_file, self.stack_size, self.data_buffer)
            for index_begin, index_end, numberofelem in splitlists:
                data_to_write = self.data_buffer[index_begin:index_end]
                self.curr_elements_in_last_file = numberofelem
                if data_to_write:
                    theStr = '\n'.join(data_to_write)
                    if os.path.exists(self._get_path_from_filenumber(filename, self.curr_number_of_files - 1)):
                        theStr = "\n" + theStr
                    with open(self._get_path_from_filenumber(filename, self.curr_number_of_files - 1), 'a+') as f:
                        f.write(theStr)

                # Increment number of elements or files
                if numberofelem == self.stack_size:
                    self.curr_number_of_files += 1
                    self.curr_elements_in_last_file = 0
                else:
                    self.curr_elements_in_last_file = numberofelem

            #  Write main file
            with open(filename, "w") as f:
                f.write(self._get_str_mainfile())
            self.data_buffer = list()

    @staticmethod
    def load(filename, **kwargs):
        with open(filename, 'r', encoding="utf-8") as f:
            theDict = json.load(f)
        newStruct = Performance_ListDataStruct()
        newStruct.stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]

        nbr_elements = theDict[Performance_ListDataStruct._NBR_ELEMENTS]
        number_of_files = int(ceil(nbr_elements/newStruct.stack_size))
        number_of_elements_last_file = nbr_elements - (number_of_files-1)*newStruct.stack_size

        newStruct.stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]
        newStruct.curr_elements_in_last_file = number_of_elements_last_file
        newStruct.curr_number_of_files = number_of_files
        newStruct.has_been_initialized = True
        newStruct.json_module_tree = theDict[Performance_ListDataStruct._COMPRESS_SAVE_STR]
        newStruct._mainfilename = filename
        return newStruct

    @staticmethod
    def load_as_listdatastruct(filename, **kwargs):
        """Return :class:`ListDataStruct`. Two-steps:
        1) Save temporary file formated like ListDataStruct
        2) Use ListDataStruct load function"""
        # 1)
        with open(filename, 'r', encoding="utf-8", newline='\n') as f:
            theDict = json.load(f)

        stack_size = theDict[Performance_ListDataStruct._STACK_SIZE]
        nbr_elements = theDict[Performance_ListDataStruct._NBR_ELEMENTS]
        number_of_files = int(ceil(nbr_elements/stack_size))
        lines = list()
        for file_number in range(number_of_files):
            with open(Performance_ListDataStruct._get_path_from_filenumber(filename, file_number), 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if nbr_elements <= len(lines):
                        break
                    line = line.rstrip()
                    if not line:
                        continue
                    if line.isprintable():
                        lines.append(line)
                    else:
                        printIfShown("Removed line {}".format(line), SHOW_WARNING)
                # lines += list(filter(None, (line.rstrip() for line in f)))  # Non-blank lines
            printIfShown("loaded {} %".format(int(file_number/number_of_files*100)), SHOW_INFO)
        theStr = ''
        theStr += '{\n'
        #  noinspection PyProtectedMember
        theStr += '\t"{}": {},'.format(ListDataStruct._COMPRESS_SAVE_STR, theDict[Performance_ListDataStruct._COMPRESS_SAVE_STR])
        #  noinspection PyProtectedMember
        theStr += '\t"{}": [\n{}\n]'.format(ListDataStruct._DATA_STR, "\n,".join(lines))
        theStr += '}'
        tempfile = filename + "_temp"
        with open(tempfile, "w", encoding="utf-8") as f:
            f.write(theStr)
        # 2)
        theDataStruct = ListDataStruct.load(tempfile, **kwargs)
        os.remove(tempfile)
        printIfShown("Done loading", SHOW_INFO)
        return theDataStruct

    def get_data_generator(self, **kwargs):
        """Get a generator to all the data stored"""
        for k in range(self.get_total_nbr_elements(count_unsaved=True)):
            yield self.get_data_at_index(k, kwargs)

    def get_nbr_elements(self):
        return self.get_total_nbr_elements(count_unsaved=True)

    def set_data_at_index(self, data_in, index):
        """Replace data at specific index"""
        self.set_data_at_indices([data_in], [index])

    def set_data_at_indices(self, data_list, indices):
        """
        Replace datas at specific indices
        :param data_list: list of objects to set to the collection, at specific indices
        :param indices: list of indices
        :return:
        """
        indices, data_list = (list(t) for t in zip(*sorted(zip(indices, data_list))))

        if len(data_list) != len(indices):
            printIfShown("Unconsistent length in set_data_at_indices", SHOW_ERROR)
        else:
            if len(self.data_buffer):
                printIfShown("Buffer of collection is not empty. Please use save function first !", SHOW_ERROR)
            # First, convert data to something readible
            self.data_buffer = list()
            for data in data_list:
                self.add_data(data)
            previous_filenumber = -1

            data = list()
            for i, index in enumerate(indices):
                filenumber, _ = self._map_index_to_file(index)
                if filenumber != previous_filenumber:
                    # Started new file => save previous data
                    if previous_filenumber >= 0:
                        with open(self._get_path_from_filenumber(self._mainfilename, previous_filenumber), "w") as f:
                            f.write('\n'.join(data))
                    # And load new file
                    data = self._get_list_from_file(filenumber)
                    previous_filenumber = filenumber

                start_index = filenumber * self.stack_size
                data[index - start_index] = self.data_buffer[i]
            # Final save
            with open(self._get_path_from_filenumber(self._mainfilename, previous_filenumber), "w") as f:
                f.write('\n'.join(data))
            self.data_buffer = list()

    def delete_points_at_indices(self, indices):
        if not self.has_been_initialized:
            for index in sorted(indices, reverse=True):
                del self.data_buffer[index]
            return

        if len(self.data_buffer):
            printIfShown("Buffer of collection is not empty. Please use save function first !", SHOW_ERROR)

        previous_filenumber = self.curr_number_of_files

        first_index = min(indices)
        start_filenumber, _ = self._map_index_to_file(first_index)
        start_index = start_filenumber * self.stack_size

        all_data = list()
        for filenumber in range(start_filenumber, self.curr_number_of_files):
            try:
                all_data += self._get_list_from_file(filenumber)
            except FileNotFoundError:
                pass

        delete_indices_from_list([index - start_index for index in indices], all_data)
        self.data_buffer = all_data
        self.curr_elements_in_last_file = 0
        self.curr_number_of_files = start_filenumber+1

        # Delete previous files
        for filenumber in range(start_filenumber, previous_filenumber):
            if os.path.exists(self._get_path_from_filenumber(self._mainfilename, filenumber)):
                os.remove(self._get_path_from_filenumber(self._mainfilename, filenumber))

        # Save
        self.save(self._mainfilename)
