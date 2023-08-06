from .traceVisual import TraceVisual
from .pyqtgraphRedefine import myLegend, myAxis
from optimeed.core.tools import printIfShown, SHOW_WARNING
from PyQt5 import QtGui
# from . import pyqtgraph as pg
from optimeed.core.color_palette import default_palette


class GraphVisual:
    """Provide an interface to a graph. A graph contains traces."""
    def __init__(self, theWidgetGraphVisual):
        """

        :param theWidgetGraphVisual: :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.widget_graphs_visual`
        """
        self.theWidgetGraphVisual = theWidgetGraphVisual

        self.traceVisuals = dict()
        self.theWGPlot = self.theWidgetGraphVisual.canvasWidget.addPlot(axisItems={'bottom': myAxis(orientation='bottom'), 'left': myAxis(orientation='left')})  # Class PLOT ITEM
        # self.theWGPlot.disableAutoRange()
        self.theWGPlot.legend = myLegend(is_light=self.theWidgetGraphVisual.is_light)
        self.theWGPlot.legend.setParentItem(self.theWGPlot.vb)

        self.theWGPlot.showGrid(x=True, y=True)
        self.set_fontTicks(11)
        self.palette = default_palette

        # Set font label
        if self.theWidgetGraphVisual.is_light:
            label_color = '#000'
        else:
            label_color = '#FFF'
        self.labelStyle = None
        self.set_fontLabel(12, label_color)

    def set_fontTicks(self, fontSize, fontname=None):
        """ Set font of the ticks

        :param fontSize: Size of the font
        :param fontname: Name of the font
        """
        font = QtGui.QFont()
        font.setPointSizeF(fontSize)
        if fontname is not None:
            font.setFamily(fontname)
        self.theWGPlot.getAxis("bottom").tickFont = font
        self.theWGPlot.getAxis("left").tickFont = font

    def set_numberTicks(self, number, axis):
        """ Set the number of ticks to be displayed

        :param number: Number of ticks for the axis
        :param axis: Axis (string, "bottom", "left", "right", "top")
        :return:
        """
        self.theWGPlot.getAxis(axis).set_number_ticks(number)

    def set_fontLabel(self, fontSize, color='#000', fontname=None):
        """Set font of the axis labels

        :param fontSize: font size
        :param color: color in hexadecimal (str)
        :param fontname: name of the font"""
        self.labelStyle = {'font-size': str(fontSize) + 'pt', 'color': color, "font-family": fontname}

    def get_legend(self) -> myLegend:
        """ Get the legend"""
        return self.theWGPlot.legend

    def get_axis(self, axis) -> myAxis:
        """ Get the axis

        :param axis: Axis (string, "bottom", "left", "right", "top")
        :return: axis object
        """
        return self.theWGPlot.getAxis(axis)

    def set_fontLegend(self, font_size, font_color, fontname=None):
        self.get_legend().set_font(font_size, font_color, fontname)

    def set_label_pos(self, orientation, x_offset=0, y_offset=0):
        self.theWGPlot.getAxis(orientation).set_label_pos(orientation, x_offset, y_offset)

    def set_color_palette(self, palette):
        self.palette = palette
        self.apply_palette()

    def apply_palette(self):
        numb_color_to_set = len(self.get_all_traces())
        theColors = self.palette(numb_color_to_set)
        for i, trace in enumerate(self.get_all_traces().values()):
            if trace.get_color() is None:
                trace.set_color(theColors[i])

    def hide_axes(self):
        self.theWGPlot.showGrid(x=False, y=False)
        self.theWGPlot.getAxis("bottom").hide()
        self.theWGPlot.getAxis("left").hide()

    def add_feature(self, theFeature):
        """To add any pyqtgraph item to the graph"""
        self.theWGPlot.addItem(theFeature)

    def remove_feature(self, theFeature):
        """To remove any pyqtgraph item from the graph"""
        self.theWGPlot.removeItem(theFeature)

    def add_data(self, idGraph, theData):
        theTrace = TraceVisual(theData, self.theWGPlot, highlight_last=self.theWidgetGraphVisual.highlight_last)
        self.add_trace(idGraph, theTrace)
        if len(self.traceVisuals) <= 1:
            self.set_graph_properties(theTrace)

    def set_graph_properties(self, theTrace):
        """This function is automatically called on creation of the graph"""
        self.theWGPlot.setLabel('bottom', text=theTrace.theData.get_x_label(), **self.labelStyle)
        self.theWGPlot.setLabel('left', text=theTrace.theData.get_y_label(), **self.labelStyle)

        self.set_lims(theTrace.theData.get_xlim(), theTrace.theData.get_ylim())

    def set_lims(self, xlim, ylim):
        """Set limits of the graphs, xlim or ylim = [val_low, val_high]. Or None."""
        # if xlim is not None:
        #     self.theWGPlot.setLimits(xMin=xlim[0], xMax=xlim[1])
        # if ylim is not None:
        #     self.theWGPlot.setLimits(yMin=ylim[0], yMax=ylim[1])
        #
        if xlim is not None or ylim is not None:
            self.theWGPlot.setRange(xRange=xlim, yRange=ylim)
        # self.theWGPlot.setAutoVisible(x=xlim is None, y=ylim is None)

    def add_trace(self, idTrace, theTrace):
        """Add a :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.TraceVisual.TraceVisual` to the graph, with index idTrace"""
        self.traceVisuals[idTrace] = theTrace
        theTrace.thePlotItem.sigPointsClicked.connect(self.theWidgetGraphVisual.on_click)  # Connect the function "on click"

    def set_legend(self):
        """Set default legend options (color and font)"""
        if self.theWidgetGraphVisual.is_light:
            legend_color = '#111'
        else:
            legend_color = '#DDD'

        self.set_fontLegend(10, legend_color)

    def set_title(self, titleName, **kwargs):
        """Set title of the graph

        :param titleName: title to set
        """
        self.theWGPlot.setTitle(title=titleName, **kwargs)

    def get_trace(self, idTrace) -> TraceVisual:
        """Return the :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.TraceVisual.TraceVisual` correspondong to the index idTrace"""
        return self.traceVisuals[idTrace]

    def get_all_traces(self):
        """Return a dictionary {idtrace: :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.TraceVisual.TraceVisual`}."""
        return self.traceVisuals

    def delete_trace(self, idTrace):
        """Delete the trace of index idTrace"""
        try:
            self.theWGPlot.removeItem(self.traceVisuals[idTrace].thePlotItem)
            self.traceVisuals.pop(idTrace)
            # self.signal_must_update.emit()
        except KeyError:
            printIfShown("Trace already deleted", SHOW_WARNING)

    def delete(self):
        """Delete the graph"""
        self.theWGPlot.deleteLater()
        self.theWidgetGraphVisual.canvasWidget.centralWidget.layout.removeItem(self.theWGPlot)

    def linkXToGraph(self, graph):
        """Link the axis of the current graph to an other :class:`GraphVisual`"""
        self.theWGPlot.setXLink(graph.theWGPlot)

    def update(self):
        """Update the traces contained in the graph"""
        for trace in self.get_all_traces().values():
            self.set_graph_properties(trace)
            trace.signal_must_update.emit()

    def fast_update(self):
        """Same as :meth:`~GraphVisual.update` but faster. This is NOT thread safe (cannot be called a second time before finishing operation)"""
        for trace in self.get_all_traces().values():
            trace.updateTrace()

    def axis_equal(self):
        self.theWGPlot.vb.setAspectLocked(True)

    def log_mode(self, x=False, y=False):
        self.theWGPlot.setLogMode(x, y)

    def grid_off(self):
        """Turn off grid"""
        self.theWGPlot.showGrid(x=False, y=False)
