import os

import numpy as np

from .graphs import Graphs, Graph, Data
from .graphs3 import SurfPlot, ContourPlot, FilledContourPlot, MeshPlot, ScatterPlot3, GridPlot_Generic
from .tools import indentParagraph

templates_tikz = os.path.join(os.path.dirname(__file__), 'templates_tikz')


def format_escape_char(theStr):
    theStr = theStr.replace("%", r"\%")
    theStr = theStr.replace("_", r"\_")
    return theStr


def convert_linestyle(linestyle):
    try:
        linestyles = {"-": '', "--": "dashed", "..": "dotted", ".": "dotted"}
        return linestyles[linestyle]
    except KeyError:
        return linestyle


def find_all_colors(theGraphs):
    all_colors = dict()
    correspondances = dict()
    for graphId in theGraphs.get_all_graphs_ids():
        correspondances[graphId] = dict()
        for traceId in theGraphs.get_graph(graphId).get_all_traces():
            try:
                r, g, b = theGraphs.get_graph(graphId).get_trace(traceId).get_color()
            except TypeError:
                r, g, b = 0, 0, 0
            key_format = "RGB{}_{}_{}".format(r, g, b)
            all_colors[key_format] = r"\definecolor{{{}}}{{RGB}}{{{},{},{}}}".format(key_format, r, g, b)
            correspondances[graphId][traceId] = key_format
    return all_colors, correspondances


def convert_marker(marker):
    try:
        markers = {"o": "*", "t1": "triangle", "t2": "triangle", "t3": "triangle", "t": "triangle", "s": "square", "d": "diamond", "p": "pentagon"}
        return markers[marker]
    except KeyError:
        return marker


def do_preamble():
    with open(os.path.join(templates_tikz, "preamble.tex"), "r") as f:
        return f.read()


def do_generate_figure():
    with open(os.path.join(templates_tikz, "generate_figure.tex"), "r") as f:
        return f.read()


def do_specific_axis_options(theGraph: Graph):
    """Get graph-specific axis options"""

    theStr = ''
    for key in theGraph.get_all_traces():
        xlabel = theGraph.get_trace(key).get_x_label()
        if xlabel:
            theStr += "xlabel={{ {} }},".format(format_escape_char(xlabel))
            break
    for key in theGraph.get_all_traces():
        ylabel = theGraph.get_trace(key).get_y_label()
        if ylabel:
            theStr += "ylabel={{ {} }},".format(format_escape_char(ylabel))
            break
    return theStr


def do_specific_trace_options(theTrace: Data, theColor):
    """Get latex trace options from Data"""
    linestyle = convert_linestyle(theTrace.get_linestyle())
    is_filled = theTrace.symbol_isfilled()
    markerstyle = convert_marker(theTrace.get_symbol())
    is_scattered = theTrace.isScattered
    outline = theTrace.get_symbolOutline()

    theStr = '\ncolor={},'.format(theColor)
    if is_scattered:
        theStr += "\nonly marks,"
    else:
        theStr += "{},".format(linestyle)
    theStr += '\nmark={},'.format(markerstyle)
    mark_options = '\nsolid, \nline width=0.1pt, \nmark size=1pt, \ndraw={}!{}!{},'.format(theColor, int(abs(outline - 2) * 100), "white" if outline < 1 else "black")
    if not is_filled:
        mark_options += "\nfill opacity=0,\n"
    theStr += "\nmark options={{{}}}".format(indentParagraph(mark_options, 1))
    return theStr


