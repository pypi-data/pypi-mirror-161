from ..widget_menuButton import widget_menuButton
from PyQt5 import QtWidgets


class guiPyqtgraph:
    """Create a gui for pyqtgraph with trace selection options, export and action on clic choices"""
    def __init__(self, graphsVisual, **kwargs):
        """

        :param graphsVisual: :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.widget_graph_visual`
        :param actionsOnClick: list of  :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.on_graph_click_interface`
        """
        self.theGraphsVisual = graphsVisual
        self.actionsOnClick = kwargs.get('actionsOnClick', list())

        # Define buttons
        horizontalLayout = self.theGraphsVisual.get_layout_buttons()

        button = QtWidgets.QPushButton('Export Graphs', self.theGraphsVisual)
        button.clicked.connect(self.theGraphsVisual.select_folder_and_export)
        horizontalLayout.addWidget(button)

        # Action button
        if self.actionsOnClick:
            comboBox = QtWidgets.QComboBox()
            for action in self.actionsOnClick:
                comboBox.addItem(action.get_name())
            comboBox.currentIndexChanged.connect(lambda index: self.theGraphsVisual.set_actionOnClick(self.actionsOnClick[index]))
            horizontalLayout.addWidget(comboBox)
            comboBox.setCurrentIndex(0)
            self.theGraphsVisual.set_actionOnClick(self.actionsOnClick[0])

        # Link axes button
        button = QtWidgets.QPushButton('Link axes', self.theGraphsVisual)
        button.clicked.connect(self.theGraphsVisual.link_axes)
        horizontalLayout.addWidget(button)

        # Traces manager button
        button = QtWidgets.QPushButton('Manage traces', self.theGraphsVisual)
        self.traceManager = widget_menuButton(button)
        horizontalLayout.addWidget(button)
        self.theGraphsVisual.signal_graph_changed.connect(lambda: self.refreshTraceList())
        self.refreshTraceList()

    def refreshTraceList(self):
        """Refresh all the traces"""
        self.traceManager.clear()
        graphsVisuals = self.theGraphsVisual.get_all_graphsVisual()
        for graphId in self.theGraphsVisual.get_all_graphsVisual():
            theGraph = graphsVisuals[graphId]
            all_traces = theGraph.get_all_traces()
            for trace in all_traces.values():
                theAction = self.traceManager.addAction("[{}] ".format(graphId) + trace.get_data().get_legend())
                theAction.setCheckable(True)
                theAction.setChecked(True)
                theAction.toggled.connect(trace.toggle)
