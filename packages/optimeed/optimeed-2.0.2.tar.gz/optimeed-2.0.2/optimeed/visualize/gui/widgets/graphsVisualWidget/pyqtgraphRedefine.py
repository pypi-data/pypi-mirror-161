from .pyqtgraph.graphicsItems.LegendItem import ItemSample
from .pyqtgraph.graphicsItems.ScatterPlotItem import ScatterPlotItem, drawSymbol
from .pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from .pyqtgraph import functions as fn
from . import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
import os

isOnWindows = os.name == 'nt'


"""Other modified files (directly): ScatterPlotItem.py, to change point selection. Ctrl + clic: select area. Clic: only one single point:


class OnClicSelector:
    def __init__(self):
        self.p_list = []

    def add_point(self, newp):
        self.p_list.append(newp)

    def draw(self, painter):
        if len(self.p_list) > 2:
            pen = fn.mkPen(1)
            pen.setWidthF(2)
            painter.setPen(pen)
            painter.drawPolyline(QtGui.QPolygonF(self.p_list))

    def reset(self):
        self.p_list = []

    def getPath(self):
        return path.Path([(p.x(), p.y()) for p in self.p_list] + [(self.p_list[-1].x(), self.p_list[-1].y())])

------------------------------
    def mouseDragEvent(self, ev):
        if ev.modifiers() and QtCore.Qt.ControlModifier:
            ev.accept()
            self.clicSelector.add_point(ev.pos())
            if ev.isFinish():
                path = self.clicSelector.getPath()
                points = self.points()
                contains_points = path.contains_points([(p.pos().x(), p.pos().y()) for p in points])
                indices = [i for i, cond in enumerate(contains_points) if cond]
                points_clicked = [points[i] for i in indices]
                self.ptsClicked = points_clicked
                self.sigClicked.emit(self, self.ptsClicked)
                self.clicSelector.reset()
            self.update()
        else:
            ev.ignore()
"""


class myGraphicsLayoutWidget(pg.GraphicsView):
    def __init__(self, parent=None, **_kwargs):
        pg.GraphicsView.__init__(self, parent)
        self.ci = myGraphicsLayout()
        for n in ['nextRow', 'nextCol', 'nextColumn', 'addPlot', 'addViewBox', 'addItem', 'getItem', 'addLayout', 'addLabel', 'removeItem', 'itemIndex', 'clear']:
            setattr(self, n, getattr(self.ci, n))
        self.setCentralItem(self.ci)

    def useOpenGL(self, b=True):
        """Overwrited to fix bad antialiasing while using openGL"""
        if b:
            if isOnWindows:
                v = QtOpenGL.QGLWidget()
            else:
                v = QtWidgets.QOpenGLWidget()
                fmt = QtGui.QSurfaceFormat()
                fmt.setSamples(8)
                fmt.setDepthBufferSize(24)
                fmt.setStencilBufferSize(8)  # Fixes antialias zoom error
                v.setFormat(fmt)
        else:
            v = QtGui.QWidget()
        self.setViewport(v)


class myGraphicsLayout(pg.GraphicsLayout):
    def __init__(self):
        super().__init__()
        self.layout.setHorizontalSpacing(-5)
        self.layout.setVerticalSpacing(-5)

    def addItem(self, item, row=None, col=None, rowspan=1, colspan=1):
        """
        Add an item to the layout and place it in the next available cell (or in the cell specified).
        The item must be an instance of a QGraphicsWidget subclass.
        """
        if row is None:
            row = self.currentRow
        if col is None:
            col = self.currentCol

        self.items[item] = []
        for i in range(rowspan):
            for j in range(colspan):
                row2 = row + i
                col2 = col + j
                if row2 not in self.rows:
                    self.rows[row2] = {}
                self.rows[row2][col2] = item
                self.items[item].append((row2, col2))

        self.layout.addItem(item, row, col, rowspan, colspan)
        self.nextRow()

    def set_graph_disposition(self, item, row=1, col=1, rowspan=1, colspan=1):
        """
        Function to modify the position of an item in the list

        :param item: WidgetPlotItem to set
        :param row: Row
        :param col: Column
        :param rowspan:
        :param colspan:
        :return:
        """
        # Remove from existing
        self.layout.removeItem(item)
        for r, c in self.items[item]:
            del self.rows[r][c]

        # Add new configuration
        for i in range(rowspan):
            for j in range(colspan):
                row2 = row + i
                col2 = col + j
                if row2 not in self.rows:
                    self.rows[row2] = {}
                self.rows[row2][col2] = item
                self.items[item].append((row2, col2))
        self.layout.addItem(item, row, col, rowspan, colspan)


