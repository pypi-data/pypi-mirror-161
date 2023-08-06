from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface


class on_graph_click_remove_trace(on_graph_click_interface):

    def __init__(self, theDataLink):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        self.theDataLink = theDataLink

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, _):
        self.theDataLink.remove_collection(index_graph, index_trace)

    def get_name(self):
        return "Remove trace"
