import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, uic
from optimeed.core.tools import get_recursive_attrs, order_lists
from optimeed.consolidate import analyse_sobol_convergence, SensitivityParameters, get_sensitivity_problem
from optimeed.visualize import start_qt_mainloop
from SALib.analyze import sobol
import os
from optimeed.core import default_palette, Graphs, Data
from optimeed.visualize.gui.widgets.graphsVisualWidget.pyqtgraph import TextItem
from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
from optimeed.visualize.gui import gui_mainWindow
from PyQt5.Qt import QFont
import numpy as np
import math


def analyse_sobol_plot_convergence(theDict, sobol='S1', title="", hold=True):
    theGraphs = Graphs()
    font = QFont("Arial", 10)

    palette = default_palette(len(theDict))

    g1 = theGraphs.add_graph()
    myWidgetGraphsVisuals = widget_graphs_visual(theGraphs, highlight_last=False, refresh_time=-1, is_light=True)  # The widget to display the graphs
    for index, key in enumerate(theDict):
        color = palette[index]

        x = theDict[key]['step']
        y1 = theDict[key][sobol]
        theGraphs.add_trace(g1, Data(x, y1, symbol=None, x_label="Sample size", y_label="Sobol indices ({})".format(sobol), color=color, xlim=[0, x[-1]*1.2]))
        myText = TextItem(theDict[key]['name'], color=color, anchor=(0, 0.5))
        myText.setPos(x[-1], y1[-1])
        myText.setFont(font)
        myText.setParentItem(myWidgetGraphsVisuals.get_graph(g1).theWGPlot.vb)
        myWidgetGraphsVisuals.get_graph(g1).add_feature(myText)
        myWidgetGraphsVisuals.get_graph(g1).set_title(title)
    guiPyqtgraph(myWidgetGraphsVisuals)  # The GUI of the widget (that contains export buttons)
    myWindow = gui_mainWindow([myWidgetGraphsVisuals])  # A Window (that will contain the widget)
    myWindow.run(hold)
    return myWindow


def analyse_sobol_plot_indices(theSensitivityParameters: SensitivityParameters, objectives, title='', hold=True):
    problem_SALib = get_sensitivity_problem(theSensitivityParameters.get_optivariables())
    nb_params = len(theSensitivityParameters.get_optivariables())

    max_N = math.floor(len(objectives) / (2*nb_params + 2))
    Si = sobol.analyze(problem_SALib, np.array(objectives[0:max_N*(2*nb_params+2)]))

    _, ordered_S1 = order_lists(Si['S1'], list(range(nb_params)))
    _, ordered_ST = order_lists(Si['ST'], list(range(nb_params)))
    ordered_S1.reverse()
    ordered_ST.reverse()

    order = ordered_ST

    # width of the bars
    barWidth = 0.3

    bars1 = [Si['S1'][map_index] for map_index in order]
    bars2 = [Si['ST'][map_index] for map_index in order]
    yer1 = [Si['S1_conf'][map_index] for map_index in order]
    yer2 = [Si['ST_conf'][map_index] for map_index in order]

    labels = [theSensitivityParameters.get_optivariables()[map_index].get_attribute_name() for map_index in order]
    indices = list(range(len(bars1)))
    # labels = indices
    r1 = [x - barWidth/2 for x in indices]
    r2 = [x + barWidth/2 for x in indices]

    def split_labels(label_str, level=2):
        splitted = label_str.split('.')
        try:
            return '.'.join(splitted[-level:])
        except IndexError:
            return label_str
    plt.figure()
    plt.bar(r1, bars1, width=barWidth, color='blue', edgecolor='black', yerr=yer1, capsize=7, label='First index (S1)')
    plt.bar(r2, bars2, width=barWidth, color='cyan', edgecolor='black', yerr=yer2, capsize=7, label='Total index (ST)')
    plt.xticks(indices, map(split_labels, labels), rotation=30, ha="right")
    plt.ylabel('Sobol Index')
    plt.legend()
    plt.grid()
    plt.title(title)
    plt.show(block=hold)