class myItemSample(ItemSample):
    def __init__(self, item):
        super().__init__(item)
        self.offset = 13
        self.widthCell = 40

    def set_offset(self, offset):
        self.offset = offset

    def set_width_cell(self, width):
        self.widthCell = width

    # """Overwrites for text closer to the sample"""
    # def boundingRect(self):
    #     return QtCore.QRectF(0, 0, 0, 0)

    def paint(self, p, *args):
        """Overwrites to make matlab-like samples"""
        # p.setRenderHint(p.Antialiasing)  # only if the data is antialiased.
        opts = self.item.opts

        if opts.get('fillLevel', None) is not None and opts.get('fillBrush', None) is not None:
            p.setBrush(fn.mkBrush(opts['fillBrush']))
            p.setPen(fn.mkPen(None))
            p.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(2, 18), QtCore.QPointF(18, 2), QtCore.QPointF(18, 18)]))

        p.save()
        linewidth = self.widthCell
        v_offset = self.offset

        opts = self.item.opts
        if not isinstance(self.item, ScatterPlotItem):
            pen = fn.mkPen(opts['pen'])
            pen.setWidthF(pen.widthF()*0.9)
            p.setPen(pen)
            p.drawLine(0, v_offset, linewidth, v_offset)

        p.restore()

        symbol = opts.get('symbol', None)
        if symbol is not None:
            if isinstance(symbol, list):
                symbol = symbol[0]

            if isinstance(self.item, PlotDataItem):
                opts = self.item.scatter.opts

            pen = fn.mkPen(opts['pen'])
            brush = fn.mkBrush(opts['brush'])
            size = opts['size'] * 1.0  # Scale factor for legend size

            p.translate(linewidth / 2, v_offset)
            drawSymbol(p, symbol, size, pen, brush)


class myLegend(pg.LegendItem):
    """Legend that fixes bugs (flush left + space) from pyqtgraph's legend"""
    def __init__(self, size=None, offset=(30, 30), is_light=False):
        super(myLegend, self).__init__(size, offset)
        self.layout.setVerticalSpacing(-8)

        self.is_light = is_light
        self.width_cell_sample = 25

    def set_space_sample_label(self, theSpace):
        """To set the gap between the sample and the label"""
        self.layout.setHorizontalSpacing(theSpace)

    def set_offset_sample(self, offset):
        """To tune the offset between the sample and the text"""
        for sample, label in self.items:
            sample.set_offset(offset)

    def set_width_cell_sample(self, width):
        """Set width of sample"""
        self.width_cell_sample = width
        self.apply_width_sample()

    def updateSize(self):
        if self.size is not None:
            return
        height = 0
        width = 0
        for sample, label in self.items:
            height += max(sample.boundingRect().height(), label.height())
            width = max(width, sample.boundingRect().width() + label.width())  # + 13
        self.setGeometry(0, 0, width, height)

    def addItem(self, item, name):
        """Overwrites to flush left"""
        # label = LabelItem(name)
        label = myLabelItem(name, justify='left')
        width_cell = self.width_cell_sample
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = myItemSample(item)
            sample.set_width_cell(width_cell*1)
        row = self.layout.rowCount()

        self.items.append((sample, label))
        self.layout.addItem(sample, row, 0)
        self.layout.setColumnFixedWidth(0, width_cell)
        self.layout.setColumnFixedWidth(1, 10)
        self.layout.setHorizontalSpacing(0.0)  # No spacing between sample and text
        self.layout.addItem(label, row, 1)
        self.layout.setRowFixedHeight(row, 15)

        self.updateSize()

    def apply_width_sample(self):
        width_cell = self.width_cell_sample
        for sample, label in self.items:
            sample.set_width_cell(width_cell*1)
        self.layout.setColumnFixedWidth(0, width_cell)
        self.updateSize()

    def set_font(self, font_size, font_color, fontname=None):
        for item in self.items:
            for single_item in item:
                if isinstance(single_item, pg.LabelItem):
                    if fontname is not None:
                        single_item.setText(single_item.text, **{'color': font_color, 'size': str(font_size) + 'pt', 'font-family': fontname})
                    else:
                        single_item.setText(single_item.text, **{'color': font_color, 'size': str(font_size) + 'pt'})

    def paint(self, p, *args):
        """Overwrited to select background color"""
        if len(self.items):
            if self.is_light:
                p.setPen(pg.mkPen(100, 100, 100, 255))
                p.setBrush(pg.mkBrush(255, 255, 255, 255))
            else:
                p.setPen(pg.mkPen(100, 100, 100, 255))
                p.setBrush(pg.mkBrush(10, 10, 10, 255))
            offset_x = 0
            offset_y = 20
            boundingRect = QtCore.QRectF(0, offset_y/2, self.width()-offset_x, self.height()-offset_y)
            p.drawRect(boundingRect)  # self.boundingRect())

    def set_position(self, position, offset):
        """
        Set the position of the legend, in a corner.

        :param position: String (NW, NE, SW, SE), indicates which corner the legend is close
        :param offset: Tuple (xoff, yoff), x and y offset from the edge
        :return:
        """
        offPosMult = 1

        if position == "NW":
            quartil_parent = (0, 0)
            oxMult, oyMult = 1, 1
        elif position == "NE":
            quartil_parent = (1, 0)
            oxMult, oyMult = -1, 1
        elif position == "SW":
            quartil_parent = (0, 1)
            oxMult, oyMult = 1, -1
            offPosMult = -1
        elif position == "SE":
            quartil_parent = (1, 1)
            oxMult, oyMult = -1, -1
            offPosMult = -1
        else:
            print("Could not place legend : position unknown (please use NW, NE, SW or SE)")
            return
        self.anchor(quartil_parent, quartil_parent, offset=(offset[0] * oxMult, offPosMult * (-10) + offset[1] * oyMult))  # * -10: corresponds to offset_y defined in paint


