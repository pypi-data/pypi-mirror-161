from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import warnings

warnings.filterwarnings("ignore")

from .utilities.get import Get
from .utilities.config_handler import ConfigHandler
from .utilities import TimeSpectraKeys, BinAutoMode
from .utilities.time_spectra import TimeSpectraLauncher
from .event_hander import EventHandler
from .session import session
from .session.session_handler import SessionHandler
from .session import SessionKeys
from .initialization import Initialization
from .utilities.check import Check
from .combine.event_handler import EventHandler as CombineEventHandler
from .bin.event_hander import EventHandler as BinEventHandler
from .bin.manual_event_handler import ManualEventHandler as BinManualEventHandler
from .bin.auto_event_handler import AutoEventHandler as BinAutoEventHandler
from .bin.preview_full_bin_axis import PreviewFullBinAxis
from .bin.statistics import Statistics
from .bin.settings import Settings as BinSettings
from .bin.manual_right_click import ManualRightClick
from maverick.export.export_images import ExportImages
from maverick.export.export_bin_table import ExportBinTable
from .log.log_launcher import LogLauncher

from . import load_ui


class MainWindow(QMainWindow):
    session = session  # dictionary that will keep record of the entire UI and used to load and save the session
    log_id = None  # ui id of the log QDialog
    version = None   # current version of application

    # raw_data_folders = {'full_path_to_folder1': {'data': [image1, image2, image3...],
    #                                              'list_files': [file1, file2, file3,...],
    #                                              'nbr_files': 0,
    #                                              },
    #                     'full_path_to_folder2': {'data': [image1, image2, image3...],
    #                                              'list_files': [file1, file2, file3,...],
    #                                              'nbr_files': 0,
    #                                              },
    #                     ....
    #                    }
    raw_data_folders = None  # dictionary of data for each of the folders

    # combine_data = [image1, image2, image3...]
    combine_data = None

    # time spectra file and arrays
    time_spectra = {TimeSpectraKeys.file_name: None,
                    TimeSpectraKeys.tof_array: None,
                    TimeSpectraKeys.lambda_array: None,
                    TimeSpectraKeys.file_index_array: None}

    linear_bins = {TimeSpectraKeys.tof_array: None,
                   TimeSpectraKeys.file_index_array: None,
                   TimeSpectraKeys.lambda_array: None}

    log_bins = {TimeSpectraKeys.tof_array: None,
                TimeSpectraKeys.file_index_array: None,
                TimeSpectraKeys.lambda_array: None}

    # each will be a dictionaries of ranges
    # ex: TimeSpectraKeys.tof_array = {0: [1],
    #                                  1: [2,6],
    #                                  3: [7,8,9,10], ...}
    manual_bins = {TimeSpectraKeys.tof_array: None,
                   TimeSpectraKeys.file_index_array: None,
                   TimeSpectraKeys.lambda_array: None}

    # dictionary that will record the range for each bin
    # {0: [0, 3], 1: [1, 10], ...}
    manual_snapping_indexes_bins = None

    # list of rows selected by each of the linear and log bins
    linear_bins_selected = None
    log_bins_selected = None

    # use to preview the full axis
    # ex: [1,2,3,4,5,6,7] or [0.1, 0.2, 0.4, 0.8, 1.6....]
    full_bin_axis_requested = None

    # profile signal (displayed on the top right of combine and bin tab)
    # 1D array
    profile_signal = None

    # pyqtgraph view
    combine_image_view = None  # combine image view id - top right plot
    combine_profile_view = None  # combine profile plot view id - bottom right plot
    bin_profile_view = None  # bin profile
    combine_roi_item_id = None  # pyqtgraph item id of the roi (combine tab)
    combine_file_index_radio_button = None  # in combine view
    tof_radio_button = None  # in combine view
    lambda_radio_button = None  # in combine view
    live_combine_image = None  # live combine image used by ROI

    # matplotlib plot
    statistics_plot = None  # matplotlib plot

    # dictionary of all the bins pg item
    # {0: pg.regionitem1,
    #  2: pg.regionitem2,
    #  ...
    # }
    dict_of_bins_item = None

    # list of manual bins.
    # using a list because any of the bin can be removed by the user
    list_of_manual_bins_item = []

    current_auto_bin_rows_highlighted = []

    # stats currently displayed in the bin stats table
    # {StatisticsName.mean: {Statistics.full: [],
    #                        Statistics.roi: [],
    #                        },
    # StatisticsName.median: ....
    #  }
    current_stats = None

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        super(MainWindow, self).__init__(parent)
        self.ui = load_ui('mainWindow.ui', baseinstance=self)
        self.initialization()
        self.setup()
        self.setWindowTitle(f"maverick - v{self.version}")

    def initialization(self):
        o_init = Initialization(parent=self)
        o_init.all()

    def setup(self):
        """
        This is taking care of
            - initializing the session dict
            - setting up the logging
            - retrieving the config file
            - loading or not the previous session
        """
        o_config = ConfigHandler(parent=self)
        o_config.load()

        current_folder = None
        if self.config['debugging']:
            list_homepath = self.config['homepath']
            for _path in list_homepath:
                if os.path.exists(_path):
                    current_folder = _path
            if current_folder is None:
                current_folder = os.path.expanduser('~')
        else:
            current_folder = os.path.expanduser('~')
        self.session[SessionKeys.top_folder] = current_folder

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        version = Get.version()
        self.version = version
        self.log_file_name = log_file_name
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logger = logging.getLogger("maverick")
        logger.info("*** Starting a new session ***")
        logger.info(f" Version: {version}")

        o_event = EventHandler(parent=self)
        o_event.automatically_load_previous_session()

    # Menu
    def session_load_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()

    def session_save_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def help_log_clicked(self):
        LogLauncher(parent=self)

    # combine events
    def check_combine_widgets(self):
        o_event = CombineEventHandler(parent=self)
        o_event.check_widgets()

    def combine_bin_tab_changed(self, new_tab_index):
        if new_tab_index == 1:  # bin
            o_event = BinEventHandler(parent=self)
            o_event.entering_tab()
            self.update_statistics()

    def select_top_folder_button_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.select_top_folder()

    def refresh_table_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.refresh_table_clicked()

    def radio_buttons_of_folder_changed(self):
        self.ui.setEnabled(False)
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use()
        o_event.combine_folders()
        o_event.display_profile()
        o_event.check_widgets()
        self.ui.setEnabled(True)

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_algorithm_changed(self):
        o_get = Get(parent=self)
        list_working_folders = o_get.list_of_folders_to_use()
        if list_working_folders == []:
            return

        o_event = CombineEventHandler(parent=self)
        o_event.combine_algorithm_changed()
        o_event.display_profile()

    def combine_instrument_settings_changed(self):
        if self.combine_data is None:
            return
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use(force_recalculation_of_time_spectra=True)
        o_event.combine_folders()
        o_event.display_profile()

    def combine_xaxis_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.display_profile()

    def combine_roi_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.combine_roi_changed()
        o_event.display_profile()

    # bin events
    def bin_xaxis_changed(self):
        o_event = BinEventHandler(parent=self)
        o_event.bin_axis_changed()

    def bin_auto_manual_tab_changed(self, new_tab_index):
        o_event = BinEventHandler(parent=self)
        o_event.bin_auto_manual_tab_changed(new_tab_index)
        self.update_statistics()

    # - auto mode
    def bin_auto_log_linear_radioButton_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_radioButton_clicked()
        self.update_statistics()

    def bin_auto_log_file_index_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.file_index_array)
        self.update_statistics()

    def bin_auto_log_tof_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.tof_array)
        self.update_statistics()

    def bin_auto_log_lambda_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.lambda_array)
        self.update_statistics()

    def bin_auto_linear_file_index_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.file_index_array)
        self.update_statistics()

    def bin_auto_linear_tof_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.tof_array)
        self.update_statistics()

    def bin_auto_linear_lambda_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.lambda_array)
        self.update_statistics()

    def auto_log_radioButton_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.log)
        o_event.auto_log_radioButton_changed()
        self.update_statistics()

    def auto_linear_radioButton_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.auto_linear_radioButton_changed()
        self.update_statistics()

    def auto_table_use_checkbox_changed(self, state, row):
        o_event = BinAutoEventHandler(parent=self)
        state = True if state == 2 else False
        o_event.use_auto_bin_state_changed(row=row, state=state)
        self.bin_auto_table_selection_changed()
        self.update_statistics()

    def bin_auto_hide_empty_bins(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.update_auto_table()

    def bin_auto_visualize_axis_generated_button_clicked(self):
        o_preview = PreviewFullBinAxis(parent=self)
        o_preview.show()

    def bin_auto_table_right_clicked(self, position):
        o_event = BinAutoEventHandler(parent=self)
        o_event.auto_table_right_click(position=position)

    def bin_auto_table_selection_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.auto_table_selection_changed()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass

    # - manual mode
    def bin_manual_add_bin_clicked(self):
        o_event = BinManualEventHandler(parent=self)
        o_event.add_bin()
        self.update_statistics()

    def bin_manual_populate_table_with_auto_mode_bins_clicked(self):
        o_event = BinManualEventHandler(parent=self)
        o_event.clear_all_items()
        o_event.populate_table_with_auto_mode()
        self.update_statistics()

    def bin_manual_region_changed(self, item_id):
        o_event = BinManualEventHandler(parent=self)
        o_event.bin_manually_moved(item_id=item_id)
        self.update_statistics()

    def bin_manual_region_changing(self, item_id):
        o_event = BinManualEventHandler(parent=self)
        o_event.bin_manually_moving(item_id=item_id)

    def bin_manual_table_right_click(self, position):
        o_event = ManualRightClick(parent=self)
        o_event.manual_table_right_click()

    # - statistics
    def update_statistics(self):
        o_stat = Statistics(parent=self)
        o_stat.update()
        o_stat.plot_statistics()

    def bin_statistics_comboBox_changed(self):
        o_stat = Statistics(parent=self)
        o_stat.plot_statistics()

    def bin_settings_clicked(self):
        o_bin = BinSettings(parent=self)
        o_bin.show()

    # export images
    def export_combined_and_binned_images_clicked(self):
        o_export = ExportImages(parent=self)
        o_export.run()

    def bin_export_table_pushButton_clicked(self):
        o_export = ExportBinTable(parent=self)
        o_export.run()

    def closeEvent(self, event):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()

        o_event = Check(parent=self)
        o_event.log_file_size()

        logging.info(" #### Leaving maverick ####")
        self.close()


def main(args):
    app = QApplication(args)
    app.setStyle("Fusion")
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("maverick")
    # app.setWindowIcon(PyQt4.QtGui.QIcon(":/icon.png"))
    application = MainWindow()
    application.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
