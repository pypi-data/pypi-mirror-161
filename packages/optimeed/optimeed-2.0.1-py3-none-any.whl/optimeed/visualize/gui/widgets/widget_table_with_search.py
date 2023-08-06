from PyQt5 import QtWidgets, Qt
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.Qt import QAbstractItemView


class Widget_table_with_search(QtWidgets.QWidget):
    cellChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout_widget = QtWidgets.QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        self.myTableWidget = QtWidgets.QTableWidget()

        # self.myTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.myTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.search_plot_data = QtWidgets.QLineEdit()
        # self.search_plot_data.setTabChangesFocus(True)

        self.layout().addWidget(self.search_plot_data)
        self.layout().addWidget(self.myTableWidget)
        self.forced_hidden_rows = list()

        # Connect signals
        self.myTableWidget.cellChanged.connect(self._cellChanged)
        self.search_plot_data.textChanged.connect(self._filter_list)

    def hideRow(self, row):
        self.myTableWidget.hideRow(row)

    def showRow(self, row):
        self.myTableWidget.showRow(row)

    def force_hide_row(self, row):
        self.forced_hidden_rows.append(row)
        self.hideRow(row)

    def remove_forced_hide_row(self, row):
        self.showRow(row)
        try:
            self.forced_hidden_rows.remove(row)
        except ValueError:
            pass

    @pyqtSlot()
    def get_entries_selected(self):
        results = []
        rows = []
        for index in sorted(self.myTableWidget.selectionModel().selectedRows()):
            row = index.row()
            rows.append(row)
            results_temp = [self.myTableWidget.item(row, k) for k in range(self.myTableWidget.columnCount())]
            results_temp = [res if res is None else res.data(0) for res in results_temp]
            results.append(results_temp)
        return results, rows

    def _cellChanged(self):
        self.cellChanged.emit()

    def set_entries(self, names, numColumns=3, hidden=False):
        self.myTableWidget.setRowCount(len(names))
        self.myTableWidget.setColumnCount(numColumns)
        for k, name in enumerate(names):
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(item.flags() ^ Qt.Qt.ItemIsEditable)
            self.myTableWidget.setItem(k, 0, item)
            if hidden:
                self.forced_hidden_rows.append(k)
                self.hideRow(k)

        header = self.myTableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

    def get_shown_entries(self):
        results = []
        rows = []
        for row in range(self.myTableWidget.model().rowCount()):
            if row not in self.forced_hidden_rows:
                rows.append(row)
                results_temp = [self.myTableWidget.item(row, k) for k in range(self.myTableWidget.columnCount())]
                results_temp = [res if res is None else res.data(0) for res in results_temp]
                results.append(results_temp)
        return results, rows

    def set_item(self, row, col, item):
        self.myTableWidget.setItem(row, col, QtWidgets.QTableWidgetItem(item))

    def get_item(self, row, col):
        return self.myTableWidget.item(row, col)

    def _filter_list(self):
        text = self.search_plot_data.text()
        for k, item in self._iter_items():
            if text in item.text() and k not in self.forced_hidden_rows:
                self.myTableWidget.showRow(k)
            else:
                self.myTableWidget.hideRow(k)

    def _iter_items(self):
        for i in range(self.myTableWidget.rowCount()):
            yield i, self.myTableWidget.item(i, 0)
