from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from optimeed.visualize.gui.gui_data_animation import DataAnimationVisuals
from optimeed.visualize.gui.widgets.widget_text import scrollable_widget_text
from optimeed.visualize.gui.widgets.widget_line_drawer import widget_line_drawer
import traceback


"""Classes for Data Animation"""


class DataAnimationOpenGL(DataAnimationVisuals):
    """Implements :class:`~DataAnimationVisuals` to show opengl drawing"""
    def __init__(self, theOpenGLWidget, theId=0, window_title='Animation'):
        super().__init__(theId, window_title)
        self.theOpenGLWidget = theOpenGLWidget
        self.horizontal_layout_visu.addWidget(self.theOpenGLWidget)

    def update_widget_w_animation(self, key, index, the_data_animation):
        self.theOpenGLWidget.set_deviceToDraw(the_data_animation.get_element_animations(0, index))

    def export_widget(self, painter):
        pass

    def delete_key_widgets(self, key):
        pass


class DataAnimationOpenGLwText(DataAnimationOpenGL):
    """Implements :class:`~DataAnimationVisuals` to show opengl drawing and text"""
    def __init__(self, *args, is_light=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.textWidget = scrollable_widget_text('', is_light=is_light, convertToHtml=False)
        self.horizontal_layout_visu.addWidget(self.textWidget)

    def update_widget_w_animation(self, key, index, the_data_animation):
        super().update_widget_w_animation(key, index, the_data_animation)
        self.textWidget.set_text(the_data_animation.get_element_animations(1, index), convertToHtml=True)

    def get_interesting_elements(self, devices_list):
        all_listOfText = [str(device) for device in devices_list]
        return [devices_list, all_listOfText]


class DataAnimationLines(DataAnimationVisuals):
    """Implements :class:`~DataAnimationVisuals` to show drawing made out of lines (:class:`~optimeed.visualize.gui.widgets.widget_line_drawer`)"""
    def __init__(self, get_lines_method, is_light=True, theId=0, window_title='Animation'):
        """

        :param get_lines_method: Method that takes Device as argument and returns list of lines
        :param is_light:
        :param theId:
        :param window_title:
        """
        super().__init__(theId, window_title)
        self.qtLinesDrawer = widget_line_drawer(is_light=is_light)
        self.horizontal_layout_visu.addWidget(self.qtLinesDrawer)
        self.get_lines_method = get_lines_method

    def export_widget(self, painter):
        self.qtLinesDrawer.paintEvent(event=None, painter=painter)

    def delete_key_widgets(self, key):
        self.qtLinesDrawer.delete_lines(key)

    def update_widget_w_animation(self, key, index, the_data_animation):
        self.qtLinesDrawer.set_lines(the_data_animation.get_element_animations(0, index), key_id=key, pen=the_data_animation.get_base_pen())

    def get_interesting_elements(self, devices_list):
        all_listsOfLines = [self.get_lines_method(device) for device in devices_list]
        all_listOfText = [str(device) for device in devices_list]
        return [all_listsOfLines, all_listOfText]


class DataAnimationVisualswText(DataAnimationLines):
    """Same as :class:`~DataAnimationLines` but also with text"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textWidget = scrollable_widget_text('', is_light=kwargs.get("is_light", True), convertToHtml=False)
        self.horizontal_layout_visu.addWidget(self.textWidget)

    def update_widget_w_animation(self, key, index, the_data_animation):
        self.qtLinesDrawer.set_lines(the_data_animation.get_element_animations(0, index), key_id=key, pen=the_data_animation.get_base_pen())
        self.textWidget.set_text(the_data_animation.get_element_animations(1, index), convertToHtml=True)


class on_graph_click_showAnim(on_graph_click_interface):
    """On click: add or remove an element to animate"""

    def __init__(self, theLinkDataGraph, theAnimation):
        """

        :param theLinkDataGraph: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        :param theAnimation: :class:`~DataAnimationVisuals`
        """
        self.theLinkDataGraph = theLinkDataGraph
        self.theAnimation = theAnimation

    def graph_clicked(self, theGraphVisual, index_graph, index_trace, indices_points):
        try:
            trace_id = int(index_graph) * 100 + int(index_trace)
            theTrace = theGraphVisual.get_graph(index_graph).get_trace(index_trace)

            # index_in_data = theTrace.get_data().get_dataIndex_from_graphIndex(index_point)

            permutation = theTrace.theData.get_permutations()
            indicesInGraph = list(range(len(permutation)))  # Orders them accordingly to plot (data -> plot)
            all_listsOfDevices = self.theLinkDataGraph.get_clicked_items(index_graph, index_trace, indicesInGraph)

            # If trace wasn't present in any window ...
            if not self.theAnimation.contains_trace(trace_id):
                self.theAnimation.add_trace(trace_id, all_listsOfDevices, theTrace)
            for index_point in indices_points:
                index_in_graph = index_point
                self.theAnimation.add_elementToTrace(trace_id, index_in_graph)

            self.theAnimation.run()
        except KeyboardInterrupt:
            raise
        except Exception:
            print("Following error occurred in visualisation :" + traceback.format_exc())

    def get_name(self):
        return "Animation"
