from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from optimeed.visualize.gui.widgets.graphsVisualWidget.examplesActionOnClick.gui_collection_exporter import gui_collection_exporter


class on_graph_click_export(on_graph_click_interface):
    """On click: export the selected points"""
    def __init__(self, theDataLink):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        self.theDataLink = theDataLink
        self.the_collection_exporter = gui_collection_exporter()

        self.the_collection_exporter.signal_has_exported.connect(self.the_collection_exporter.reset)
        self.the_collection_exporter.signal_has_reset.connect(self.reset_graph)

        self.modifiedTraces = list()

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        theTrace = theGraphVisual.get_graph(index_graph).get_trace(index_trace)
        self.modifiedTraces.append(theTrace)
        # Add the point to the collection exporter
        for index_point in indices_points:
            theTrace.set_brush(index_point, (250, 250, 0))
            theData = self.theDataLink.get_clicked_item(index_graph, index_trace, index_point)
            self.the_collection_exporter.add_data_to_collection(theData)

    def reset_graph(self):
        for trace in self.modifiedTraces:
            trace.reset_all_brushes()
        self.modifiedTraces = list()

    def get_name(self):
        return "Select points to export collection"


