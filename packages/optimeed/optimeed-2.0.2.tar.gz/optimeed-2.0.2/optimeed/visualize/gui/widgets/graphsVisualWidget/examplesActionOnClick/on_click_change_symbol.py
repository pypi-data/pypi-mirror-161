from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface


class on_click_change_symbol(on_graph_click_interface):
    """On Click: Change the symbol of the point that is clicked"""

    def __init__(self, theLinkDataGraph):
        """

        :param theLinkDataGraph: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        self.theLinkDataGraph = theLinkDataGraph

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        theTrace = theGraphVisual.get_graph(index_graph).get_trace(index_trace)
        for index_point in indices_points:
            theTrace.set_symbol(index_point, 'x')

    def get_name(self):
        return "Change symbol"