class myLabelItem(pg.LabelItem):
    def setText(self, text, **args):
        """ Overwrited to add font-family to options """
        self.text = text
        opts = self.opts
        for k in args:
            opts[k] = args[k]

        optlist = []

        color = self.opts['color']
        if color is None:
            color = pg.getConfigOption('foreground')
        color = fn.mkColor(color)
        optlist.append('color: #' + fn.colorStr(color)[:6])
        if 'size' in opts:
            optlist.append('font-size: ' + opts['size'])
        if 'bold' in opts and opts['bold'] in [True, False]:
            optlist.append('font-weight: ' + {True: 'bold', False: 'normal'}[opts['bold']])
        if 'italic' in opts and opts['italic'] in [True, False]:
            optlist.append('font-style: ' + {True: 'italic', False: 'normal'}[opts['italic']])
        if 'font-family' in opts:
            optlist.append('font-family: ' + opts['font-family'])
        full = "<span style='%s'>%s</span>" % ('; '.join(optlist), text)
        # print full
        self.item.setHtml(full)
        self.updateMin()
        self.resizeEvent(None)
        self.updateGeometry()


class myAxis(pg.AxisItem):
    update_label = QtCore.pyqtSignal(str)

    def __init__(self, orientation):
        super().__init__(orientation)
        self.nudges = {'left': (-10, 0), 'right': (5, 0), 'bottom': (0, -5), 'top': (0, 5)}
        self.update_label.connect(self.label.setHtml)
        # self.style.update({'textFillLimits': [(0, 0.8),    ## never fill more than 80% of the axis
        #         (4, 0.4),    ## If we already have 4 ticks with text, fill no more than 40% of the axis
        #         (6, 0.2)]})

    def _updateLabel(self):
        # self.label.setHtml(self.labelString())
        self.update_label.emit(self.labelString())  # Use of a signal/slot instead of directly changing the value
        self._adjustSize()
        self.picture = None
        self.update()

    def get_label_pos(self):
        """Overwrited to place label closer to the axis"""
        br = self.label.boundingRect()
        x, y = 0, 0
        if self.orientation == 'left':
            y, x = int(self.size().height()/2 + br.width()/2), 0
        elif self.orientation == 'right':
            y, x = int(self.size().height()/2 + br.width()/2), int(self.size().width()-br.height())
        elif self.orientation == 'top':
            y, x = 0, int(self.size().width()/2. - br.width()/2.)
        elif self.orientation == 'bottom':
            x, y = int(self.size().width()/2. - br.width()/2.), int(self.size().height()-br.height())
        try:
            return int(x + self.nudges[self.orientation][0]), int(y - self.nudges[self.orientation][1])
        except AttributeError:
            return x, y

    def resizeEvent(self, ev=None):
        """Overwrited to place label closer to the axis"""
        p = QtCore.QPointF(0, 0)
        x_pos, y_pos = self.get_label_pos()
        p.setX(int(x_pos))
        p.setY(int(y_pos))
        self.label.setPos(p)
        self.picture = None

    def set_label_pos(self, orientation, x_offset=0, y_offset=0):
        self.nudges[orientation] = (x_offset, y_offset)

    def set_number_ticks(self, number):
        self.style.update({'textFillLimits': [(number, 0)]})
