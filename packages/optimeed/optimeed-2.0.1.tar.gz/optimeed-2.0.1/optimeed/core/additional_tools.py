import math
from optimeed.core import printIfShown, SHOW_WARNING

try:
    import scipy.spatial.qhull as qhull
    has_scipy = True
except ImportError:
    has_scipy = False
import numpy as np


class fast_LUT_interpolation:
    """Class designed for fast interpolation in look-up table when successive searchs are called often.
    Otherwise use griddata"""

    def __init__(self, independent_variables, dependent_variables):
        """

        :param independent_variables: np.array of shape (N,d) containing the independent variables of the dataset to interpolate. Typically X for 1D LU, or XY for 2D LUT
        :param dependent_variables: np.array of shape (1,d) containing the dependet variables of the dataset to interpolate. Typically Y for 1D LU, or Z for 2D LUT
        """
        self.param_ind = independent_variables
        self.param_dep = dependent_variables
        self.tri = self.interp_tri(independent_variables)
        self.dim = independent_variables.shape[1]

    @staticmethod
    def interp_tri(xyz):
        if has_scipy:
            tri = qhull.Delaunay(xyz)
        else:
            printIfShown("Scipy library not found -> fast_LUT_interpolation has been deactivated", SHOW_WARNING)
        return tri

    def interpolate(self, point, fill_value=np.nan):
        """
        Perform the interpolation
        :param point: coordinates to interpolate (tuple or list of tuples for multipoints)
        :param fill_value: value to put if extrapolated.
        :return: coordinates
        """
        d = self.dim
        tri = self.tri
        values = self.param_dep
        simplex = tri.find_simplex(point)
        vertices = np.take(tri.simplices, simplex, axis=0)
        temp = np.take(tri.transform, simplex, axis=0)
        delta = point - temp[:, d]
        bary = np.einsum('njk,nk->nj', temp[:, :d, :], delta)
        wts = np.hstack((bary, 1.0 - bary.sum(axis=1, keepdims=True)))
        ret = np.einsum('nj,nj->n', np.take(values, vertices), wts)
        ret[np.any(wts < 0, axis=1)] = fill_value
        return ret


def interpolate_table(x0, x_values, y_values):
    """From sorted table (x,y) find y0 corresponding to x0 (linear interpolation)"""
    index = np.searchsorted(x_values, x0)
    def _interpolate(x0, x_values, y_values, index):
        if index == len(x_values):
            return y_values[-1]
        if index == 0:
            return y_values[0]
        x_before, y_before = x_values[index-1], y_values[index-1]
        x_after, y_after = x_values[index], y_values[index]

        for x, y in [(x_before, y_before), (x_after, y_after)]:
            if x == x0:
                return y

        ratio = (x0 - x_before)/(x_after-x_before)
        return y_before + ratio*(y_after - y_before)

    if isinstance(index, np.ndarray):
        results = [0.0]*len(index)
        for k, ind in enumerate(index):
            results[k] = _interpolate(x0[k], x_values, y_values, ind)
        return results
    else:
        return _interpolate(x0, x_values, y_values, index)


def derivate(t, y):
    derivated = [0.0]*len(y)
    for i in range(1, len(y)-1):
        derivated[i] = (y[i+1] - y[i-1])/(t[i+1] - t[i-1])
    derivated[-1] = (y[1] - y[-2])/((t[-1]-t[-2]) + (t[1]-t[0]))
    derivated[0] = derivated[-1]
    return derivated


def linspace(start, stop, npoints):
    return np.linspace(start, stop, npoints).tolist()


def reconstitute_signal(amplitudes, phases, numberOfPeriods=1, x_points=None, n_points=50):
    """Reconstitute the signal from fft. Number of periods of the signal must be specified if different of 1"""
    if x_points is None:
        x_points = np.linspace(0, 2*np.pi*numberOfPeriods, num=int(n_points))
    n_points = len(x_points)
    y = np.zeros(n_points)
    for key in amplitudes:
        y += amplitudes[key] * np.cos(key/numberOfPeriods * x_points + phases[key])
    return x_points, y
# def my_ifft(amplitude, angle, hasBeenTruncated=True):
#     """Inverse fft of signal.
#     If hasBeenTruncated (initial fft signal was full period (including first point of next period):
#     Axis vector must be multiplied by (n_points-1)/(n_points-2)"""
#     amplitudes = list(amplitude.values())
#     angles = list(angle.values())
#     n_points = (len(angles))*2
#     normalization = 2/n_points
#     if hasBeenTruncated:
#         normalization *= (n_points+1)/(n_points-1)
#     coeffs = np.array([amplitudes[i] * np.exp(1j*angles[i]) for i in range(len(angles))])
#     return np.fft.irfft(coeffs)/normalization


def my_fft(y):
    """Real FFT of signal Bx, with real amplitude of harmonics. Input signal must be within a period."""
    if np.isclose(y[0], y[-1]):
        y = y[:-1]
    n_points = len(y)
    normalization = 2/n_points
    res = np.fft.rfft(y)*normalization
    res[0] /= 2

    amplitudes = np.abs(res)
    phases = np.angle(res)
    max_amplitude = max(amplitudes[1:])
    amplitude = dict()
    phase = dict()

    for harmonic in range(len(amplitudes)):
        if harmonic > 0 and amplitudes[harmonic] > 0.01*max_amplitude:
            amplitude[harmonic] = amplitudes[harmonic]
            phase[harmonic] = phases[harmonic]

    # harmonics = list(range(len(res)))
    # amplitude = dict(zip(harmonics, np.abs(res)))
    # phase = dict(zip(harmonics, np.angle(res)))
    return amplitude, phase


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return rho, phi


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


