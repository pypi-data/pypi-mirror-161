from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow, start_qt_mainloop, stop_qt_mainloop
from optimeed.core.graphs import Data, Graphs
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
from optimeed.visualize import on_click_measure


class PlotHolders:
    def __init__(self):
        self.curr_g = None
        self.graphs = Graphs()
        self.theGraphVisual = widget_graphs_visual(self.graphs, refresh_time=-1, is_light=True)
        self.list_actions_on_clik = list()
        # self.new_plot()

    def add_plot(self, x, y, **kwargs):
        if self.curr_g is None:
            self.new_plot()
        theData = Data(x, y, **kwargs)
        return self.curr_g, self.graphs.add_trace(self.curr_g, theData)

    def get_wgGraphs(self):
        return self.theGraphVisual

    def new_plot(self):
        self.curr_g = self.graphs.add_graph()

    def set_title(self, theTitle, **kwargs):
        self.theGraphVisual.set_title(self.curr_g, theTitle, **kwargs)

    def reset(self):
        self.graphs.reset()
        self.curr_g = None

    def axis_equal(self):
        self.theGraphVisual.get_graph(self.curr_g).axis_equal()


class WindowHolders:
    def __init__(self):
        self.figures = dict()
        self.plotHolders = dict()
        self.currFigure = None
        self.actions_on_click = [on_click_measure()]

    def set_currFigure(self, currFigure):
        if currFigure is None:
            self.new_figure()
        else:
            self.currFigure = currFigure

    def add_plot(self, *args, **kwargs):
        if self.currFigure is None:
            self.currFigure = 0
            self.new_figure()
        graph_id, trace_id = self.get_curr_plotHolder().add_plot(*args, **kwargs)
        return self.currFigure, graph_id, trace_id

    def set_title(self, *args, **kwargs):
        self.get_curr_plotHolder().set_title(*args, **kwargs)

    def new_figure(self):
        self.currFigure += 1
        self.plotHolders[self.currFigure] = PlotHolders()

        def actionOnWindowClose(mainWindow, _):
            # stop_qt_mainloop()
            mainWindow.close()
            self.plotHolders[self.currFigure].reset()
            self.currFigure = None
            # self.figures[self.currFigure] = self.create_figure()

        guiPyqtgraph(self.plotHolders[self.currFigure].get_wgGraphs(), actionsOnClick=self.actions_on_click)
        the_mainWindow = gui_mainWindow([self.plotHolders[self.currFigure].get_wgGraphs()], size=[1000, 700], actionOnWindowClosed=actionOnWindowClose)
        self.figures[self.currFigure] = the_mainWindow
        the_mainWindow.run(False)

    def new_plot(self):
        self.get_curr_plotHolder().new_plot()

    def show(self):
        self.figures[self.currFigure].hold()

    def get_curr_plotHolder(self):
        return self.plotHolders[self.currFigure]

    def get_wgGraphs(self, fig=None):
        if fig is None:
            return self.get_curr_plotHolder().get_wgGraphs()
        return self.plotHolders[fig].get_wgGraphs()

    def get_all_figures(self):
        return list(self.figures.keys())

    def axis_equal(self):
        self.get_curr_plotHolder().axis_equal()

    def add_action_on_click(self, theAction):
        self.actions_on_click.append(theAction)


myWindows = WindowHolders()


def plot(x, y, hold=False, **kwargs):
    """Plot new trace"""
    idPlot = myWindows.add_plot(x, y, **kwargs)

    if hold:
        show()

    return idPlot


def show():
    """Show (start qt mainloop) graphs. Blocking"""
    start_qt_mainloop()
    # myWindows.show()


def figure(numb=None):
    """Set current figure"""
    myWindows.set_currFigure(numb)

def add_action_on_click(theAction):
    myWindows.add_action_on_click(theAction)

def set_title(theTitle, **kwargs):
    """Set title of the plot"""
    myWindows.set_title(theTitle, **kwargs)


def axis_equal():
    myWindows.axis_equal()


def get_all_figures():
    """Get all existing figures"""
    return myWindows.get_all_figures()


def get_wgGraphs(fig=None):
    """Advanced option.
    :return: :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.widget_graphs_visual`
    """
    return myWindows.get_wgGraphs(fig)

