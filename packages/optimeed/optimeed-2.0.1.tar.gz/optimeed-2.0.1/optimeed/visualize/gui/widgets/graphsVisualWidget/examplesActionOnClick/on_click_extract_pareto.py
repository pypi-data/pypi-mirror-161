from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from optimeed.core.tools import get_2D_pareto
from optimeed.core.collection import ListDataStruct


class on_click_extract_pareto(on_graph_click_interface):
    """On click: extract the pareto from the cloud of points"""
    def __init__(self, theDataLink, max_x=False, max_y=False):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        :param max_x: x axis is to maximize or not (bool)
        :param max_y: y axis is to maximize or not (bool)
        """
        self.theDataLink = theDataLink
        self.max_x = max_x
        self.max_y = max_y

    def graph_clicked(self, the_graph_visual, index_graph, index_trace, _):
        # Retrieve collection plotted -> getShadow = False
        theCollection_plotted = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getShadow=False)

        # Recover x-y points
        x_list, y_list = self.theDataLink.get_x_y_to_plot(theCollection_plotted, self.theDataLink.get_howToPlotGraph(index_graph))

        # Get pareto from them
        xx, yy, indices = get_2D_pareto(x_list, y_list, max_X=self.max_x, max_Y=self.max_y)

        # Create new collection. We extract the "X-Y" (non-shadow) points from original collection
        newCollection_plotted = ListDataStruct()
        newCollection_plotted.set_data([theCollection_plotted.get_data_at_index(index) for index in indices])

        # Add it to the data link
        id_newCollection_plotted = self.theDataLink.add_collection(newCollection_plotted, {"is_scattered": False, "sort_output": True, "legend": 'Pareto extracted'})

        # Now we also need to extract the underlying motors.
        theCollection_motor = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getShadow=True)
        subset_collection_motor = theCollection_motor.extract_collection_from_indices(indices)

        # We add it to the datalink as shadow
        self.theDataLink.set_shadow_collection(id_newCollection_plotted, subset_collection_motor)

    def get_name(self):
        return "Extract pareto"
