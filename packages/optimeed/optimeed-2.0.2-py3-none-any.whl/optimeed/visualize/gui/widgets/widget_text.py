from PyQt5 import QtCore, QtGui, QtWidgets
from optimeed.core.ansi2html import Ansi2HTMLConverter


class widget_text(QtWidgets.QLabel):
    """Widget able to display a text"""
    def __init__(self, theText, is_light=False, convertToHtml=False):
        """

        :param theText: str
        :param is_light: light interface (bool)
        :param convertToHtml: if True: allow to use ansi syntax (= colors)
        """
        super().__init__()

        if is_light:  # Template "Light"
            text_color = QtCore.Qt.black
            text_background = QtCore.Qt.white
        else:
            text_color = QtCore.Qt.white
            text_background = QtCore.Qt.black

        p = self.palette()
        p.setColor(QtGui.QPalette.Background, text_background)
        p.setColor(QtGui.QPalette.WindowText, text_color)
        self.setPalette(p)
        self.setAutoFillBackground(True)

        if convertToHtml:
            conv = Ansi2HTMLConverter()
            self.setTextFormat(QtCore.Qt.RichText)
            self.setText(conv.convert(theText))
        else:
            self.setText(theText)
        self.setFont(QtGui.QFont('Arial', 10))
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    def set_text(self, theText, convertToHtml=False):
        """Set the text to display"""
        if convertToHtml:
            conv = Ansi2HTMLConverter()
            self.setTextFormat(QtCore.Qt.RichText)
            self.setText(conv.convert(theText))
        else:
            self.setText(theText)


class scrollable_widget_text(QtWidgets.QWidget):
    """Same as :class:`~widget_text` but scrollable"""
    def __init__(self, theText, is_light=False, convertToHtml=False):
        super().__init__()
        layout_widget = QtWidgets.QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        scrollarea = QtWidgets.QScrollArea()
        self.theWidget = widget_text(theText, is_light, convertToHtml)
        scrollarea.setWidget(self.theWidget)
        scrollarea.setWidgetResizable(True)
        scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.layout().addWidget(scrollarea)
        self.setMinimumHeight(150)

    def set_text(self, theText, convertToHtml=False):
        self.theWidget.set_text(theText, convertToHtml)
