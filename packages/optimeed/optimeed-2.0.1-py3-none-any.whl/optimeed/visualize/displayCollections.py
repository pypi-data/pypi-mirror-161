from PyQt5 import QtWidgets, uic
from optimeed.core.tools import rgetattr, get_recursive_attrs
from optimeed.core import LinkDataGraph, HowToPlotGraph
from optimeed.core import SHOW_ERROR, printIfShown
from optimeed.visualize.gui import On_select_highlight, On_select_new_trace, On_select_split_trace, guiPyqtgraph
from optimeed.visualize import widget_graphs_visual, gui_mainWindow, start_qt_mainloop
import traceback
import os


def _is_object_selected(object_in, min_max_attributes):
    for name_attr, min_attr, max_attr in min_max_attributes:
        value = rgetattr(object_in, name_attr)
        if value is None:
            return False
        type_init = type(value)

        try:
            min_attr = type_init(min_attr)
            has_min = True
        except (TypeError, ValueError):
            has_min = False
        try:
            max_attr = type_init(max_attr)
            has_max = True
        except (TypeError, ValueError):
            has_max = False

        if not (has_min or has_max):
            return False
        if not has_min:
            if rgetattr(object_in, name_attr) > type_init(max_attr):
                return False
        if not has_max:
            if rgetattr(object_in, name_attr) < type_init(min_attr):
                return False
        if not (min_attr <= value <= max_attr or max_attr <= value <= min_attr):
            return False
    return True


def _select_and_apply_action(theCollections, min_max_attributes, theAction, selectionName):
    id_selections = list()
    try:

        for collection in theCollections:
            selected_data_indices = []
            unselected_data_indices = []

            for k, data in enumerate(collection.get_data_generator()):
                if _is_object_selected(data, min_max_attributes):
                    selected_data_indices.append(k)
                else:
                    unselected_data_indices.append(k)
            id_selections.append(theAction.selector_updated(selectionName, collection, selected_data_indices, unselected_data_indices))
    except KeyboardInterrupt:
        raise
    except Exception:
        printIfShown("{}".format(traceback.format_exc()), SHOW_ERROR)
    return id_selections


class CollectionDisplayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  #
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'displayCollections_gui.ui'), self)

        # Structures
        self.howToPlot = HowToPlotGraph('', '', kwargs_graph={"is_scattered": True, "alpha": 255}, meta="")
        self.theDataLink = LinkDataGraph()
        self.theDataLink.add_graph(self.howToPlot)
        self.theWGPlot = widget_graphs_visual(self.theDataLink.get_graphs(), refresh_time=-1)
        self.window_plot = gui_mainWindow([self.theWGPlot])

        # Fill in
        possible_actions = list()
        possible_actions.append(On_select_highlight(self.theDataLink, self.theWGPlot))
        possible_actions.append(On_select_new_trace(self.theDataLink))
        possible_actions.append(On_select_split_trace(self.theDataLink))
        for action in possible_actions:
            self.selector_action.addItem(action.get_name())
        self.selector_action.setCurrentIndex(0)
        self.possible_actions = possible_actions
        self.curr_action = possible_actions[0]
        # Connect
        self.selector_action.currentIndexChanged.connect(lambda index: self.set_action_selector(self.possible_actions[index]))
        self.set_X.clicked.connect(self._set_x)
        self.set_Y.clicked.connect(self._set_y)
        self.set_Z.clicked.connect(self._set_z)

        self.selector_to.clicked.connect(self._selector_to)
        self.selector_cancel.clicked.connect(self._remove_item_selector)
        self.reset_colors.clicked.connect(self._reset_colors)
        self.items_selected.cellChanged.connect(self._apply_selector)
        self.previous_selection = list()

        # SHOW
        self.show()
        self.window_plot.show()

        self.initialized = False

    # Users functions
    def add_collection(self, theCollection, name=""):
        theIdCollection = self.theDataLink.add_collection(theCollection, {"legend": name})
        if not self.initialized:
            self._initialize(theCollection)
        return theIdCollection

    def set_shadow(self, master_collectionId, shadow_collection):
        self.theDataLink.set_shadow_collection(master_collectionId, shadow_collection)

    def remove_collection(self, theCollection):
        self.theDataLink.remove_collection(self.theDataLink.get_idcollection_from_collection(theCollection))

    def update_graphs(self):
        self.theDataLink.update_graphs()

    def set_actions_on_click(self, theActionsOnClick):
        guiPyqtgraph(self.theWGPlot, actionsOnClick=theActionsOnClick)

    @staticmethod
    def run():
        start_qt_mainloop()

    def get_datalink(self):
        return self.theDataLink

    # Others

    def _initialize(self, theCollection):
        first_data = theCollection.get_data_at_index(0)
        all_attrs = get_recursive_attrs(first_data)

        self.available_plot_data.set_list(all_attrs)
        self.items_to_select.set_entries(all_attrs)
        self.items_selected.set_entries(all_attrs, hidden=True)

        self.items_selected.myTableWidget.setHorizontalHeaderLabels(["Attribute", "Min", "Max"])
        self.items_to_select.myTableWidget.setHorizontalHeaderLabels(["Attribute", "Min", "Max"])

        self.initialized = True

    # Plot methods

    def _set_x(self):
        name = self.available_plot_data.get_name_selected()
        self.howToPlot.kwargs_graph.update({"x_label": name})
        if name is not None:
            howToPlot = self.theDataLink.get_howToPlotGraph(0)
            howToPlot.attribute_x = name
        self.update_graphs()

    def _set_y(self):
        name = self.available_plot_data.get_name_selected()
        self.howToPlot.kwargs_graph.update({"y_label": name})

        if name is not None:
            howToPlot = self.theDataLink.get_howToPlotGraph(0)
            howToPlot.attribute_y = name
        self.update_graphs()

    def _set_z(self):
        name = self.available_plot_data.get_name_selected()
        howToPlot = self.theDataLink.get_howToPlotGraph(0)

        if name is not None:
            howToPlot.meta = name
        else:
            howToPlot.meta = None
        self.update_graphs()

    # Selector methods

    def set_action_selector(self, theAction):
        self.curr_action = theAction

    def _selector_to(self):
        results, rows = self.items_to_select.get_entries_selected()
        if len(rows):
            [self.items_to_select.force_hide_row(row) for row in rows]
            [self.items_selected.remove_forced_hide_row(row) for row in rows]
            self.items_selected.blockSignals(True)
            for k, row in enumerate(rows):
                for col in [1, 2]:
                    self.items_selected.set_item(row, col, results[k][col])
            self.items_selected.blockSignals(False)

            self._apply_selector()

    def _remove_item_selector(self):
        results, rows = self.items_selected.get_entries_selected()
        if len(rows):
            [self.items_selected.force_hide_row(row) for row in rows]
            [self.items_to_select.remove_forced_hide_row(row) for row in rows]

            for k, row in enumerate(rows):
                for col in [1, 2]:
                    self.items_to_select.set_item(row, col, results[k][col])
            self._apply_selector()

    def _cancel_selector(self):
        # Automatically called by _apply_selector

        # noinspection PyBroadException
        try:
            if self.previous_selection:
                for graphId, traceId, id_selections in self.previous_selection:
                    for id_selection in id_selections:
                        self.curr_action.cancel_selector(id_selection)
                self.previous_selection = list()
        except Exception:
            pass

    def _apply_selector(self):
        if self.initialized:
            self._cancel_selector()

            for graphId in self.theDataLink.get_idGraphs():
                for traceId in self.theDataLink.get_idTraces(graphId):
                    selected, _ = self.items_selected.get_shown_entries()
                    if selected:
                        legend = self.theDataLink.kwargs_collections[self.theDataLink.get_idCollection_from_graph(graphId, traceId)].get('legend', '')  # Tricky line, might need to update DataLink
                        id_selections = _select_and_apply_action([self.theDataLink.get_collection_from_graph(graphId, traceId, getShadow=False)], selected, self.curr_action, legend)
                        self.previous_selection.append([graphId, traceId, id_selections])
            self.update_graphs()

    def _reset_colors(self):
        for graphId in self.theDataLink.get_idGraphs():
            for traceId in self.theDataLink.get_idTraces(graphId):
                self.theWGPlot.get_trace(graphId, traceId).reset_all_symbolPens(update=False)
                howToPlot = self.theDataLink.get_howToPlotGraph(graphId)
                howToPlot.meta = None
                self.theWGPlot.get_trace(graphId, traceId).reset_all_brushes(update=False)
        self.update_graphs()
