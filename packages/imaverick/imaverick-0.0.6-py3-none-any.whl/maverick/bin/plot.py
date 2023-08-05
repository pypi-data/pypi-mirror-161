import copy

from ..utilities.get import Get
from ..utilities import TimeSpectraKeys

from . import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from .. import LAMBDA, MICRO, ANGSTROMS


class Plot:

    def __init__(self, parent=None):
        self.parent = parent

    def refresh_profile_plot(self):
        """
        this clear, remove all bin items and just replot the profile on the bin right imageView
        """

        self.parent.bin_profile_view.clear()  # clear previous plot
        if not (self.parent.dict_of_bins_item is None):  # remove previous bins
            for _key in self.parent.dict_of_bins_item.keys():
                self.parent.bin_profile_view.removeItem(self.parent.dict_of_bins_item[_key])

        profile_signal = self.parent.profile_signal

        o_get = Get(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        time_spectra_x_axis_name = o_get.bin_x_axis_selected()

        x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            x_axis_label = "file index"
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            x_axis *= TO_MICROS_UNITS    # to display axis in micros
            x_axis_label = "tof (" + MICRO + "s)"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis *= TO_ANGSTROMS_UNITS    # to display axis in Angstroms
            x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"

        self.parent.bin_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        self.parent.bin_profile_view.setLabel("left", f"{combine_algorithm} counts")
        self.parent.bin_profile_view.setLabel("bottom", x_axis_label)
