import os
from qtpy.uic import loadUi
from maverick import ui
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

root = os.path.dirname(os.path.realpath(__file__))
refresh_image = os.path.join(root, "icons/refresh.png")
settings_image = os.path.join(root, "icons/plotSettings.png")
combine_image = os.path.join(root, "icons/combine.png")
bin_image = os.path.join(root, "icons/bin.png")
auto_image = os.path.join(root, "icons/auto.png")
manual_image = os.path.join(root, "icons/manual.png")
more_infos_image = os.path.join(root, "icons/more_infos.png")
stats_table_image = os.path.join(root, "icons/stats_table.png")
stats_plot_image = os.path.join(root, "icons/stats_plot.png")

ANGSTROMS = u"\u212B"
LAMBDA = u"\u03BB"
MICRO = u"\u00B5"
SUB_0 = u"\u2080"
DELTA = u"\u0394"


def load_ui(ui_filename, baseinstance):
    ui_filename = os.path.split(ui_filename)[-1]
    ui_path = os.path.dirname(ui.__file__)

    # get the location of the ui directory
    # this function assumes that all ui files are there
    filename = os.path.join(ui_path, ui_filename)

    return loadUi(filename, baseinstance=baseinstance)
