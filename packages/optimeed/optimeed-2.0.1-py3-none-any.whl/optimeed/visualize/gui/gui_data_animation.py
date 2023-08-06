from PyQt5 import QtCore, QtWidgets, QtSvg, QtGui
from abc import abstractmethod
import subprocess
import os
import math


class DataAnimationTrace:
    """Contains all the element to animate for a trace"""
    class element_animation:
        def __init__(self, elements):
            self.elements = elements

        def get(self):
            return self.elements

    def __init__(self, elements_list, theTrace):
        self.curr_index = 0
        self.indices_to_show = []

        self.element_animations = []
        for elements in elements_list:
            self.element_animations.append(self.element_animation(elements))

        self.theTrace = theTrace
        self.nbr_elements = len(self.element_animations[0].get())

    def get_element_animations(self, itemNumber, index_in_show):
        """
        Get the element to show
        :param itemNumber: item number (0 if only one think to draw)
        :param index_in_show: index in the list
        :return: The element to draw
        """
        return self.element_animations[itemNumber].get()[self.map_index(index_in_show)]

    def show_all(self):
        self.delete_all()
        self.indices_to_show = list(range(self.nbr_elements))
        self.curr_index = 0

    def delete_all(self):
        self.theTrace.reset_all_brushes()
        self.indices_to_show = []
        self.curr_index = 0

    def get_indices_to_show(self):
        return self.indices_to_show

    def add_element(self, indexPoint):
        if indexPoint not in self.get_indices_to_show():
            self.add_index_to_show(indexPoint)
            self.theTrace.set_brush(indexPoint, (250, 250, 0))
        else:
            self._remove_index_from_show(indexPoint)

    def add_index_to_show(self, index):
        self.indices_to_show.append(index)

    def _remove_index_from_show(self, index):
        self.theTrace.reset_brush(index)
        self.get_indices_to_show().remove(index)

    def set_curr_brush(self, index_in_show):
        self.theTrace.set_brush(self.map_index(index_in_show), (0, 0, 250))

    def set_idle_brush(self, index_in_show):
        self.theTrace.set_brush(self.map_index(index_in_show), self.theTrace.get_base_symbol_brush().color().lighter(150))

    def get_number_of_elements(self):
        return len(self.get_indices_to_show())

    def map_index(self, index_in_show):
        try:
            return self.get_indices_to_show()[index_in_show]
        except IndexError:
            return 0

    def get_base_pen(self):
        return self.theTrace.get_base_pen()


