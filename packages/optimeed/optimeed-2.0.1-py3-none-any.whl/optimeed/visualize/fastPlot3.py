from optimeed.core import FilledContourPlot, ContourPlot, SurfPlot, MeshPlot, ScatterPlot3, printIfShown, SHOW_WARNING

try:
    from plotly import graph_objects as go
    hasPlotly = True
except ImportError:
    hasPlotly = False
except ImportError:
    printIfShown("3D plots deactivated (impossible to import graph_objects)", SHOW_WARNING)
    hasPlotly = False

if hasPlotly:
    def _do_scatterPlot(theData: ScatterPlot3):
        x, y, z = theData.get_plot_data()

        return go.Scatter3d(x=x, y=y, z=z, mode='markers', name=theData.get_legend(), showlegend=True, marker=dict(
            size=5,
            color=z if theData.get_color() is None else theData.get_color(),
            colorscale='Viridis',  # choose a colorscale
            opacity=1.0
        ))


    def _do_contourPlot(theData: ContourPlot):
        x, y, z = theData.get_plot_data()
        return go.Contour(x=x, y=y, z=z, contours_coloring='lines', line_smoothing=0.85, contours={'showlabels': True})


    def _do_filledcontourPlot(theData: FilledContourPlot):
        x, y, z = theData.get_plot_data()
        return go.Contour(x=x, y=y, z=z, line_smoothing=0.85)


    def _do_surfPlot(theData: SurfPlot):
        x, y, z = theData.get_plot_data()
        return go.Surface(x=x, y=y, z=z)


    def _do_meshPlot(theData: MeshPlot):
        x, y, z = theData.get_plot_data()
        return go.Mesh3d(x=x, y=y, z=z)


    def _get_goPlot(theData):
        if isinstance(theData, SurfPlot):
            return _do_surfPlot(theData)
        elif isinstance(theData, MeshPlot):
            return _do_meshPlot(theData)
        elif isinstance(theData, FilledContourPlot):
            return _do_filledcontourPlot(theData)
        elif isinstance(theData, ContourPlot):
            return _do_contourPlot(theData)
        elif isinstance(theData, ScatterPlot3):
            return _do_scatterPlot(theData)
        else:
            raise NotImplementedError()


    def plot3d(listOfData3D, options_x=None, options_y=None, options_z=None):
        fig = go.Figure(data=list(map(_get_goPlot, listOfData3D)))
        options = {"x": options_x, "y": options_y, "z": options_z}

        for axis in ["x", "y", "z"]:
            if options[axis] is None:
                options[axis] = dict()
            for data3D in listOfData3D:
                if data3D.get_label(axis):
                    options[axis].update({"title": data3D.get_label(axis)})
                if data3D.get_lim(axis) is not None:
                    options[axis].update({"range": data3D.get_lim(axis)})
        fig.update_layout(
            scene=dict(
                xaxis=options["x"],
                yaxis=options["y"],
                zaxis=options["z"], ),
        )
        fig.layout.scene.camera.projection.type = "orthographic"
        fig.show()
        return fig
else:
    def plot3d(*args, **kwargs):
        printIfShown("3D plots deactivated (plotly not installed)", SHOW_WARNING)
