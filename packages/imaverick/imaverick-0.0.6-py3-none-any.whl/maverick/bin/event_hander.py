import logging

from ..session import SessionKeys
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys, BinAutoMode, BinMode
from .manual_event_handler import ManualEventHandler
from .auto_event_handler import AutoEventHandler

FILE_INDEX_BIN_MARGIN = 0.5

UNSELECTED_BIN = (0, 0, 200, 50)
SELECTED_BIN = (0, 200, 0, 50)


class EventHandler:

    tof_bin_margin = 0
    lambda_bin_margin = 0

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

        self.tof_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.tof_array][1] -
                               self.parent.time_spectra[TimeSpectraKeys.tof_array][0]) / 2.

        self.lambda_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.lambda_array][1] -
                                  self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]) / 2

    def entering_tab(self):
        o_get = Get(parent=self.parent)
        if o_get.bin_mode() == BinMode.auto:
            o_auto_event = AutoEventHandler(parent=self.parent)
            if o_get.bin_auto_mode() == BinAutoMode.linear:
                o_auto_event.auto_linear_radioButton_changed()
            elif o_get.bin_auto_mode() == BinAutoMode.log:
                o_auto_event.auto_log_radioButton_changed()
            o_auto_event.refresh_auto_tab()

        elif o_get.bin_mode() == BinMode.manual:
            o_manual_event = ManualEventHandler(parent=self.parent)
            o_manual_event.refresh_manual_tab()
            o_manual_event.display_all_items()

        else:
            pass

    def bin_auto_manual_tab_changed(self, new_tab_index=0):
        if new_tab_index == 0:
            self.parent.session[SessionKeys.bin_mode] = BinMode.auto

        elif new_tab_index == 1:
            self.parent.session[SessionKeys.bin_mode] = BinMode.manual

        elif new_tab_index == 2:
            pass

        else:
            raise NotImplementedError("LinearBin mode not implemented!")

        self.entering_tab()

    def bin_axis_changed(self):
        o_get = Get(parent=self.parent)
        if o_get.bin_mode() == BinMode.auto:
            o_event = AutoEventHandler(parent=self.parent)
            o_event.refresh_auto_tab()
        else:
            o_event = ManualEventHandler(parent=self.parent)
            o_event.refresh_manual_tab()