class DataAnimationVisuals(QtWidgets.QMainWindow):
    """Spawns a gui that includes button to create animations nicely when paired with :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual`"""
    SlIDER_MAXIMUM_VALUE = 500
    SLIDER_MINIMUM_VALUE = 1

    def __init__(self, id=0, window_title='Animation'):
        """

        :param id: id of the window (int)
        :param window_title: Title of the window (str)
        """

        self.refresh_time = 0.1
        self.isRunning = False
        self.data_animation_traces = dict()
        self.id = id

        # Create PyQt5 window
        super(DataAnimationVisuals, self).__init__()
        self.mainbox = QtWidgets.QWidget()
        self.setWindowTitle(window_title)
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())
        self.mainbox.layout().setContentsMargins(0, 0, 0, 0)

        self.horizontal_layout_visu = QtWidgets.QHBoxLayout()
        self.mainbox.layout().addLayout(self.horizontal_layout_visu)

        # Add button panels
        horizontal_layout = QtWidgets.QHBoxLayout()

        # First: Show all
        button = QtWidgets.QPushButton('Show All', self)
        button.clicked.connect(self.show_all)
        horizontal_layout.addWidget(button)

        # Second: Delete All
        button = QtWidgets.QPushButton('Delete All', self)
        button.clicked.connect(self.delete_all)
        horizontal_layout.addWidget(button)

        # Third: Pause
        self.isPlaying = True
        self.pause_play_button = QtWidgets.QPushButton('Pause', self)
        self.pause_play_button.clicked.connect(self.pause_play)
        horizontal_layout.addWidget(self.pause_play_button)

        # Fourth: Speed
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(self.SLIDER_MINIMUM_VALUE)
        self.slider.setMaximum(self.SlIDER_MAXIMUM_VALUE)
        self.slider.valueChanged.connect(self.slider_handler)
        self.mainbox.layout().addWidget(self.slider)

        # Put them in layout
        self.mainbox.layout().addLayout(horizontal_layout)

        # Add export option
        exportButton = QtWidgets.QPushButton('Export', self)
        exportButton.clicked.connect(self.export_picture)
        self.mainbox.layout().addWidget(exportButton)

    def add_trace(self, trace_id, element_list, theTrace):
        """
        Add a trace to the animation.

        :param trace_id: id of the trace
        :param element_list: List of elements to save: [[OpenGL_item1, text_item1], [OpenGL_item2, text_item2], ... [OpenGL_itemN, text_itemN]]
        :param theTrace: :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.TraceVisual.TraceVisual`
        :return:
        """
        self.data_animation_traces[trace_id] = DataAnimationTrace(self.get_interesting_elements(element_list), theTrace)

    @staticmethod
    def get_interesting_elements(element_list):
        """
        Function called upon new trace creation. From a list, takes the interesting elements for animation
        :param element_list:
        :return: new_element_list
        """
        return [element_list]

    def add_elementToTrace(self, trace_id, indexPoint):
        self.data_animation_traces[trace_id].add_element(indexPoint)

    def delete_point(self, trace_id, thePoint):
        self.data_animation_traces[trace_id].delete_point(thePoint)

    def reset_all(self):
        for trace_id in self.data_animation_traces:
            self.data_animation_traces[trace_id].delete_all()

    def delete_all(self):
        self.isRunning = False
        self.reset_all()
        for key in self.data_animation_traces:
            self.delete_key_widgets(key)

        self.data_animation_traces = dict()

    def pause_play(self):
        if self.isRunning:
            self.pause_play_button.setText("Play")
            self.isRunning = False
        else:
            self.pause_play_button.setText("Pause")
            self.run()
            self.isRunning = True

    def show_all(self):
        buff_state_running = self.isRunning
        self.reset_all()
        for key in self.data_animation_traces:
            self.data_animation_traces[key].show_all()
        self.isRunning = buff_state_running
        self.run()

    def next_frame(self):
        if self.isRunning:
            try:
                for key in self.data_animation_traces:
                    the_data_animation = self.data_animation_traces[key]
                    the_data_animation.set_idle_brush(the_data_animation.curr_index)

                    the_data_animation.curr_index += 1
                    the_data_animation.curr_index = the_data_animation.curr_index % the_data_animation.get_number_of_elements()

                    the_data_animation.set_curr_brush(the_data_animation.curr_index)
                    self.update_widget_w_animation(key, the_data_animation.curr_index, the_data_animation)
            except (AttributeError, ZeroDivisionError):
                pass

            QtCore.QTimer().singleShot(int(self.refresh_time*1000), self.next_frame)

    def slider_handler(self):
        if self.isRunning:
            self.set_refreshTime()
        else:
            self.frame_selector()

    def frame_selector(self):
        for key in self.data_animation_traces:
            data_animation_trace = self.data_animation_traces[key]
            slider_value = self.slider.value()
            a = (data_animation_trace.get_number_of_elements()-1)/(self.SlIDER_MAXIMUM_VALUE - self.SLIDER_MINIMUM_VALUE)
            b = -a*self.SLIDER_MINIMUM_VALUE
            selected_index = min(math.floor(a*slider_value+b), data_animation_trace.get_number_of_elements()-1)

            self.data_animation_traces[key].set_idle_brush(data_animation_trace.curr_index)
            data_animation_trace.curr_index = selected_index
            data_animation_trace.set_curr_brush(data_animation_trace.curr_index)
            self.update_widget_w_animation(key, selected_index, data_animation_trace)

    def set_refreshTime(self):
        self.refresh_time = self.slider.value()/1000

    def is_empty(self):
        is_empty = True
        for key in self.data_animation_traces:
            if len(self.data_animation_traces[key].get_indices_to_show()):
                is_empty = False
        return is_empty

    def run(self):
        if (not self.isRunning) and (not self.is_empty()):
            self.show()
            self.isRunning = True
            self.next_frame()

    def closeEvent(self, _):
        self.isRunning = False
        self.delete_all()

    def contains_trace(self, trace_id):
        return trace_id in self.data_animation_traces

    def export_picture(self):
        dlg = QtWidgets.QFileDialog.getSaveFileName()[0]
        if dlg:
            root, ext = os.path.splitext(dlg)
            filename_png = root + '.png'
            filename_svg = root + '.svg'

            # Create exporter
            generator = QtSvg.QSvgGenerator()
            generator.setFileName(filename_svg)
            painter = QtGui.QPainter()
            painter.begin(generator)
            self.export_widget(painter)
            painter.end()

            with open(filename_svg, 'r') as f:
                lines = f.read()
                lines = lines.replace('vector-effect="non-scaling-stroke"', 'stroke-width="2"')
            with open(filename_svg, 'w') as f:
                f.write(lines)
            converter_cmd_line = 'inkscape -z ' + filename_svg + ' -D -e ' + filename_png + ' -d 400'
            subprocess.Popen(converter_cmd_line, shell=True)

    @abstractmethod
    def export_widget(self, painter):
        """
        Render scene with a painter

        :param painter: PyQt painter
        """
        pass

    @abstractmethod
    def update_widget_w_animation(self, key, index, the_data_animation):
        """
        What to do when a new element has to be animated. Example: self.theOpenGLWidget.set_deviceToDraw(the_data_animation.get_element_animations(0, index))

        :param key: key of the trace that has to be animated
        :param index: index that has to be animated
        :param the_data_animation: :class:`~DataAnimationTrace` that has to be animated
        """
        pass

    @abstractmethod
    def delete_key_widgets(self, key):
        """
        What to do when a key has to be deleted

        :param key: key of the trace that has to be deleted
        """
        pass
