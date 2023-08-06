from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from PyQt5 import QtWidgets
import os


class on_graph_click_export_trace(on_graph_click_interface):
    """On click: export the data of the whole the trace selected"""
    def __init__(self, theDataLink, getShadow=True):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        self.theDataLink = theDataLink
        self.getShadow = getShadow

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        theCollection = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getShadow=self.getShadow)
        dlg = QtWidgets.QFileDialog.getSaveFileName()[0]
        if dlg:
            root, ext = os.path.splitext(dlg)
            filename_collection = root + theCollection.get_extension()
            theCollection.clone(filename_collection)

    def get_name(self):
        return "Export collection of the trace"
