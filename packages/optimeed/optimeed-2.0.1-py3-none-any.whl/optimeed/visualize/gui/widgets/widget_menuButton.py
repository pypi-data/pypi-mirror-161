from PyQt5 import QtWidgets


class widget_menuButton(QtWidgets.QMenu):
    """Same as QMenu, but integrates it behind a button more easily."""
    def __init__(self, theParentButton):
        super().__init__()
        self.theButton = theParentButton
        self.theButton.setMenu(self)

    def showEvent(self, QShowEvent):
        p = self.pos()
        geo = self.theButton.geometry()
        self.move(p.x() + geo.width() - self.geometry().width(), p.y())

    def mouseReleaseEvent(self, QMouseEvent):
        action = self.activeAction()
        if action is not None and action.isEnabled():
            action.setEnabled(False)
            super().mouseReleaseEvent(QMouseEvent)
            action.setEnabled(True)
            action.trigger()
        else:
            super().mouseReleaseEvent(QMouseEvent)
