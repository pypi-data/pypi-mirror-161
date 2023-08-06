import numpy
from optimeed.core.tools import printIfShown, SHOW_WARNING
from optimeed.core.additional_tools import convert_color_with_alpha


class Data:
    """This class is used  to store informations necessary to plot a 2D graph. It has to be combined with a gui to be useful (ex. pyqtgraph)"""
    def __init__(self, x: list, y: list, x_label='', y_label='',
                 legend='', is_scattered=False,
                 transfo_x=lambda selfData, x: x, transfo_y=lambda selfData, y: y,
                 xlim=None, ylim=None,
                 permutations=None, sort_output=False,
                 color=None, alpha=255,
                 symbol='o', symbolsize=8, fillsymbol=True, outlinesymbol=1.8,
                 linestyle='-', width=2, meta=None):

        """
        :param x_label: label of x axis
        :param x: x (list) coordinates. If None => it will be the indices
        :param y_label: label of y axis
        :param y: y (list) coordinates.
        :param color: Color to use for the trace (either rgb tuple or matlab-like diminutif (e.g.:'r')
        :param alpha: set transparency (0 to 255)
        :param legend: legend associated with the data
        :param linestyle: style of the line linking points of the trace
        :param is_scattered: boolean. If True: plot will be scattered
        :param sort_output: boolean. If True: x axis will be sorted to ascending number
        :param symbol: symbol to display the points of the trace (e.g.: 'o', 't1', ...)
        :param fillsymbol: paint a solid symbol or not (bool)
        :param outlinesymbol: make the outline of the symbol darker (>1) or clearer (<1). No outline = 1
        :param transfo_x: Method applied to all the x coordinates. Useful to change units for instance
        :param transfo_y: Method applied to all the y coordinates. Useful to change units for instance
        :param xlim: [x_min, x_max] view box
        :param ylim: [y_min, y_max] view box
        :param meta: list (or None if None) of the same length than y. Used for tikz meta.
        """
        if x is None:
            x = []
        if y is None:
            y = []
        self.x = x
        self.x_label = x_label
        self.y = y
        self.y_label = y_label
        self.legend = legend
        self.is_scattered = is_scattered
        self.sort_output = sort_output
        self.symbol = symbol
        self.fillsymbol = fillsymbol
        self.outlinesymbol = outlinesymbol
        self.color = color
        self.alpha = alpha
        self.transfo_x = transfo_x
        self.transfo_y = transfo_y
        self.xlim = xlim
        self.ylim = ylim
        self.points_to_plot = None  # None Value => plot all, [] => plot None
        self.linestyle = linestyle
        self.permutations = None
        self.set_permutations(permutations)
        self.width = width
        self.symbolsize = symbolsize
        self.meta = meta

    def set_kwargs(self, kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def set_data(self, x: list, y: list):
        """Overwrites current datapoints with new set"""
        self.x = x
        self.y = y

    def set_meta(self, meta):
        self.meta = meta

    def get_x(self):
        """Get x coordinates of datapoints"""
        the_list = self.x
        if len(self.y) != len(self.x):
            the_list = range(len(self.y))
        return the_list

    def get_symbolsize(self):
        """Get size of the symbols"""
        return self.symbolsize

    def symbol_isfilled(self):
        """Check if symbols has to be filled or not"""
        return self.fillsymbol

    def get_symbolOutline(self):
        """Get color factor of outline of symbols"""
        return self.outlinesymbol

    def get_length_data(self):
        """Get number of points"""
        return max(len(self.x), len(self.y))

    def get_xlim(self):
        """Get x limits of viewbox"""
        return self.xlim

    def get_ylim(self):
        """Get y limits of viewbox"""
        return self.ylim

    def get_y(self):
        """Get y coordinates of datapoints"""
        return self.y

    def get_meta(self):
        if self.meta is None:
            return None
        if len(self.get_y()) == len(self.meta):
            return self.meta
        return None

    def get_color(self):
        """Get color of the line, without transformation"""
        return self.color

    def get_color_alpha(self):
        """Get color of the line. Return r, g, b in 0, 255 scale"""
        return convert_color_with_alpha(self.color, self.alpha)

    def get_alpha(self):
        return self.alpha

    def get_width(self):
        """Get width of the line"""
        return self.width

    def get_number_of_points(self):
        """Get number of points"""
        return len(self.get_permutations())

    def get_plot_data(self):
        """
        Call this method to get the x and y coordinates of the points that have to be displayed.
        => After transformation, and after permutations.

        :return: x (list), y (list)
        """
        x = self.get_x()
        y = self.get_y()

        x = [self.transfo_x(self, i) for i in x]
        y = [self.transfo_y(self, i) for i in y]
        permutations = self.get_permutations(x=x)
        x, y = [x[perm_i] for perm_i in permutations], [y[perm_i] for perm_i in permutations]
        min_length = min(len(x), len(y))
        return x[:min_length], y[:min_length]

    def get_plot_meta(self, x, y):
        """
        Call this method to get the z coordinates of the points that been displayed.
        => After transformation, and after permutations.

        :return: z (list)
        """
        z = self.get_meta()
        if z is None:
            return z

        permutations = self.get_permutations(x=x)
        min_length = min(len(x), len(y))
        z = [z[perm_i] for perm_i in permutations]
        return z[:min_length]

    def get_permutations(self, x=None):
        """Return the transformation 'permutation':
        xplot[i] = xdata[permutation[i]]
        """
        indices_to_plot = self.get_indices_points_to_plot()

        if x is None:
            x = self.get_x()

        if self.permutations is not None:
            permutations = self.permutations
        elif self.sort_output:
            permutations = list(numpy.argsort(x))
        else:
            permutations = range(len(x))
            if len(indices_to_plot) == self.get_length_data():
                return permutations
        return [permutations[index] for index in indices_to_plot]

    def get_invert_permutations(self):
        """Return the inverse of permutations:
        xdata[i] = xplot[revert[i]]
        """
        return numpy.argsort(self.get_permutations())

    def get_dataIndex_from_graphIndex(self, index_graph_point):
        """
        From an index given in graph, recovers the index of the data.

        :param index_graph_point: Index in the graph
        :return: index of the data
        """
        return self.get_permutations()[index_graph_point]

    def get_dataIndices_from_graphIndices(self, index_graph_point_list):
        """
        Same as get_dataIndex_from_graphIndex but with a list in entry.
        Can (?) improve performances for huge dataset.

        :param index_graph_point_list: List of Index in the graph
        :return: List of index of the data
        """
        permutations = self.get_permutations()
        return [permutations[index] for index in index_graph_point_list]

    def get_graphIndex_from_dataIndex(self, index_data):
        """
        From an index given in the data, recovers the index of the graph.

        :param index_data: Index in the data
        :return: index of the graph
        """
        return self.get_permutations().index(index_data)

    def get_graphIndices_from_dataIndices(self, index_data_list):
        """
        Same as get_graphIndex_from_dataIndex but with a list in entry.
        Can (?) improve performances for huge dataset.

        :param index_data_list: List of Index in the data
        :return: List of index of the graph
        """
        invert_permutation = self.get_invert_permutations()
        return [invert_permutation[index] for index in index_data_list]

    def set_permutations(self, permutations):
        """
        Set permutations between datapoints of the trace

        :param permutations: list of indices to plot (example: [0, 2, 1] means that the first point will be plotted, then the third, then the second one)
        """
        if permutations is not None:
            if len(self.get_x()) == len(permutations):
                if self.sort_output:
                    print("Warning : Permutations due to flag 'sort_output' are overridden by user")
                self.permutations = permutations
            else:
                print("Error : Permutations have not the same length as the data")

    def get_x_label(self):
        """ Get x label of the trace """
        return self.x_label

    def get_y_label(self):
        """ Get y label of the trace """
        return self.y_label

    def get_legend(self):
        """ Get name of the trace """
        return self.legend

    def get_symbol(self):
        """ Get symbol """
        return self.symbol

    def add_point(self, x, y):
        """Add point(s) to trace (inputs can be list or numeral)"""
        if not isinstance(x, list):
            x = [x]
        if not isinstance(y, list):
            y = [y]
        self.x.extend(x)
        self.y.extend(y)

    def delete_point(self, index_point):
        """Delete a point from the datapoints"""
        if len(self.x):
            del self.x[index_point]
            del self.y[index_point]
        else:
            del self.y[index_point]

    def isScattered(self):
        """Check if plot is scatteded"""
        return self.is_scattered or len(self.get_y()) == 1

    def set_indices_points_to_plot(self, indices):
        """Set indices points to plot"""
        self.points_to_plot = indices

    def get_indices_points_to_plot(self):
        """Get indices points to plot"""
        indices = self.points_to_plot
        if indices is None:
            indices = range(self.get_length_data())
        return indices

    def get_linestyle(self):
        """Get linestyle"""
        return str(self.linestyle)

    def __str__(self):
        theStr = self.x_label + '\t' + self.y_label + '\n'
        theX = self.get_x()
        theY = self.get_y()
        for i in range(self.get_length_data()):
            theStr += str(theX[i]) + '\t\t\t' + str(theY[i]) + '\n'
        return theStr

    def export_str(self):
        """Method to save the points constituting the trace"""
        theStr = "# $NEW TRACE 2D$\n"
        theStr += "# $LEGEND$: ${}$\n".format(self.get_legend())
        theStr += "# $LABEL X$: ${}$\n".format(self.get_x_label())
        theStr += "# $LABEL Y$: ${}$\n".format(self.get_y_label())
        theStr += "# $BEGIN DATA$\n"
        x, y = self.get_plot_data()
        for i in range(len(x)):
            theStr += "{}\t{}\n".format(x[i], y[i])
        theStr += "# $END DATA$\n"
        return theStr

    def set_color(self, theColor):
        self.color = theColor

    def set_legend(self, theLegend):
        self.legend = theLegend


class Graph:
    """Simple graph container that contains several traces"""
    def __init__(self):
        self.traces = dict()
        self.curr_id = 0

    def add_trace(self, data):
        """Add a trace to the graph

        :param data: :class:`~Data`
        :return: id of the created trace
        """
        idTrace = self.curr_id
        self.traces[idTrace] = data
        self.curr_id += 1
        return idTrace

    def remove_trace(self, idTrace):
        """Delete a trace from the graph

        :param idTrace: id of the trace to delete
        """
        try:
            del self.traces[idTrace]
        except KeyError:
            printIfShown("Key {} not found".format(idTrace), SHOW_WARNING)

    def get_trace(self, idTrace) -> Data:
        """Get data object of idTrace

        :param idTrace: id of the trace to get
        :return: :class:`~Data`
        """
        return self.traces[idTrace]

    def get_all_traces(self):
        """Get all the traces id of the graph"""
        return self.traces

    def get_all_traces_ids(self):
        """Get all the traces id of the graph
        :return: list of id graphs
        """
        return list(self.traces.keys())

    def export_str(self):
        theStr = "# $NEW GRAPH$\n\n"
        for idTrace in self.get_all_traces():
            theStr += self.get_trace(idTrace).export_str()
            theStr += "\n"
        return theStr


class Graphs:
    """Contains several :class:`Graph`"""
    def __init__(self):
        self.graphs = dict()
        self.curr_id = 0
        self.updateMethods = set()

    def updateChildren(self):
        for updateMethod in self.updateMethods:
            updateMethod()

    def add_trace_firstGraph(self, data, updateChildren=True):
        """
        Same as add_trace, but only if graphs has only one id
        :param data:
        :param updateChildren:
        :return:
        """
        all_ids = self.get_all_graphs_ids()
        if len(all_ids) == 1:
            return self.add_trace(all_ids[0], data, updateChildren=updateChildren)
        printIfShown("Cannot add trace .. graphs are multiple", SHOW_WARNING)
        return None

    def add_trace(self, idGraph, data, updateChildren=True):
        """Add a trace to the graph

        :param idGraph: id of the graph
        :param data: :class:`~Data`
        :param updateChildren: Automatically calls callback functions
        :return: id of the created trace
        """
        idTrace = self.get_graph(idGraph).add_trace(data)
        if updateChildren:
            self.updateChildren()
        return idTrace

    def remove_trace(self, idGraph, idTrace, updateChildren=True):
        """Remove the trace from the graph

        :param idGraph: id of the graph
        :param idTrace: id of the trace to remove
        :param updateChildren: Automatically calls callback functions
        """
        self.get_graph(idGraph).remove_trace(idTrace)
        if updateChildren:
            self.updateChildren()

    def get_first_graph(self):
        """Get id of the first graph

        :return: id of the first graph
        """
        return self.get_graph(self.get_all_graphs_ids()[0])

    def get_graph(self, idGraph):
        """Get graph object at idgraph

        :param idGraph: id of the graph to get
        :return: :class:`~Graph`
        """
        return self.graphs[idGraph]

    def get_all_graphs_ids(self):
        """Get all ids of the graphs

        :return: list of id graphs
        """
        return list(self.graphs.keys())

    def get_all_graphs(self):
        """Get all graphs. Return dict {id: :class:`~Graph`}"""
        return self.graphs

    def add_graph(self, updateChildren=True):
        """Add a new graph

        :return: id of the created graph
        """
        idGraph = self.curr_id
        self.graphs[idGraph] = Graph()
        self.curr_id += 1
        if updateChildren:
            self.updateChildren()
        return idGraph

    def remove_graph(self, idGraph):
        """Delete a graph

        :param idGraph: id of the graph to delete
        """
        try:
            del self.graphs[idGraph]
        except KeyError:
            printIfShown("Key {} not found".format(idGraph), SHOW_WARNING)
        self.updateChildren()

    def add_update_method(self, childObject):
        """Add a callback each time a graph is modified.

        :param childObject: method without arguments
        """
        self.updateMethods.add(childObject)

    def export_str(self):
        """Export all the graphs in text

        :return: str"""
        theStr = ""
        for graphId in self.get_all_graphs_ids():
            theStr += self.get_graph(graphId).export_str()
            theStr += "\n\n\n"
        return theStr

    def merge(self, otherGraphs):
        # curr_id = 0
        # mappings = [{}]*2
        # all_graphs_1 = self.get_all_graphs()
        # all_graphs_2 = otherGraphs.get_all_graphs()
        #
        # new_graphs = dict()
        #
        # for index, all_graphs in enumerate([all_graphs_1, all_graphs_2]):
        #     for graphId in all_graphs_1:
        #         new_graphs[curr_id] = all_graphs[graphId]
        #         mappings[index][graphId] = curr_id
        #         curr_id += 1
        # self.graphs = new_graphs
        id_1 = self.get_all_graphs_ids()
        id_2 = otherGraphs.get_all_graphs_ids()

        not_in_1 = list(set(id_2) - set(id_1))
        in_1 = list(set(id_1) & set(id_2))

        # Add traces belonging to second graphs to first
        for id_graph in in_1:
            for trace_data in otherGraphs.get_graph(id_graph).get_all_traces().values():
                self.add_trace(id_graph, trace_data, updateChildren=False)
        # Create new graphs and add traces belonging to second graphs to first
        for id_graph in not_in_1:
            new_id = self.add_graph(updateChildren=False)
            for trace_data in otherGraphs.get_graph(id_graph).get_all_traces().values():
                self.add_trace(new_id, trace_data, updateChildren=False)
        self.updateChildren()

    def reset(self):
        self.graphs = dict()
        self.updateChildren()

    def is_empty(self):
        return len(self.get_all_graphs()) == 0
