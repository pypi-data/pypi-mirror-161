
from optimeed.visualize import ViewOptimizationResults  # This is new. High-level interface to load saved optimization results.

# This is for the visualization, you are already familiar with that.
from optimeed.visualize.gui.widgets.graphsVisualWidget.examplesActionOnClick import *
import os

foldername = "/optimeed/tutorials/Workspace/opti_9"

theViewer = ViewOptimizationResults()  # Create an optimization viewer
theViewer.add_opti_project(os.path.abspath(foldername))  # Add the opti project to it (you can load several, here we only load one)
# Let's start the visualisation! Set the actions on click
theActionsOnClick = list()
theDataLink = theViewer.get_data_link()

theActionsOnClick.append(on_click_extract_pareto(theDataLink, max_x=False, max_y=False))
theActionsOnClick.append(on_graph_click_delete(theDataLink))
theActionsOnClick.append(On_click_tojson(theDataLink))
theActionsOnClick.append(on_graph_click_export_trace(theDataLink, getShadow=True))

# And now we display the graphs ...
theViewer.display_graphs(theActionsOnClick=theActionsOnClick, max_nb_points_convergence=None, light_background=True)
# Once again, nothing easier.theViewer = ViewOptimizationResults()  # Create an optimization viewer
theViewer.add_opti_project(foldername)  # Add the opti project to it (you can load several, here we only load one)

# Let's start the visualisation! Set the actions on click
theActionsOnClick = list()
theDataLink = theViewer.get_data_link()

theActionsOnClick.append(on_click_extract_pareto(theDataLink, max_x=False, max_y=False))
theActionsOnClick.append(On_click_tojson(theDataLink))

# And now we display the graphs ...
theViewer.display_graphs(theActionsOnClick=theActionsOnClick, max_nb_points_convergence=None, light_background=True)
