from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow
from optimeed.visualize.gui.widgets.widget_openGL import widget_openGL
from optimeed.visualize.gui.widgets.widget_line_drawer import widget_line_drawer
from optimeed.visualize.gui.widgets.widget_text import scrollable_widget_text
from optimeed.core.tools import str_all_attr, rgetattr
import traceback


class on_graph_click_draw_device(on_graph_click_interface):
    """On click: show informations about the points (loop through attributes)"""
    class DataInformationVisuals:
        def __init__(self):
            self.listOfVisuals = {}
            self.theTraces = {}
            self.indicesPoints = {}
            self.index = 0

        def delete_visual(self, theVisual):
            goodkey = 0
            for key in self.listOfVisuals:
                if self.listOfVisuals[key] == theVisual:
                    goodkey = key
            self.theTraces[goodkey].reset_brush(self.indicesPoints[goodkey])

        def add_visual(self, theVisual, theTrace, indexPoint):
            theTrace.set_brush(indexPoint, (250, 250, 0))

            index = self.get_new_index()
            self.listOfVisuals[index] = theVisual
            self.indicesPoints[index] = indexPoint
            self.theTraces[index] = theTrace

            theVisual.move(10, 0)
            theVisual.setWindowTitle("Visual information of point " + str(index))
            # Put all previously opened window on top
            for key in self.listOfVisuals:
                self.listOfVisuals[key].raise_()

        def get_new_index(self):
            self.index += 1
            return self.index

        def curr_index(self):
            return self.index

    def __init__(self, theLinkDataGraph, visuals=None):
        """

        :param theLinkDataGraph: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        """
        self.theLinkDataGraph = theLinkDataGraph
        self.dataInformationVisuals = self.DataInformationVisuals()
        if visuals is None:
            self.visuals = list()
        else:
            self.visuals = visuals

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        """Action to perform when a point in the graph has been clicked:
        Creates new window displaying the device and its informations
        """
        try:
            def actionOnWindowClosed(theVisual, _):
                """Action to perform when a window has been closed:
                Remove the window from the dataInformationVisuals
                """
                theVisual.close()
                self.dataInformationVisuals.delete_visual(theVisual)

            theTrace = theGraphVisual.get_graph(index_graph).get_trace(index_trace)
            for index_point in indices_points:
                theDevice = self.theLinkDataGraph.get_clicked_item(index_graph, index_trace, index_point)

                theWidgetList = list()
                for visual in self.visuals:
                    theWidgetList.append(visual.get_widget(theDevice))
                theWidgetList.append(scrollable_widget_text(str_all_attr(theDevice, 5), is_light=True, convertToHtml=True))

                visual_temp = gui_mainWindow(theWidgetList, actionOnWindowClosed=actionOnWindowClosed)
                self.dataInformationVisuals.add_visual(visual_temp, theTrace, index_point)
                visual_temp.run(False)
        except KeyboardInterrupt:
            raise
        except Exception:
            print("Following error occurred in visualisation :" + traceback.format_exc())

    def get_name(self):
        return "Show informations"


class Repr_lines:
    def __init__(self, attribute_lines):
        self.attribute_lines = attribute_lines

    def get_widget(self, theNewDevice):
        widgetLineDrawer = widget_line_drawer()
        widgetLineDrawer.set_lines(rgetattr(theNewDevice, self.attribute_lines))
        return widgetLineDrawer


class Repr_opengl:
    def __init__(self, DeviceDrawer):
        self.DeviceDrawer = DeviceDrawer

    def get_widget(self, theNewDevice):
        theOpenGLWidget = widget_openGL()
        theOpenGLWidget.set_deviceDrawer(self.DeviceDrawer)
        theOpenGLWidget.set_deviceToDraw(theNewDevice)
        return theOpenGLWidget
