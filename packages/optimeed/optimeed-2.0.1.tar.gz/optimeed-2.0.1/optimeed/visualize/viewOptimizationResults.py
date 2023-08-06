from optimeed.core import LinkDataGraph, HowToPlotGraph, merge_two_dicts
from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
from optimeed.core import ListDataStruct, Performance_ListDataStruct, ListDataStruct_Interface
from optimeed.core import Graphs
import os


class _OptiProjectLoader:
    """A loader for an opti project."""
    def __init__(self, foldername, kwargsPlot=None):
        """

        :param foldername: the folder containing the saved files.
        :param kwargsPlot: Check kgwargs `~optimeed.core.graphs.Data`
        """
        self.logopti = ListDataStruct.load(os.path.join(foldername, "logopti.json"))
        try:
            self.theDevices = Performance_ListDataStruct.load(os.path.join(foldername, "autosaved.json"))
        except KeyError:  # If it fails, it is probably a ListDataStruct
            self.theDevices = ListDataStruct.load(os.path.join(foldername, "autosaved.json"))
        self.theConvergence = ListDataStruct.load(os.path.join(foldername, "optiConvergence.json"))
        self.kwargsPlot = kwargsPlot

    def get_devices(self) -> ListDataStruct_Interface:
        return self.theDevices

    def get_logopti(self) -> ListDataStruct_Interface:
        return self.logopti

    def get_convergence(self):
        return self.theConvergence.get_data_at_index(0)

    def get_kwargs(self):
        return dict() if self.kwargsPlot is None else self.kwargsPlot

    def get_nbr_objectives(self):
        return len(self.logopti.get_data_at_index(0).objectives)


