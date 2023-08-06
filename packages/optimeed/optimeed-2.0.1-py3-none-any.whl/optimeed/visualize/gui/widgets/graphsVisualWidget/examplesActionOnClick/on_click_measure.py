from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
import numpy as np
from optimeed.visualize.gui.widgets.graphsVisualWidget.pyqtgraph import mkPen, TextItem
from optimeed.visualize.gui.widgets.graphsVisualWidget.pyqtgraph import GraphicsObject, Point
from PyQt5 import QtGui, QtCore


class LineItem(GraphicsObject):
    def __init__(self, point1, point2):
        GraphicsObject.__init__(self)
        self.point1 = point1
        self.point2 = point2

    def paint(self, p, *args):
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = mkPen("b")
        pen.setWidthF(pen.widthF())
        p.setPen(pen)
        p.drawLine(self.point1, self.point2)

        # p.setFont(QtGui.QFont('Helvetica', 1))
        # p.drawText(self.point1, self.text)  # Problem

    def boundingRect(self):
        vr = self.viewRect()  # bounds of containing ViewBox mapped to local coords.
        if vr is None:
            return QtCore.QRectF()
        return QtCore.QRectF(self.point1, self.point2)


class on_click_measure(on_graph_click_interface):
    """On Click: Measure distance. Click on two points to perform that action"""

    def __init__(self):
        self.point1 = None
        self.point2 = None
        self.theGraphVisual = None
        self.clicked_graph = None
        self.added_items = list()
        self.gtp1 = None
        self.gtp2 = None

    def graph_clicked(self, the_graph_visual, index_graph, index_trace, indices_points):
        if self.clicked_graph is None:
            self.clicked_graph = index_graph
            self.theGraphVisual = the_graph_visual

        if self.clicked_graph == index_graph:
            theTrace = the_graph_visual.get_graph(index_graph).get_trace(index_trace)
            point = indices_points[0]
            clickedPoint = theTrace.get_point(point).pos()
            if self.point1 is None:
                self.point1 = clickedPoint
                self.gtp1 = (index_graph, index_trace, point)
            elif self.point2 is None:
                self.point2 = clickedPoint
                self.display_distance()
                self.gtp2 = (index_graph, index_trace, point)
            else:
                self.point1 = clickedPoint
                self.point2 = None
                self.reset_distance()
                self.gtp1 = (index_graph, index_trace, point)
            theTrace.set_brush(point, (250, 250, 0))

    def reset_distance(self):
        for item in self.added_items:
            self.theGraphVisual.get_graph(self.clicked_graph).remove_feature(item)
        self.added_items = list()
        for gtp in [self.gtp1, self.gtp2]:
            if len(gtp):
                self.theGraphVisual.get_graph(gtp[0]).get_trace(gtp[1]).reset_brush(gtp[2])
        self.gtp1 = list()
        self.gtp2 = list()

    def display_distance(self):
        distance = np.sqrt((self.point1.x()-self.point2.x())**2 + (self.point1.y()-self.point2.y())**2)
        lineItem = LineItem(self.point1, self.point2)
        textItem = TextItem("{:#.4g}".format(distance), color="b", anchor=(0.5, 0.5))
        textItem.setPos((self.point2 + self.point1)/2.0)
        # textItem.setParentItem(lineItem)
        # textItem.setAngle(np.arctan((self.point2.y()-self.point1.y())/(self.point2.x()-self.point1.x()))*180/np.pi)
        self.theGraphVisual.get_graph(self.clicked_graph).add_feature(lineItem)
        self.theGraphVisual.get_graph(self.clicked_graph).add_feature(textItem)
        self.added_items.append(lineItem)
        self.added_items.append(textItem)

    def get_name(self):
        return "Measure distance"

