WKEY_GENERAL = "GENERAL"
WKEY_MIN = "Min"
WKEY_MAX = "Max"
WKEY_SERIES = "Series"
WKEY_FIGURE = "figures"
WKEY_MODEL = "models"
WKEY_ROUTE = "Route"
WKEY_POINT = "Point"
WKEY_MAP = "Map"
WKEY_CASE = "Case number"
WKEY_APPENDIX = "Appendix"
WKEY_DESCRIPTION = "Description"
WKEY_CASE_TITLE = "Case description"
WKEY_CASE_DESCRIPTION = "Extra description"
WKEY_PRJ_NUMBER = "Project number"
WKEY_CHAPTER = "Chapter"
WKEY_PIPES = "all pipes"
WKEY_TSTEP = "TSTEP"

# Define keys for excel parser
XLS_CASE = "Cases"
# Case keys
XLS_CASE_NAME = "Name"
XLS_CASE_NUMBER = "Number"
XLS_CASE_INCLUDE = "Include"
XLS_CASE_APPENDIX = "Appendix"
XLS_CASE_CHAPTER = "Chapter"
XLS_CASE_EXTRA = "Extra"
XLS_CASE_DESCRIPTION = "Description"
XLS_OUTPUT = "Output"
XLS_TPLOT = "Tplots"
XLS_RPLOT = "Rplots"
# Plot keys
XLS_PLOT_FIG = "fig"
XLS_PLOT_PLOT = "plot"
XLS_PLOT_NAME = "name"
XLS_PLOT_PROP = "property"
XLS_PLOT_TIMES = "times"
XLS_PLOT_TITLE = "title"
XLS_PLOT_LEGEND = "Legend"
XLS_PLOT_XLABEL = "Xlabel"
XLS_PLOT_YLABEL = "Ylabel"
XLS_PLOT_XMIN = "Xmin"
XLS_PLOT_YMIN = "Ymin"
XLS_PLOT_XMAX = "Xmax"
XLS_PLOT_YMAX = "Ymax"
XLS_PLOT_XSCALE = "Xscale"
XLS_PLOT_YSCALE = "Yscale"
XLS_PLOT_YTICK = "Ytick"
XLS_PLOT_XTICK = "Xtick"

# Route points
XLS_ROUTEPTS = "route_points"


import os

# Figure sizes
figtable = {"A4":[8.3, 11.7], "A3":[11.7, 16.5]}

# GLOBAL properties
ROOT_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
ROOT_EXAMPLE = os.path.join(ROOT_DIR, "example")
ROOT_DATA = os.path.join(ROOT_DIR, 'data')
ROOT_MODELS = os.path.join(ROOT_DATA, 'models')
ROOT_EXPORT = os.path.join(ROOT_DIR, 'export')
WBIN = "c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\"