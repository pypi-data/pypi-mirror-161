from PyQt5 import QtCore, QtGui, QtWidgets


class widget_line_drawer(QtWidgets.QWidget):
    """Widget allowing to display several lines easily"""

    signal_must_update = QtCore.pyqtSignal(object)

    # listOfLines[i] = [x_1, y_1, x_2, y_2]
    def __init__(self, minWinHeight=300, minWinWidth=300, is_light=True):
        super().__init__()
        # Set windows width
        self.setMinimumHeight(minWinHeight)
        self.setMinimumWidth(minWinWidth)

        # Set background colour
        p = self.palette()
        self.is_light = is_light
        if self.is_light:
            p.setColor(self.backgroundRole(), QtCore.Qt.white)
        else:
            p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        self.setAutoFillBackground(True)

        # Set objects to draw
        self.dict_listOfLines = {}
        self.dict_pens = {}

        self.signal_must_update.connect(self.on_update_signal)

    def on_update_signal(self, listOfLines):
        self.set_lines(listOfLines=listOfLines)

    def delete_lines(self, key_id):
        """
        Dele the lines
        :param key_id: id to delete
        :return:
        """
        del self.dict_listOfLines[key_id]
        del self.dict_pens[key_id]

    def set_lines(self, listOfLines, key_id=0, pen=None):
        """
        Set the lines to display
        :param listOfLines: list of [x1, y1, x2, y2] corresponding to lines
        :param key_id: id of the trace
        :param pen: pen used to draw the lines
        :return:
        """
        for k, line in enumerate(listOfLines):
            if len(line) == 6:  # Coordinates are (x,y,z) and not (x,y) -> compress
                listOfLines[k] = [line[0], line[1], line[3], line[4]]

        self.dict_listOfLines[key_id] = listOfLines
        if pen is None:
            if self.is_light:
                self.dict_pens[key_id] = QtGui.QPen(QtCore.Qt.black, 1)
            else:
                self.dict_pens[key_id] = QtGui.QPen(QtCore.Qt.white, 1)
        else:
            self.dict_pens[key_id] = QtGui.QPen(pen.color())  # pen
        self.repaint()
        self.update()

    def paintEvent(self, event, painter=None):
        if painter is None:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        x_min, x_max, y_min, y_max = self.get_extrema_lines()
        min_margin = 20
        maxwidth = x_max - x_min
        maxheight = y_max - y_min
        width_window = self.rect().width()
        height_window = self.rect().height()

        try:
            ratio_width = (width_window - min_margin * 2) / maxwidth
            ratio_height = (height_window - min_margin * 2) / maxheight
        except ZeroDivisionError:
            ratio_width = 1
            ratio_height = 1
        ratio = min(ratio_width, ratio_height)

        center_x = (width_window + min_margin * 2 - ratio * maxwidth) / 2
        painter.translate(-min_margin + center_x - x_min * ratio, -(min_margin - y_min * ratio) + height_window)

        for key in self.dict_listOfLines:
            # Set painters and objects to draw
            thePen = self.dict_pens[key]
            thePen.setWidthF(2)
            painter.setPen(thePen)

            for line in self.dict_listOfLines[key]:
                painter.drawLine(line[0]*ratio, -line[1]*ratio, line[2]*ratio, -line[3]*ratio)

            thePen.setWidthF(0.5)
            painter.setPen(thePen)
            painter.drawLine(0, 0, x_max * ratio, 0)
            painter.drawLine(0, 0, 0, -y_max * ratio)

    def get_extrema_lines(self):
        x_min, x_max, y_min, y_max = 0, 1e-12, 0, 1e-12
        for i, key in enumerate(self.dict_listOfLines):
            try:
                x_min_temp = min(min(x[0], x[2]) for x in self.dict_listOfLines[key])
                x_max_temp = max(max(x[0], x[2]) for x in self.dict_listOfLines[key])
                y_min_temp = min(min(x[1], x[3]) for x in self.dict_listOfLines[key])
                y_max_temp = max(max(x[1], x[3]) for x in self.dict_listOfLines[key])

                if i == 0:
                    x_min = x_min_temp
                    x_max = x_max_temp
                    y_min = y_min_temp
                    y_max = y_max_temp
                else:
                    x_min = min(x_min, x_min_temp)
                    x_max = max(x_max, x_max_temp)
                    y_min = min(y_min, y_min_temp)
                    y_max = max(y_max, y_max_temp)
            except (IndexError, ValueError):
                pass
        return x_min, x_max, y_min, y_max

