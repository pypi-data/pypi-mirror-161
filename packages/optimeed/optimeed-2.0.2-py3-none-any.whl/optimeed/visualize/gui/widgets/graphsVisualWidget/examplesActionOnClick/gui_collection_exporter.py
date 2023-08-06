from PyQt5 import QtWidgets, QtCore
from optimeed.core.collection import ListDataStruct
import os


class gui_collection_exporter(QtWidgets.QMainWindow):
    """Simple gui that allows to export data"""
    signal_has_exported = QtCore.pyqtSignal()
    signal_has_reset = QtCore.pyqtSignal()

    def __init__(self):
        self.theCollection = ListDataStruct()

        # Create PyQt5 window
        super(gui_collection_exporter, self).__init__()
        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())
        self.mainbox.layout().setContentsMargins(0, 0, 0, 0)

        self.exportButton = QtWidgets.QPushButton('Export Collection', self)
        self.mainbox.layout().addWidget(self.exportButton)
        self.exportButton.clicked.connect(self.exportCollection)

        resetButton = QtWidgets.QPushButton('Reset', self)
        self.mainbox.layout().addWidget(resetButton)
        resetButton.clicked.connect(self.reset)

    def exportCollection(self):
        """Export the collection"""
        dlg = QtWidgets.QFileDialog.getSaveFileName()[0]
        if dlg:
            root, ext = os.path.splitext(dlg)
            filename_collection = root + self.theCollection.get_extension()
            self.theCollection.save(filename_collection)
            self.signal_has_exported.emit()

    def reset(self):
        self.theCollection.reset_data()
        self.signal_has_reset.emit()

    def add_data_to_collection(self, data):
        """
        Add data to the collection to export

        :param data: Whichever type you like
        """
        self.theCollection.add_data(data)
        self.show()

    def set_collection(self, theCollection):
        self.theCollection = theCollection