def export_to_tikz_groupGraphs(theGraphs: Graphs, foldername, additionalPreamble=lambda: '', additionalAxisOptions=lambda graphId: '', additionalTraceOptions=lambda graphId, traceId: '', debug=False):
    """
    Export the graphs as group

    :param theGraphs: Graphs to save
    :param foldername: Foldername to save
    :param additionalPreamble: method that returns string for custom tikz options
    :param additionalAxisOptions: method that returns string for custom tikz options
    :param additionalTraceOptions: method that returns string for custom tikz options
    :return:
    """
    all_colors, correspondance_colors = find_all_colors(theGraphs)

    if not debug:
        if not foldername:
            return
        os.makedirs(foldername, exist_ok=True)
        source_folder = os.path.join(foldername, "source")
        os.makedirs(source_folder, exist_ok=True)

    # Data file creation
    if not debug:
        for graphId in theGraphs.get_all_graphs_ids():
            theGraph = theGraphs.get_graph(graphId)
            for traceId in theGraph.get_all_traces():
                filename = os.path.join(source_folder, "g{}t{}.dat".format(graphId, traceId))
                theTrace = theGraph.get_trace(traceId)
                x, y = theTrace.get_plot_data()
                meta = theTrace.get_meta()
                if meta is not None:
                    with open(filename, "w") as f:
                        f.write("x\ty\tmeta\n")
                        for i in range(len(x)):
                            f.write("{}\t{}\t{}\n".format(x[i], y[i], meta[i]))
                else:
                    np.savetxt(filename, np.array([[x[i], y[i]] for i in range(len(x))]), header='x\ty')
                # add_body += "\\pgfplotstableread{{source/g{}t{}.dat}}{{\\g{}t{}}}\n".format(graphId, traceId, graphId, traceId)

    # Preamble
    theStr = ''
    theStr += do_preamble() + additionalPreamble()
    for color in all_colors.values():
        theStr += "% Colors\n{}\n".format(color)
    if not debug:
        with open(os.path.join(foldername, "preamble.tex"), "w") as f:
            f.write(theStr)
    else:
        print("PREAMBLE\n{}\n\n\n".format(theStr))
    # Generate picture creation
    theStr = ''
    theStr += do_generate_figure()
    if not debug:
        with open(os.path.join(foldername, "generate_figure.tex"), "w") as f:
            f.write(theStr)
    else:
        print("GENERATOR\n{}\n\n\n".format(theStr))

    # picture file creation
    theStr = ''
    theStr += indentParagraph("\\begin{tikzpicture}\n", 1)
    groupStyle = "group style={{group size=1 by {},}},".format(len(theGraphs.get_all_graphs_ids()))
    theStr += indentParagraph("\\begin{{groupplot}}[default_axis_style, {}]".format(groupStyle), 3)

    for graphId in theGraphs.get_all_graphs_ids():
        theGraph = theGraphs.get_graph(graphId)
        theStr += indentParagraph("\\nextgroupplot[{}]".format(do_specific_axis_options(theGraph) + additionalAxisOptions(graphId)), 5)
        for traceId in theGraph.get_all_traces():
            theTrace = theGraph.get_trace(traceId)
            filename = "source/g{}t{}.dat".format(graphId, traceId)
            theStr += indentParagraph("\\addplot[default_trace_style, {}] file {{\\relativepath {}}};\n".format(indentParagraph(do_specific_trace_options(theTrace, correspondance_colors[graphId][traceId]) + additionalTraceOptions(graphId, traceId), 3), filename), 7)
            if theTrace.get_legend():
                theStr += indentParagraph("\\addlegendentry{{{}}}".format(theTrace.get_legend()), 7)
    theStr += indentParagraph("\\end{groupplot}\n", 2)
    theStr += indentParagraph("\\end{tikzpicture}\n", 1)
    if not debug:
        with open(os.path.join(foldername, "figure.tex"), "w") as f:
            f.write(theStr)
    else:
        print("FIGURE\n{}\n\n\n".format(theStr))


""" Content from here is destined to 3D plots"""


def do_preamble3D():
    with open(os.path.join(templates_tikz, "preamble3D.tex"), "r") as f:
        return f.read()


