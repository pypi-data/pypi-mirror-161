try:
    from scipy.interpolate import griddata
    griddata_found = True
except ImportError:
    griddata_found = False
import numpy as np


class Plot3D_Generic:
    def __init__(self, x_label='', y_label='', z_label='', legend='',
                 x_lim=None, y_lim=None,z_lim=None):
        self.x_label = x_label
        self.y_label = y_label
        self.z_label = z_label
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.z_lim = z_lim
        self.legend = legend

    def get_lim(self, axis):
        return getattr(self, "{}_lim".format(axis))

    def get_label(self, axis):
        return getattr(self, "{}_label".format(axis))

    def get_legend(self):
        return self.legend


class GridPlot_Generic(Plot3D_Generic):
    def __init__(self, X, Y, Z, **kwargs):
        super().__init__(**kwargs)
        self.X = X
        self.Y = Y
        self.Z = Z

    def get_plot_data(self):
        return self.X, self.Y, self.Z


class ContourPlot(GridPlot_Generic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.numberOfContours = kwargs.get("n", 10)
        self.levels = kwargs.get("levels", list())

    def get_levels(self):
        return self.levels

    def get_number_of_contours(self):
        return self.numberOfContours


class FilledContourPlot(ContourPlot):
    pass


class SurfPlot(GridPlot_Generic):
    pass


class MeshPlot(GridPlot_Generic):
    pass


class ScatterPlot3(Plot3D_Generic):
    def __init__(self, x, y, z, **kwargs):
        self.color = kwargs.pop("color", None)
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.z = z

    def get_plot_data(self):
        return self.x, self.y, self.z

    def get_color(self):
        return self.color


def convert_to_gridplot(x, y, z, x_interval=None, y_interval=None, n_x=20, n_y=20):
    """
    Convert set of points x, y, z to a grid

    :param x:
    :param y:
    :param z:
    :param x_interval: [Min, max] of the grid. If none, use min and max values
    :param y_interval: [Min, max] of the grid.  If none, use min and max values
    :param n_x: number of points in x direction
    :param n_y: number of points in y direction
    :return: X, Y, Z as grid
    """
    if griddata_found:

        if x_interval is None:
            x_interval = [min(x), max(x)]
        if y_interval is None:
            y_interval = [min(y), max(y)]
        xi = np.linspace(*x_interval, n_x)
        yi = np.linspace(*y_interval, n_y)
        zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method='cubic')  # 2D array
        return xi, yi, zi
    else:
        raise ImportError("Scipy is needed for that")
