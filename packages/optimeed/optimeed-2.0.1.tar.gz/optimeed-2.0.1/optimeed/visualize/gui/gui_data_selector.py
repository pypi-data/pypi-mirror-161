from PyQt5 import QtWidgets  #, QtCore
# from optimeed.core.tools import rgetattr, indentParagraph
import sys
# import traceback
from abc import ABCMeta, abstractmethod

#
# if QtWidgets.QApplication.instance() is None:
#     app = QtWidgets.QApplication(sys.argv)  # must initialize only once


class Action_on_selector_update(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self):
        """Get the name of the action

        :return: string
        """
        pass

    @abstractmethod
    def selector_updated(self, selection_name, the_collection, selected_indices, not_selected_indices):
        """
        Action to perform once the data have been selected
        :param selection_name: name of the selection (deprecated ?)
        :param the_collection: the collection
        :param selected_indices: indices of selected data
        :param not_selected_indices: indices of data NOT selected
        :return: identifier that can later be used with cancel_selector
        """
        pass

    @abstractmethod
    def cancel_selector(self, selection_identifier):
        """
        Action to perform when data stopped being selected
        :param selection_identifier: identifier that was returned by selector_updated
        :return:
        """
        pass
    
# 
# class Attribute_selector:
#     # Contains min max values for either list or scalar:
#     # If list, displays from self.children_list [Attribute_selector]
#     # Otherwise displays from self.min/max_value_box
# 
#     def __init__(self, attribute_name, value):
#         self.attribute_name = attribute_name
#         self.value = value
#         self.min_value_box = None
#         self.max_value_box = None
#         self.children_list = []
# 
#     def add_child(self, child):
#         self.children_list.append(child)
# 
#     def get_children(self):
#         return self.children_list
# 
#     def get_name(self):
#         return '{:.50}'.format(self.attribute_name)
# 
#     def get_min_max_attributes(self):
#         min_max_attributes = []
# 
#         def _get_min_max_attributes(the_attribute_selector, min_max_attr):
#             if not len(the_attribute_selector.children_list):
#                 attribute_min_valid = True
#                 try:
#                     min_value = float(the_attribute_selector.min_value_box.text())
#                 except ValueError:
#                     min_value = float("-inf")
#                     attribute_min_valid = False
# 
#                 attribute_max_valid = True
#                 try:
#                     max_value = float(the_attribute_selector.max_value_box.text())
#                 except ValueError:
#                     max_value = float("inf")
#                     attribute_max_valid = False
# 
#                 if attribute_max_valid or attribute_min_valid:
#                     min_max_attr.append((min_value, max_value, the_attribute_selector.attribute_name))
#             else:
#                 for child in the_attribute_selector.get_children():
#                     _get_min_max_attributes(child, min_max_attr)
# 
#         _get_min_max_attributes(self, min_max_attributes)
#         return min_max_attributes
# 
#     def __str__(self):
#         theStr = ''
#         for child in self.children_list:
#             theStr += indentParagraph(str(child), 1)
#         if not len(self.children_list):
#             theStr += self.get_name() + ': \t' + str(self.value)
#         return theStr
# 
# 
# class Container_attribute_selector:
#     def __init__(self, containerName):
#         self.children = []
#         self.containerName = containerName
#         self.attribute_selectors = []
# 
#     def add_child(self, child):
#         self.children.append(child)
# 
#     def add_attribute_selector(self, attribute_selector):
#         self.attribute_selectors.append(attribute_selector)
# 
#     def set_attribute_selectors(self, attribute_selectors):
#         self.attribute_selectors = attribute_selectors
# 
#     def get_name(self):
#         return self.containerName
# 
#     def get_children(self):
#         return self.children
# 
#     def get_attribute_selectors(self):
#         return self.attribute_selectors
# 
#     def __str__(self):
#         theStr = ''
#         for item in self.attribute_selectors:
#             theStr += str(item) + '\n'
# 
#         index = 1
#         for item in self.children:
#             theStr += str(index) + '\n'
#             theStr += indentParagraph(str(item))
#             index += 1
#         return theStr
# 
# 
# class GuiDataSelector(QtWidgets.QMainWindow):
#     def __init__(self, list_ListDataStruct_in, list_actionOnUpdate):
#         """Base on collection, display a list of variables that can be updated.
#         When the button "update" is pressed, select the datas in Collection and call the method methodToCallWhenUpdated from the actions list.
# 
#         :param list_ListDataStruct_in: (type Collection) containing the data to select
#         :param list_actionOnUpdate: list of :class:`Action_on_selector_update`
#         """
# 
#         """Store variables"""
#         self.theListDataStructs = list_ListDataStruct_in
#         self.possible_actions = list_actionOnUpdate
# 
#         """Generate GUI"""
#         super(GuiDataSelector, self).__init__()
#         self.setMinimumWidth(300)
# 
#         self.mainbox = QtWidgets.QWidget()
# 
#         scrollarea = QtWidgets.QScrollArea()
#         scrollarea.setWidget(self.mainbox)
#         scrollarea.setWidgetResizable(True)
#         scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setCentralWidget(scrollarea)
# 
#         layout = QtWidgets.QVBoxLayout(scrollarea)
#         self.mainbox.setLayout(layout)
# 
#         # Create a layout for a global name
#         self.selectionName = QtWidgets.QLineEdit("Default Name")
#         self.mainbox.layout().addWidget(self.selectionName)
# 
#         # Create a selection of actions to perform upon selection
#         comboBox = QtWidgets.QComboBox()
#         for action in self.possible_actions:
#             comboBox.addItem(action.get_name())
#         comboBox.currentIndexChanged.connect(lambda index: self.set_action_on_update(self.possible_actions[index]))
#         self.mainbox.layout().addWidget(comboBox)
#         comboBox.setCurrentIndex(0)
#         self.theActionOnUpdate = None
#         self.set_action_on_update(self.possible_actions[0])
# 
#         # For each attribute, create new layout
#         self.main_container = Container_attribute_selector('Device')
#         get_attr_object(self.main_container, self.theListDataStructs[0].get_data_at_index(0))
# 
#         def collapse(theGroupBox, theFrame):
#             if theGroupBox.isChecked():
#                 theFrame.show()
#             else:
#                 theFrame.hide()
# 
#         def create_frames(theContainer, parent_layout, curr_recursion):
#             MAX_RECURSION = 2
# 
#             theGroupBox = QtWidgets.QGroupBox(theContainer.get_name())
#             theGroupBox.setCheckable(True)
#             theGroupBox.setChecked(True)
# 
#             parent_layout.addWidget(theGroupBox)
# 
#             # Little trick here: to be able to hide only the content, put a frame in a layout in the groupbox, and hide the frame
#             new_layout_temp = QtWidgets.QVBoxLayout(theGroupBox)
#             new_frame = QtWidgets.QFrame()
#             theGroupBox.clicked.connect(lambda: collapse(theGroupBox, new_frame))
# 
#             if curr_recursion >= MAX_RECURSION:
#                 new_frame.hide()
#                 theGroupBox.setChecked(False)
#             new_layout_temp.addWidget(new_frame)
#             new_layout = QtWidgets.QVBoxLayout(new_frame)
# 
#             for attribute_selector in theContainer.get_attribute_selectors():
#                 # create
#                 horizontal_layout = QtWidgets.QHBoxLayout()
#                 new_layout.addLayout(horizontal_layout)
# 
#                 # First: label
#                 label = QtWidgets.QLabel()
#                 label.setText(attribute_selector.get_name())
#                 horizontal_layout.addWidget(label, alignment=QtCore.Qt.AlignTop)
# 
#                 vertical_layout = QtWidgets.QVBoxLayout()
#                 horizontal_layout.addLayout(vertical_layout)
# 
#                 min_value_layout = QtWidgets.QHBoxLayout()
#                 vertical_layout.addLayout(min_value_layout)
#                 min_value_layout.addStretch()
# 
#                 max_value_layout = QtWidgets.QHBoxLayout()
#                 vertical_layout.addLayout(max_value_layout)
#                 max_value_layout.addStretch()
# 
#                 separator = QtWidgets.QFrame()
#                 separator.setFrameShape(QtWidgets.QFrame.HLine)
#                 new_layout.addWidget(separator)
# 
#                 # Create buttons
#                 create_buttons(attribute_selector, min_value_layout, max_value_layout)
# 
#             for child in theContainer.get_children():
#                 create_frames(child, new_layout, curr_recursion=curr_recursion + 1)
# 
#         def create_buttons(the_attribute_selector, min_value_layout, max_value_layout):
#             if not len(the_attribute_selector.get_children()):
#                 the_attribute_selector.min_value_box = QtWidgets.QLineEdit(None)
#                 the_attribute_selector.min_value_box.setFixedWidth(50)
#                 the_attribute_selector.min_value_box.setPlaceholderText("Min")
#                 min_value_layout.addWidget(the_attribute_selector.min_value_box, alignment=QtCore.Qt.AlignLeft)
# 
#                 the_attribute_selector.max_value_box = QtWidgets.QLineEdit(None)
#                 the_attribute_selector.max_value_box.setFixedWidth(50)
#                 the_attribute_selector.max_value_box.setPlaceholderText("Max")
#                 max_value_layout.addWidget(the_attribute_selector.max_value_box, alignment=QtCore.Qt.AlignLeft)
#             else:
#                 for child in the_attribute_selector.get_children():
#                     create_buttons(child, min_value_layout, max_value_layout)
# 
#         create_frames(self.main_container, layout, 1)
# 
#         # Create a button in the window
#         dock = QtWidgets.QDockWidget(self)
#         button = QtWidgets.QPushButton('Update', self)
#         dock.setWidget(button)
#         self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)
# 
#         button.clicked.connect(self.apply_filters)
#         self.resize(self.mainbox.sizeHint())
# 
#     def apply_filters(self, _):
#         try:
#             for collection in self.theListDataStructs:
#                 selected_data_indices = []
#                 for data_index in range(len(collection)):
#                     the_item = collection.get_data_at_index(data_index)
# 
#                     if is_object_selected(self.main_container, the_item):
#                         selected_data_indices.append(data_index)
#                 self.theActionOnUpdate.selector_updated(self.selectionName.text(), collection, selected_data_indices)
#         except KeyboardInterrupt:
#             raise
#         except Exception:
#             print("Following error occurred in selector :" + traceback.format_exc())
# 
#         # textboxValue = self.textbox.text()
# 
#     def set_action_on_update(self, theAction):
#         self.theActionOnUpdate = theAction
# 
#     def run(self):
#         self.activateWindow()
#         self.show()
#         # app.exec_()
# 
# 
# def is_object_selected(container_in, object_in):
#     for attribute_selector in container_in.get_attribute_selectors():
#         min_max_attribute = attribute_selector.get_min_max_attributes()
#         for min_attr, max_attr, name_attr in min_max_attribute:
#             # Reverse boundaries if max < min
#             if min_attr > max_attr:
#                 buff = min_attr
#                 min_attr = max_attr
#                 max_attr = buff
#             # Check if item satisfies the condition
#             try:
#                 if not (min_attr <= rgetattr(object_in, name_attr) <= max_attr):
#                     return False
#             except IndexError:
#                 pass
#     return all([is_object_selected(container, rgetattr(object_in, container.get_name())) for container in container_in.get_children()])
# 