def partition(array, begin, end):
    pivot = begin
    for i in range(begin+1, end+1):
        if array[i] <= array[begin]:
            pivot += 1
            array[i], array[pivot] = array[pivot], array[i]
    array[pivot], array[begin] = array[begin], array[pivot]
    return pivot


def quicksort(array):
    end = len(array) - 1

    def _quicksort(_array, _begin, _end):
        if _begin >= _end:
            return
        pivot = partition(_array, _begin, _end)
        _quicksort(_array, _begin, pivot-1)
        _quicksort(_array, pivot+1, _end)
    _quicksort(array, 0, end)
    return array


def dist(p, q):
    """Return the Euclidean distance between points p and q.
    :param p: [x, y]
    :param q: [x, y]
    :return: distance (float)"""
    return math.hypot(p[0] - q[0], p[1] - q[1])


def sparse_subset(points, r):
    """Returns a maximal list of elements of points such that no pairs of
    points in the result have distance less than r.
    :param points: list of tuples (x,y)
    :param r: distance
    :return: corresponding subset (list), indices of the subset (list)"""
    result = []
    indices = []
    for i, p in enumerate(points):
        if all(dist(p, q) >= r for q in result):
            result.append(p)
            indices.append(i)
    return result, indices


def integrate(x, y):
    """
    Performs Integral(x[0] to x[-1]) of y dx

    :param x: x axis coordinates (list)
    :param y: y axis coordinates (list)
    :return: integral value
    """
    integral = 0
    for i in range(1, len(x)):
        dx = x[i]-x[i-1]
        integral += dx*(y[i] + y[i-1])/2
    return integral


def my_fourier(x, y, n, L):
    """
    Fourier analys

    :param x: x axis coordinates
    :param y: y axis coordinates
    :param n: number of considered harmonic
    :param L: half-period length
    :return: a and b coefficients (y = a*cos(x) + b*sin(y))
    """
    y_to_integrate_a = [None]*len(y)
    y_to_integrate_b = [None]*len(y)

    for i in range(len(y)):
        y_to_integrate_a[i] = y[i] * np.cos(n*np.pi*x[i] / L)
        y_to_integrate_b[i] = y[i] * np.sin(n*np.pi*x[i] / L)

    a_n = 1/L * integrate(x, y_to_integrate_a)
    b_n = 1/L * integrate(x, y_to_integrate_b)
    return a_n, b_n


def get_ellipse_axes(a, b, dphi):
    """Trouve les longueurs des axes majeurs et mineurs de l'ellipse, ainsi que l'orientation de l'ellipse.
    ellipse: x(t) = A*cos(t), y(t) = B*cos(t+dphi)
    Etapes: longueur demi ellipse CENTRéE = sqrt(a^2 cos^2(x) + b^2 cos^2(t+phi)
    Minimisation de cette formule => obtention formule tg(2x) = alpha/beta"""
    assert a >= 0, 'a must be positive'
    assert b >= 0, 'b must be positive'

    if np.isclose(dphi, 0):  # Line
        if a == 0:
            phase = np.pi/2
        else:
            phase = np.arctan(b/a)
        return np.sqrt(a**2 + b**2), 0.0, phase
    elif np.isclose(dphi, np.pi/2):  # Properly oriented ellipse
        if a > b:
            return a, b, 0.0
        return b, a, np.pi/2
    sdphi = np.sin(dphi)
    cdphi = np.cos(dphi)
    alpha = (a**2)/2 + (b**2)/2*(cdphi**2 - sdphi**2)
    beta = -b**2*(sdphi*cdphi)
    t_optim_1, t_optim_2 = 0.5*(np.arctan(beta/alpha) + np.pi), 0.5*(np.arctan(beta/alpha) + 2*np.pi)
    max_length = np.sqrt((a * np.cos(t_optim_1))**2 + (b * np.cos(t_optim_1 + dphi))**2)
    min_length = np.sqrt((a * np.cos(t_optim_2))**2 + (b * np.cos(t_optim_2 + dphi))**2)
    # print(np.cos(t_optim_1 + dphi)/np.cos(t_optim_1), np.cos(t_optim_2 + dphi)/np.cos(t_optim_2))
    if max_length > min_length:
        phase = np.arctan(b/a * np.cos(t_optim_1 + dphi)/np.cos(t_optim_1))
    else:
        phase = np.arctan(b/a * np.cos(t_optim_2 + dphi)/np.cos(t_optim_2))
        max_length, min_length = min_length, max_length

    return max_length, min_length, phase


def convert_color(color):
    """
    Convert a color to a tuple if color is a char, otherwise return the tuple.

    :param color: (r,g,b) or char.
    :return:
    """
    try:
        colors = {"b": (0, 0, 255), "r": (255, 0, 0), "g": (0, 255, 0), "y": (255, 255, 0), "c": (0, 255, 255), "k": (0, 0, 0), "w": (255, 255, 255), "m": (255, 0, 255), "o": (255, 120, 0)}
        return colors[color]
    except KeyError:
        if type(color) == list or type(color) == tuple:
            return color[0], color[1], color[2]
        printIfShown("Unknown color {}, returning blue".format(color), SHOW_WARNING)
        return 0, 0, 255


def convert_color_with_alpha(color, alpha=255):
    """
    Same as meth:`convert_color` but with transparency
    """
    r, g, b = convert_color(color)
    return r, g, b, alpha

