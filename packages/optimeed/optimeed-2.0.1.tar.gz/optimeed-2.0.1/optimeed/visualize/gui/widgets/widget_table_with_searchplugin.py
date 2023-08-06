from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from widget_table_with_search import Widget_table_with_search as TheWidget


class Plugin_table_with_search(QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return TheWidget(parent)

    def name(self):
        return "Widget_table_with_search"

    def group(self):
        return "ICS Custom Widgets"

    def icon(self):
        return QIcon()

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    # Returns an XML description of a custom widget instance that describes
    # default values for its properties. Each custom widget created by this
    # plugin will be configured using this description.
    # def domXml(self):
    #     return '<widget class="PyAnalogClock" name="analogClock">\n' \
    #            ' <property name="toolTip">\n' \
    #            '  <string>The current time</string>\n' \
    #            ' </property>\n' \
    #            ' <property name="whatsThis">\n' \
    #            '  <string>The analog clock widget displays the current ' \
    #            'time.</string>\n' \
    #            ' </property>\n' \
    #            '</widget>\n'

    def includeFile(self):
        return "optimeed.visualize.gui.widgets.widget_table_with_search"