class ViewOptimizationResults:
    """Convenience class to display the results of an optimization"""

    def __init__(self):
        self.optiProjects = list()
        self.theDataLink = LinkDataGraph()

    def add_opti_project(self, foldername, kwargsPlot=None):
        """Add an opti project to visualize.

        :param foldername: the folder containing the saved files. (as string)
        :param kwargsPlot: Check kgwargs `~optimeed.core.graphs.Data`
        """
        self.optiProjects.append(_OptiProjectLoader(foldername, kwargsPlot))

    def get_data_link(self) -> LinkDataGraph:
        """Return the object :class:`~optimeed.core.linkDataGraph.LinkDataGraph`"""
        return self.theDataLink

    def display_graphs(self, theActionsOnClick=None, kwargs_common=None, keep_alive=True, max_nb_points_convergence=None, light_background=False):
        """Generates the optimization graphs.

        :param theActionsOnClick: list of actions to perform when a graph is clicked
        :param kwargs_common: plot options (from Data class) to apply to all the graphs (ex: {"is_scattered": True}).
        :param keep_alive: if set to true, this method will be blocking. Otherwise you should manually call start_qt_mainloop().
        :param max_nb_points_convergence: maximum number of points in the graph that displays the convergence. Put None if performance is not an issue.
        :param light_background: boolean, True or False for White or Black background color in graphs
        :return: widget_graphs_visual for the log opti, widget_graphs_visual for the convergence (:class:`~widget_graphs_visual`)
        """
        if theActionsOnClick is None:
            theActionsOnClick = list()

        nbrObjectives = self.optiProjects[0].get_nbr_objectives()
        theDataLink = self.theDataLink

        # Creates empty graphs
        listOf_howtoplot = list()

        base_kwargs = {'is_scattered': True}
        if kwargs_common is not None:
            base_kwargs.update(kwargs_common)

        if nbrObjectives == 2:  # bi-objective -> each objective is an axis
            howToPlot = HowToPlotGraph('objectives[0]', 'objectives[1]', base_kwargs)
            theDataLink.add_graph(howToPlot)  # Creates a graph
            listOf_howtoplot.append(howToPlot)
        elif nbrObjectives == 3:  # 3-objectives -> plot graphs by pairs of objective
            for i in range(nbrObjectives):
                i_plus_1 = i + 1 if i != 2 else 2
                curr_i = i if i != 2 else 0
                howToPlot = HowToPlotGraph('objectives[{}]'.format(curr_i), 'objectives[{}]'.format(i_plus_1), base_kwargs)
                theDataLink.add_graph(howToPlot)  # Creates a graph
                listOf_howtoplot.append(howToPlot)
        else:  # Plot each objective as a function of the time
            for i in range(nbrObjectives):
                howToPlot = HowToPlotGraph(None, 'objectives[{}]'.format(i), base_kwargs)
                theDataLink.add_graph(howToPlot)  # Creates a graph
                listOf_howtoplot.append(howToPlot)

        # Graphs are created, now add the data to it.
        for theOptiProject in self.optiProjects:
            collection_devices = theOptiProject.get_devices()
            collection_logOpti = theOptiProject.get_logopti()

            # There is a bit of processing here to split the full data set into two:
            # Those that respects the constraints and those that do not
            all_constraints = collection_logOpti.get_list_attributes("constraints")
            violate_constraint_indices = list()
            max_index = min(collection_devices.get_nbr_elements(), collection_logOpti.get_nbr_elements())

            for index, constraints in enumerate(all_constraints):
                if index > max_index:
                    break
                for constraint in constraints:
                    if constraint > 0:
                        violate_constraint_indices.append(index)  # Index in data

            # Based on that -> create subsets
            subsets_opti = list()  # will contain master, slave, kwargs

            if len(violate_constraint_indices):
                all_indices = set(range(max_index))
                indices_ko = violate_constraint_indices
                indices_ok = [u for u in all_indices if u not in set(indices_ko)]

                collection_devices_ok = collection_devices.extract_collection_from_indices(indices_ok)
                collection_logOpti_ok = collection_logOpti.extract_collection_from_indices(indices_ok)
                subsets_opti.append((collection_devices_ok, collection_logOpti_ok, {"legend": "Respects constraints"}))

                collection_devices_ko = collection_devices.extract_collection_from_indices(indices_ko)
                collection_logOpti_ko = collection_logOpti.extract_collection_from_indices(indices_ko)
                subsets_opti.append((collection_devices_ko, collection_logOpti_ko, {"legend": "Violates constraints"}))
            else:
                subsets_opti.append((collection_devices, collection_logOpti, {}))

            # We add them
            for collection_devices, collection_logOpti, newKwargs in subsets_opti:
                id_logOpti = theDataLink.add_collection(collection_logOpti, kwargs=merge_two_dicts(theOptiProject.get_kwargs(), newKwargs))
                """The trick here is that the objective functions is not directly stocked in collection_devices but in collection_logOpti. 
                So we display the objectives coming from collection_logOpti but we link collection_devices from it.
                So that when a point is clicked, the action is performed on the device and not on the logOpti."""
                theDataLink.set_shadow_collection(id_logOpti, collection_devices)

        """Create the widget of the graphs, and the associated GUI"""
        myWidgetGraphsVisuals = widget_graphs_visual(theDataLink.get_graphs(), highlight_last=False, refresh_time=-1, is_light=light_background)
        guiPyqtgraph(myWidgetGraphsVisuals, actionsOnClick=theActionsOnClick)  # Add GUI to change action easily and export graphs

        """Spawn the GUI"""
        theWindow = gui_mainWindow([myWidgetGraphsVisuals])
        theWindow.run(hold=False)

        """Spawn an other GUI for the convergence graphs"""
        graphs_convergence = Graphs()
        for theOptiProject in self.optiProjects:
            newGraphs = theOptiProject.get_convergence().get_graphs(max_number_of_points=max_nb_points_convergence)
            newGraphs.get_first_graph().get_trace(0).set_legend(theOptiProject.get_kwargs().get("legend", ''))
            graphs_convergence.merge(newGraphs)
        wg_graphs_convergence = widget_graphs_visual(graphs_convergence, highlight_last=False, refresh_time=-1, is_light=light_background)
        guiPyqtgraph(wg_graphs_convergence)  # Add GUI to change action easily and export graphs

        myWindow = gui_mainWindow([wg_graphs_convergence])
        myWindow.run(hold=keep_alive)

        return myWidgetGraphsVisuals, wg_graphs_convergence
