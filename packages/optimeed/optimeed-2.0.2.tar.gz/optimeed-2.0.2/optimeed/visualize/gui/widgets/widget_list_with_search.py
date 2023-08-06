from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot


class Widget_list_with_search(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout_widget = QtWidgets.QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        self.myListWidget = QtWidgets.QListWidget()

        self.search_plot_data = QtWidgets.QLineEdit()
        # self.search_plot_data.setTabChangesFocus(True)

        self.layout().addWidget(self.search_plot_data)
        self.layout().addWidget(self.myListWidget)

        self.search_plot_data.textChanged.connect(self._filter_list)

    @pyqtSlot()
    def get_index_selected(self):
        return self.myListWidget.currentRow()

    @pyqtSlot()
    def get_name_selected(self):
        return self.myListWidget.currentItem().text()

    def set_list(self, names):
        for name in names:
            self.myListWidget.addItem(name)

    def _filter_list(self):
        text = self.search_plot_data.text()
        for item in self._iter_items():
            if text in item.text():
                item.setHidden(False)
            else:
                item.setHidden(True)
        # print(text)

    def _iter_items(self):
        for i in range(self.myListWidget.count()):
            yield self.myListWidget.item(i)
