from . import pyqtgraph as pg
from PyQt5 import QtCore, QtGui
from .colormap_pyqtgraph import matplotlib_colormap_to_pg_colormap


default_colormap = matplotlib_colormap_to_pg_colormap('jet')


def normalize_colors(z):
    # Get colors to set
    min_value = min(z)
    max_value = max(z)
    colors = [(0, 0, 0)] * len(z)
    for k, value in enumerate(z):
        normalized_value = (value - min_value) / (max_value - min_value)
        colors[k] = default_colormap.mapToQColor(normalized_value)
    return colors


class TraceVisual(QtCore.QObject):
    """Defines a trace in a graph."""
    signal_must_update = QtCore.pyqtSignal()

    class _ModifiedPaintElem:
        """Hidden class to manage brushes or pens"""
        def __init__(self):
            self.changed = dict()  # {index_plot, newPaintElem}

        def add_modified_paintElem(self, index, newPaintElem):
            self.changed[index] = newPaintElem

        def modify_paintElems(self, paintElemsIn_List):
            """Apply transformation to paintElemsIn_List.

            :param: paintElemsIn_List: list of brushes or pens to modify
            :return: False if nothing has been modified, True is something has been modified
            """
            if not len(self.changed):
                return False

            for index in self.changed:
                try:
                    paintElemsIn_List[index] = self.changed[index]
                except IndexError:
                    pass
            return True

        def reset_paintElem(self, index):
            """ Remove transformation of point index"""
            self.changed.pop(index, None)

        def reset(self):
            self.__init__()

    def __init__(self, theData, theWGPlot, highlight_last):
        """
        :param theData: from class Data. Contains all the informations to plot (x, y, z, transforms, etc.)
        :param theWGPlot: holder of the trace. This is a plotWidget
        :param highlight_last: Boolean. If set to true, the last point in the data will be highlighted.
        """
        super().__init__()

        # set brush
        self.theBrushesModifier = self._ModifiedPaintElem()

        # set symbolPen
        self.theSymbolPensModifier = self._ModifiedPaintElem()

        # set symbols
        self.theSymbolModifier = self._ModifiedPaintElem()

        # set data
        self.theData = theData

        # set trace item (plotItem)
        if theData.get_legend():
            self.thePlotItem = theWGPlot.plot([float('inf')], name=theData.get_legend())
        else:
            self.thePlotItem = theWGPlot.plot([float('inf')])

        # set highlight last
        self.highlight_last = highlight_last
        self.drawPoints = True

        # signals
        self.signal_must_update.connect(self.updateTrace)

        # Performance issues:
        self._base_symbol_pen = None
        self._base_symbol_brush = None
        self._base_pen = None

        self.visible = True

    def hide_points(self):
        """Hide all the points"""
        self.drawPoints = False
        self.signal_must_update.emit()

    def get_color(self):
        """Get colour of the trace, return tuple (r,g,b)"""
        return self.get_data().get_color()

    def set_color(self, color):
        """Set colour of the trace, argument as tuple (r,g,b)"""
        self.get_data().set_color(color)
        self.thePlotItem.scatter.opts['brush'] = color

    def get_base_symbol_brush(self):
        """Get symbol brush configured for this trace, return :class:`pg.QBrush`"""
        if self._base_symbol_brush is None:
            self._base_symbol_brush = pg.mkBrush(self.get_data().get_color_alpha())
        return self._base_symbol_brush

    def get_base_pen(self):
        """Get pen configured for this trace, return :class:`pg.QPen`"""
        if self._base_pen is None:
            pen = pg.mkPen(self.get_color(), width=self.get_data().get_width())
            if self.theData.isScattered():
                pen.setStyle(QtCore.Qt.NoPen)
            else:
                self.set_pen_linestyle(pen, self.theData.get_linestyle())
            self._base_pen = pen
        return self._base_pen

    def get_base_symbol_pen(self):
        """Get symbol pen configured for this trace, return :class:`pg.QPen`"""
        if self._base_symbol_pen is None:
            if self.get_data().symbol_isfilled():
                if self.get_data().get_symbolOutline() == 1:
                    return None
                init_color = QtGui.QColor(*self.get_color())
                darker_color = init_color.darker(int(self.get_data().get_symbolOutline()*100))
                alpha = self.get_data().get_alpha()
                if alpha < 255:
                    darker_color.setAlpha(self.get_data().get_alpha())
                thePen = pg.mkPen(darker_color, isCosmetic=True)
                # thePen = pg.mkPen(QtGui.QColor(*self.get_color()).darker(int(self.get_data().get_symbolOutline()*100)), isCosmetic=True)  # 120 or 250 ? :)
            else:
                thePen = pg.mkPen(self.get_color(), isCosmetic=False, width=self.get_data().get_width())
            self._base_symbol_pen = thePen
        return self._base_symbol_pen

    def get_base_symbol(self):
        """Get base symbol configured for this trace, return str of the symbol (e.g. 'o')"""
        return self.get_data().get_symbol()

    def get_symbol(self, size):
        """Get actual symbols for the trace. If the symbols have been modified: return a list which maps each points to a symbol.
        Otherwise: return :meth:TraceVisual.get_base_symbol()"""
        symbol = self.get_base_symbol()
        theSymbolList = [symbol] * size
        hasBeenModified = self.theSymbolModifier.modify_paintElems(theSymbolList)
        return symbol if not hasBeenModified else theSymbolList

    def updateTrace(self):
        """Forces the trace to refresh."""
        if self.visible:
            try:
                theData = self.get_data()
                x, y = theData.get_plot_data()
                if x and y:
                    z = theData.get_plot_meta(x, y)

                    if z is not None:
                        self.set_brushes(list(range(len(z))), list(map(QtGui.QBrush, normalize_colors(z))), update=False)

                    if self.drawPoints:
                        theBrushes = self.get_brushes(len(x))
                        theSymbolPens = self.get_symbolPens(len(x))
                    else:
                        theBrushes = None
                        theSymbolPens = None

                    theBasePen = self.get_base_pen()
                    self.thePlotItem.setData(x, y, symbolBrush=theBrushes, symbol=self.get_symbol(len(x)), symbolPen=theSymbolPens, symbolSize=self.get_data().get_symbolsize(), pen=theBasePen)  # symbolPen = None for no outline
                else:
                    self.thePlotItem.setData([], [], symbolBrush=None)

            except ValueError:
                pass
        else:
            self.thePlotItem.setData([], [], symbolBrush=None)

    def get_length(self):
        """Return number of data to plot"""
        x = self.get_data().get_plot_data()
        return len(x)

    def hide(self):
        """Hides the trace"""
        self.visible = False
        self.thePlotItem.clear()
        self.signal_must_update.emit()

    def show(self):
        """Shows the trace"""
        self.visible = True
        self.signal_must_update.emit()

    def toggle(self, boolean):
        """Toggle the trace (hide/show)"""
        if boolean:
            self.show()
        else:
            self.hide()

    def get_data(self):
        """Get data to plot :class:`~optimeed.visualize.graphs.Graphs.Data`"""
        return self.theData

    def get_brushes(self, size):
        """Get actual brushes for the trace (=symbol filling). return a list which maps each points to a symbol brush"""
        symbolBrush = self.get_base_symbol_brush() if self.get_data().symbol_isfilled() else None
        theBrushList = [symbolBrush] * size

        if self.highlight_last:
            theBrushList[-1] = pg.mkBrush('y')
        hasBeenModified = self.theBrushesModifier.modify_paintElems(theBrushList)
        if not hasBeenModified and not self.highlight_last:
            return symbolBrush
        return theBrushList

    def set_brush(self, indexPoint, newbrush, update=True):
        """Set the symbol brush for a specific point:

        :param indexPoint: Index of the point (in the graph) to modify
        :param newbrush: either QBrush or tuple (r, g, b) of the new brush
        :param update: if True, update the trace afterwards. This is slow operation."""
        if isinstance(newbrush, tuple):
            newbrush = pg.mkBrush(newbrush)
        self.theBrushesModifier.add_modified_paintElem(indexPoint, newbrush)
        if update:
            self.signal_must_update.emit()

    def set_symbol(self, indexPoint, newSymbol, update=True):
        """Set the symbol shape for a specific point:

        :param indexPoint: Index of the point (in the graph) to modify
        :param newSymbol: string of the new symbol (e.g.: 'o')
        :param update: if True, update the trace afterwards. This is slow operation."""
        self.theSymbolModifier.add_modified_paintElem(indexPoint, newSymbol)
        if update:
            self.signal_must_update.emit()

    def set_brushes(self, list_indexPoint, list_newbrush, update=True):
        """Same as :meth:`~TraceVisual.set_brush` but by taking a list as input"""
        if not isinstance(list_newbrush, list):
            list_newbrush = [list_newbrush] * len(list_indexPoint)
        for i in range(len(list_indexPoint)):
            self.set_brush(list_indexPoint[i], list_newbrush[i], update=False)
        if update:
            self.signal_must_update.emit()

    def reset_brush(self, indexPoint, update=True):
        """Reset the brush of the point indexpoint"""
        self.theBrushesModifier.reset_paintElem(indexPoint)
        if update:
            self.signal_must_update.emit()

    def reset_brushes(self, list_indexPoint, update=True):
        """Same as :meth:`~TraceVisual.reset_brush` but by taking a list as input"""
        [self.reset_brush(idPoint, update=False) for idPoint in list_indexPoint]
        if update:
            self.signal_must_update.emit()
            
    def reset_all_brushes(self, update=True):
        """Reset all the brushes"""
        self.theBrushesModifier.reset()
        if update:
            self.signal_must_update.emit()

    def reset_symbol(self, indexPoint, update=True):
        """Reset the symbol shape of the point indexpoint"""
        self.theSymbolModifier.reset_paintElem(indexPoint)
        if update:
            self.signal_must_update.emit()

    def get_symbolPens(self, size):
        """Get actual symbol pens for the trace (=symbol outline). return a list which maps each points to a symbol pen"""
        thePenList = [self.get_base_symbol_pen()] * size
        hasBeenModified = self.theSymbolPensModifier.modify_paintElems(thePenList)
        if not hasBeenModified:
            return self.get_base_symbol_pen()
        return thePenList

    def set_symbolPen(self, indexPoint, newPen, update=True):
        """Set the symbol shape for a specific point:

        :param indexPoint: Index of the point (in the graph) to modify
        :param newPen: QPen item or tuple of the color (r,g,b)
        :param update: if True, update the trace afterwards. This is slow operation."""
        if isinstance(newPen, tuple):
            newPen = pg.mkPen(newPen)
        self.theSymbolPensModifier.add_modified_paintElem(indexPoint, newPen)
        if update:
            self.signal_must_update.emit()

    def set_symbolPens(self, list_indexPoint, list_newpens, update=True):
        """Same as :meth:`~TraceVisual.set_symbolPen` but by taking a list as input"""
        if not isinstance(list_newpens, list):
            list_newpens = [list_newpens] * len(list_indexPoint)
        for i in range(len(list_indexPoint)):
            self.set_symbolPen(list_indexPoint[i], list_newpens[i], update=False)
        if update:
            self.signal_must_update.emit()

    def reset_symbolPen(self, indexPoint, update=True):
        """Reset the symbol pen of the point indexpoint"""
        self.theSymbolPensModifier.reset_paintElem(indexPoint)
        if update:
            self.signal_must_update.emit()

    def reset_symbolPens(self, list_indexPoint, update=True):
        """Same as :meth:`~TraceVisual.reset_symbolPen` but by taking a list as input"""
        [self.reset_symbolPen(idPoint, update=False) for idPoint in list_indexPoint]
        if update:
            self.signal_must_update.emit()

    def reset_all_symbolPens(self, update=True):
        """Reset all the symbol pens"""
        self.theSymbolPensModifier.reset()
        if update:
            self.signal_must_update.emit()

    @staticmethod
    def set_pen_linestyle(thePen, linestyle):
        """Transform a pen for dashed lines:

        :param thePen: QPen item
        :param linestyle: str (e.g.: '.', '.-', '--', ...)
        """
        if linestyle in ['.', ':', '..']:
            thePen.setDashPattern([0.1, 2])
            thePen.setCapStyle(QtCore.Qt.RoundCap)
            thePen.setWidthF(thePen.width()*1.75)
        elif linestyle in ['.-', '-.']:
            thePen.setCapStyle(QtCore.Qt.RoundCap)
            thePen.setDashPattern([3, 2, 0.1, 2])
            thePen.setWidthF(thePen.width()*1.25)
        elif linestyle in ['-..', '.-.', '..-']:
            thePen.setDashPattern([0.1, 2, 3, 2, 0.1, 2])
            thePen.setWidthF(thePen.width()*1.25)
        elif linestyle in ['--']:
            thePen.setDashPattern([2.5, 2])
            thePen.setWidthF(thePen.width()*1.1)
        else:
            thePen.setStyle(QtCore.Qt.SolidLine)

    def get_point(self, indexPoint):
        """Return object pyqtgraph.SpotItem"""
        return self.thePlotItem.scatter.points()[indexPoint]