def analyse_sobol_plot_2ndOrder_indices(theSensitivityParameters: SensitivityParameters, objectives, title='', hold=True):
    problem_SALib = get_sensitivity_problem(theSensitivityParameters.get_optivariables())
    nb_params = len(theSensitivityParameters.get_optivariables())

    names = [var.get_attribute_name() for var in theSensitivityParameters.get_optivariables()]

    max_N = math.floor(len(objectives) / (2 * nb_params + 2))
    Si = sobol.analyze(problem_SALib, np.array(objectives[0:max_N * (2 * nb_params + 2)]))

    matrix = Si["S2"]
    for i in range(nb_params):
        for j in range(i, nb_params):
            matrix[j, i] = matrix[i, j]

    fig, ax = plt.subplots()
    im = ax.imshow(matrix, cmap="Blues")
    cbar = ax.figure.colorbar(im, ax=ax)

    # Show all ticks and label them with the respective list entries
    slope = (4-12)/(75-25)
    offset = 12-slope*25
    max_len = max([len(word) for word in names])
    fontsize = max(6, int(max_len*slope + offset))
    fontsize = min(12, fontsize)

    ax.set_xticks(np.arange(nb_params), labels=names)
    ax.set_yticks(np.arange(nb_params), labels=names)
    plt.tick_params(axis='both', which='major', labelsize=fontsize)

    # # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=70, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(names)):
        for j in range(len(names)):
            max_value = np.nanmax(matrix)
            curr_value_relative = matrix[i, j]/max_value
            color = "white" if curr_value_relative > 0.7 else "black"
            text = ax.text(j, i, "{:.3f}".format(matrix[i, j]),
                           ha="center", va="center", color=color)

    ax.set_title(title)
    fig.tight_layout()
    plt.show(block=hold)


class SensitivityDisplayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  #
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'displaySensitivity_gui.ui'), self)

        self.studies = list()
        self.curr_study = None

        self.combo_collection.currentIndexChanged.connect(self._set_study)
        # Todo
        self.button_get_S1_conv.clicked.connect(self._get_S1_conv)
        self.button_get_ST_conv.clicked.connect(self._get_ST_conv)
        self.button_get_indices.clicked.connect(self._get_sobol_indices)

        self.show()
        self.initialized = False
        self._windowsHolder = list()

    def add_study(self, theCollection, theParameters, name):
        self.studies.append((theCollection, theParameters, name))
        self.combo_collection.addItem(name)
        if not self.initialized:
            self.combo_collection.setCurrentIndex(0)
            self.initialized = True

    def _set_study(self, index):
        self.curr_study = self.studies[index]
        first_data = self.curr_study[0].get_data_at_index(0)
        self.list_attributes.set_list(get_recursive_attrs(first_data))

    def _get_sobol_indices(self):
        collection, parameters, name = self.curr_study
        attribute_selected = self.list_attributes.get_name_selected()
        values_selected = collection.get_list_attributes(attribute_selected)
        analyse_sobol_plot_indices(parameters, values_selected, title="{} | {}".format(name, attribute_selected), hold=False)
        analyse_sobol_plot_2ndOrder_indices(parameters, values_selected, title="{} | {}".format(name, attribute_selected), hold=False)

    def _get_S1_conv(self):
        collection, parameters, name = self.curr_study
        attribute_selected = self.list_attributes.get_name_selected()
        win = analyse_sobol_plot_convergence(analyse_sobol_convergence(parameters, collection.get_list_attributes(attribute_selected), stepsize=10),
                                             sobol="S1", title="{} | {}".format(name, attribute_selected), hold=False)
        self._windowsHolder.append(win)

    def _get_ST_conv(self):
        collection, parameters, name = self.curr_study
        attribute_selected = self.list_attributes.get_name_selected()
        win = analyse_sobol_plot_convergence(analyse_sobol_convergence(parameters, collection.get_list_attributes(attribute_selected), stepsize=10),
                                             sobol="ST", title="{} | {}".format(name, attribute_selected), hold=False)
        self._windowsHolder.append(win)


    @staticmethod
    def run():
        start_qt_mainloop()

