from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from PyQt5.QtWidgets import QApplication


class on_click_copy_something(on_graph_click_interface):
    """On Click: copy something"""

    def __init__(self, theDataLink, functionStrFromDevice):
        """
        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        :param functionStrFromDevice: simple method that takes a device (point that is clicked) as argument.
        """
        self.theLinkDataGraph = theDataLink
        self.function = functionStrFromDevice

    def graph_clicked(self, the_graph_visual, index_graph, index_trace, indices_points):
        theDevice = self.theLinkDataGraph.get_clicked_item(index_graph, index_trace, indices_points[0])

        # Add the point to the collection exporter
        theStr = self.function(theDevice)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(theStr, mode=cb.Clipboard)

    def get_name(self):
        return "Copy in clipboard Str"
