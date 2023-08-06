import signal
import sys

from PyQt5 import QtCore, QtWidgets, QtGui

if QtWidgets.QApplication.instance() is None:
    app = QtWidgets.QApplication(sys.argv)  # must initialize only once


def start_qt_mainloop():
    """Starts qt mainloop, which is necessary for qt to handle events"""

    def handler_quit(sign_number, _):
        app.quit()
        sys.exit(sign_number)

    try:
        signal.signal(signal.SIGINT, handler_quit)
    except AttributeError:
        pass
    try:
        signal.signal(signal.SIGTSTP, handler_quit)
    except AttributeError:
        pass
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.exec()


def stop_qt_mainloop():
    """Stops qt mainloop and resumes to program"""
    app.quit()


def process_qt_events():
    """Process current qt events"""
    app.processEvents()


class gui_mainWindow(QtWidgets.QMainWindow):
    """
    Main class that spawns a Qt window. Use :meth:`~gui_mainWindow.run` to display it.
    """

    def __init__(self, QtWidgetList, isLight=True, actionOnWindowClosed=None, neverCloseWindow=False, title_window='Awesome Visualisation Tool', size=None):
        """

        :param QtWidgetList: List of QWidgets to display in the window
        :param isLight: Light theme option (bool)
        :param actionOnWindowClosed: Callback before the window closes (method)
        :param neverCloseWindow: Hide the option to kill the window (bool)
        :param title_window: Title of the window (str)
        :param size: Size of the window ([x, y])
        """
        # config
        super(gui_mainWindow, self).__init__()

        if not isLight:
            p = self.palette()  # To change color
            p.setColor(QtGui.QPalette.Background, (30, 30, 30))
            self.setPalette(p)

        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())
        self.mainbox.layout().setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle(title_window)

        if neverCloseWindow:
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.neverCloseWindow = neverCloseWindow

        # Add widgets - QtPlot
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.mainbox.layout().addWidget(splitter)
        for widget in QtWidgetList:
            splitter.addWidget(widget)

        if size is not None:
            self.resize(*size)
            # QtCore.QTimer().singleShot(10, lambda: self.resize(*size))

        self.actionOnWindowClosed = actionOnWindowClosed

    def set_actionOnClose(self, actionOnWindowClosed):
        self.actionOnWindowClosed = actionOnWindowClosed

    def closeEvent(self, event):
        if self.actionOnWindowClosed is not None:
            self.actionOnWindowClosed(self, event)
        super().closeEvent(event)

    def run(self, hold=False):
        """Display the window"""
        self.show()
        self.repaint()
        if hold:
            self.hold()

    @staticmethod
    def hold():
        start_qt_mainloop()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if not self.neverCloseWindow:
                self.deleteLater()
                self.closeEvent(None)
