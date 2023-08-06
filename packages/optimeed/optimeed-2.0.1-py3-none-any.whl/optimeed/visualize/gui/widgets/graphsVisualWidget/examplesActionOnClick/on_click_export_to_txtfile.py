from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from PyQt5 import QtWidgets
import os
from optimeed.core import rgetattr


class On_click_export_to_txtfile(on_graph_click_interface):
    """On click: export the data of the whole the trace selected"""
    def __init__(self, theDataLink, attributes_shadow=None):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        :param attributes_shadow: list of attributes (as string) to recover from the shadow (=data points/devices)
        """
        self.theDataLink = theDataLink
        self.attributes_shadow = attributes_shadow if attributes_shadow is not None else list()

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        howToPlot = self.theDataLink.get_howToPlotGraph(index_graph)
        attributes = [howToPlot.attribute_x, howToPlot.attribute_y]

        # Write header
        theStr = ""
        for attribute in attributes:
            theStr += "{}\t".format(attribute)
        for attribute in self.attributes_shadow:
            theStr += "{}\t".format(attribute)
        theStr += "\n"

        # Recover data to export
        collection_displayed = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getShadow=False)
        collection_shadowed = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getShadow=True)

        for index_point, _ in enumerate(collection_displayed.get_data_generator()):
            dataObj = collection_displayed.get_data_at_index(index_point)
            for attribute in attributes:
                theStr += "{}\t".format(rgetattr(dataObj, attribute))

            if len(self.attributes_shadow):
                dataObj = collection_shadowed.get_data_at_index(index_point)
                for attribute in self.attributes_shadow:
                    theStr += "{}\t".format(rgetattr(dataObj, attribute))
            theStr += "\n"

        # Export
        dlg = QtWidgets.QFileDialog.getSaveFileName()[0]
        if dlg:
            root, ext = os.path.splitext(dlg)
            filename = root + ".txt"
            with open(filename, "w") as f:
                f.write(theStr)

    def get_name(self):
        return "Export trace to text file"
