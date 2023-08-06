from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface


# from optimeed.core.Collection import Collection


class on_graph_click_delete(on_graph_click_interface):
    """On Click: Delete the points from the graph"""

    def __init__(self, theDataLink):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        super().__init__()
        self.theDataLink = theDataLink

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        self.theDataLink.delete_clicked_items(index_graph, index_trace, indices_points)

    def get_name(self):
        return "Delete points"