def format_Griddata(X, Y, Z):
    theStr = ''
    for row in range(len(Z)):
        for col in range(len(Z[row])):
            theStr += "{}\t{}\t{}\n".format(X[col], Y[row], Z[row, col])
        theStr += "\n"
    return theStr


def format_scatterdata(x, y, z):
    theStr = ''
    for i in range(len(x)):
        theStr += "{}\t{}\t{}\n".format(x[i], y[i], z[i])
    return theStr


def export_to_tikz_contour_plot(list_of_traces3, foldername, filename_data="data"):
    """
    Export the graphs as group

    :param list_of_traces3: List of 3D traces
    :param foldername: Foldername to save
    :param filename_data: filename of the data
    :return:
    """
    if not foldername:
        return
    os.makedirs(foldername, exist_ok=True)
    source_folder = os.path.join(foldername, "source")
    os.makedirs(source_folder, exist_ok=True)

    # Data file creation
    for k, trace in enumerate(list_of_traces3):
        filename = os.path.join(source_folder, "{}_{}.dat".format(filename_data, k))
        with open(filename, 'w', encoding="utf-8") as f:
            if isinstance(trace, GridPlot_Generic):
                f.write(format_Griddata(*trace.get_plot_data()))
            else:
                f.write(format_scatterdata(*trace.get_plot_data()))

    # Preamble
    theStr = ''
    theStr += do_preamble3D()
    with open(os.path.join(foldername, "preamble.tex"), "w") as f:
        f.write(theStr)
    # Generate picture creation
    theStr = ''
    theStr += do_generate_figure()
    with open(os.path.join(foldername, "generate_figure.tex"), "w") as f:
        f.write(theStr)

    # picture file creation
    default_view = '{0}{90}' if any(map(lambda tr: isinstance(tr, ContourPlot) or isinstance(tr, FilledContourPlot), list_of_traces3)) else '{35}{55}'
    theStr = ''
    theStr += indentParagraph("\\begin{tikzpicture}\n", 1)
    theStr += indentParagraph("\\begin{{axis}}[default_axis_style, view = {}, grid on]\n".format(default_view), 2)
    for k, trace in enumerate(list_of_traces3):
        args = ''
        add_line = ''
        if isinstance(trace, SurfPlot):
            args = 'surf, line width = 0.1pt, unbounded coords=jump'
        elif isinstance(trace, MeshPlot):
            args = 'mesh, scatter, mark size = 1 pt, line width = 0.1pt, unbounded coords=jump'
        elif isinstance(trace, FilledContourPlot):
            levels = '{' + ','.join([str(lev) for lev in trace.get_levels()]) + '}'
            args = 'contour gnuplot = {{number={},labels={{true}}, levels={}, draw color=black, labels over line}}, unbounded coords=jump'.format(trace.get_number_of_contours(), levels)
            add_line = '\\addplot3[surf, shader=interp, unbounded coords=jump] file {{\\relativepath {}}};\n'.format("source/{}_{}.dat".format(filename_data, k))
        elif isinstance(trace, ContourPlot):
            levels = '{' + ','.join([str(lev) for lev in trace.get_levels()]) + '}'
            args = 'contour gnuplot = {{number={},labels={{true}}, levels={}}}, unbounded coords=jump'.format(trace.get_number_of_contours(), levels)
        elif isinstance(trace, ScatterPlot3):
            args = 'scatter, only marks, mark size=1.5pt, scatter/use mapped color={fill=mapped color, draw=black}, unbounded coords=jump'
        theStr += indentParagraph("{}\n".format(add_line), 3)
        theStr += indentParagraph("\\addplot3[{}] file {{\\relativepath {}}};\n".format(args, "source/{}_{}.dat".format(filename_data, k)), 3)
    theStr += indentParagraph("\\end{axis}\n", 2)
    theStr += indentParagraph("\\end{tikzpicture}\n", 1)
    with open(os.path.join(foldername, "figure.tex"), "w") as f:
        f.write(theStr)
