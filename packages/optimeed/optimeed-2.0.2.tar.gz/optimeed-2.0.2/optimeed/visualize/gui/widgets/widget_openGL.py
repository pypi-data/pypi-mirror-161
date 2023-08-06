from .openGLWidget.ContextHandler import ContextHandler, SpecialButtonsMapping
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.Qt import QSize
# from PyQt5.QtGui import QColor, QPainter


class widget_openGL(QOpenGLWidget):
    """Interface that provides opengl capabilities.
    Ensures zoom, light, rotation, etc."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theContextHandler = ContextHandler()
        self.theContextHandler.set_specialButtonsMapping(self._get_specialButtonsMapping())
        self.setFocusPolicy(Qt.StrongFocus)
        theFormat = QSurfaceFormat()
        theFormat.setSamples(10)
        self.setFormat(theFormat)
        self.resize(self.sizeHint())

    def sizeHint(self):
        return QSize(400, 400)

    def minimumSizeHint(self):
        return QSize(400, 400)

    def set_deviceDrawer(self, theDeviceDrawer):
        """Set a drawer :class:`optimeed.visualize.gui.widgets.openGLWidget.DeviceDrawerInterface.DeviceDrawerInterface`"""
        self.theContextHandler.set_deviceDrawer(theDeviceDrawer)

    def set_deviceToDraw(self, theDeviceToDraw):
        """Set the device to draw :class:`optimeed.InterfaceDevice.InterfaceDevice`"""
        self.theContextHandler.set_deviceToDraw(theDeviceToDraw)
        self.update()

    @staticmethod
    def _get_specialButtonsMapping():
        theMapping = SpecialButtonsMapping()
        theMapping.KEY_UP = Qt.Key_Up
        theMapping.KEY_DOWN = Qt.Key_Down
        theMapping.KEY_LEFT = Qt.Key_Left
        theMapping.KEY_RIGHT = Qt.Key_Right
        theMapping.KEY_TAB = Qt.Key_Tab
        theMapping.MOUSE_LEFT = Qt.LeftButton
        theMapping.MOUSE_RIGHT = Qt.RightButton
        return theMapping

    def initializeGL(self):
        self.theContextHandler.initialize()
        self.update()

    def paintGL(self):
        self.theContextHandler.redraw()
        # # Uncomment to print text
        # painter = QPainter(self)
        # for text in self.theContextHandler.get_text_to_write():
        #     fontColor = QColor(*text.color)
        #     painter.setPen(fontColor)
        #     painter.drawText(text.position[0], text.position[1], text.theStr)
        # painter.end()

    def resizeGL(self, w, h):
        self.theContextHandler.resizeWindowAction(w, h)
        self.update()

    def mousePressEvent(self, event):
        self.theContextHandler.mouseClicAction(event.button(), event.x(), event.y())
        self.update()

    def mouseMoveEvent(self, event):
        self.theContextHandler.mouseMotionAction(event.x(), event.y())
        self.update()

    def keyPressEvent(self, event):
        self.theContextHandler.keyboardPushAction(event.key())
        super().keyPressEvent(event)
        self.update()

    def wheelEvent(self, QWheelEvent):
        self.theContextHandler.mouseWheelAction(float(QWheelEvent.angleDelta().y())/80.0)
        self.update()
