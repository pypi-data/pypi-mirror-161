from PyQt5 import QtWidgets, QtGui, QtCore
import base64


class Widget_image(QtWidgets.QLabel):

    def __init__(self, image_b64):
        """This widget allows to easily visualize any png image and manages redimensioning

        :param image_b64: An encoded base 64 png, typically base64(file.read())
        """

        QtWidgets.QLabel.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.initiaPixmap = QtGui.QPixmap()
        self.set_image(image_b64)
        self.installEventFilter(self)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def eventFilter(self, source, event):
        if source is self and event.type() == QtCore.QEvent.Resize:
            self.setPixmap(self.initiaPixmap.scaled(self.size()*0.95, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        return super().eventFilter(source, event)

    def set_image(self, image_b64):
        """ Set new image to widget """

        self.initiaPixmap.loadFromData(base64.b64decode(image_b64))
        self.setPixmap(self.initiaPixmap)

