from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import copy

from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..combine.event_handler import EventHandler as CombineEventHandler

from . import SessionKeys
from . import session as default_session
from ..utilities.get import Get
from ..utilities import CombineAlgorithm, BinMode


class SessionHandler:

    logger = None   # customized logging for maverick

    config_file_name = ""
    load_successful = True

    session = None

    def __init__(self, parent=None):
        self.logger = logging.getLogger("maverick")
        self.logger.info("-> Saving current session before leaving the application")
        self.parent = parent

    def save_from_ui(self):
        pass

    def load_to_ui(self):
        if not self.load_successful:
            return

        self.logger.info(f"Automatic loading of session")
        session = copy.deepcopy(self.parent.session)
        self.logger.info(f"session -> {session}")

        # combine
        self.parent.ui.top_folder_label.setText(session[SessionKeys.top_folder])
        self.parent.ui.distance_source_detector_doubleSpinBox.setValue(session[SessionKeys.distance_source_detector])
        self.parent.ui.detector_offset_spinBox.setValue(session[SessionKeys.detector_offset])
        self.parent.ui.combine_sample_position_doubleSpinBox.setValue(session[SessionKeys.sample_position])
        o_combine_event = CombineEventHandler(parent=self.parent)
        o_combine_event.reset_data()
        self.parent.session = session
        o_combine_event.populate_list_of_folders_to_combine()
        o_combine_event.update_list_of_folders_to_use()

        combine_algorithm = session.get(SessionKeys.combine_algorithm, CombineAlgorithm.mean)
        if combine_algorithm == CombineAlgorithm.mean:
            self.parent.ui.combine_mean_radioButton.setChecked(True)
        elif combine_algorithm == CombineAlgorithm.median:
            self.parent.ui.combine_median_radioButton.setChecked(True)
        else:
            raise NotImplementedError("Combine method not implemented!")

        if not (SessionKeys.combine_roi in session.keys()):
            self.parent.session[SessionKeys.combine_roi] = default_session[SessionKeys.combine_roi]

        o_combine_event.combine_folders()
        o_combine_event.display_profile()

        bin_mode = session.get(SessionKeys.bin_mode, BinMode.auto)
        if bin_mode == BinMode.auto:
            self.parent.bin_tabWidget.setCurrentIndex(0)
        elif bin_mode == BinMode.manual:
            self.parent.bin_tabWidget.setCurrentIndex(1)
        else:
            raise NotImplementedError("Auto bin mode not implemented!")

        bin_algorithm = session.get(SessionKeys.bin_algorithm, CombineAlgorithm.mean)
        self.parent.session[SessionKeys.bin_algorithm] = bin_algorithm

    def automatic_save(self):
        self.logger.info(self.parent.session)
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)

    def save_to_file(self, config_file_name=None):
        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                           caption="Select session file name ...",
                                                           directory=self.parent.session[SessionKeys.top_folder],
                                                           filter="session (*.json)",
                                                           initialFilter="session")

            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            output_file_name = config_file_name
            session = self.parent.session

            with open(output_file_name, 'w') as json_file:
                json.dump(session, json_file)

            show_status_message(parent=self.parent,
                                message=f"Session saved in {config_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
            self.logger.info(f"Saving configuration into {config_file_name}")

    def load_from_file(self, config_file_name=None):
        if config_file_name is None:
            config_file_name = QFileDialog.getOpenFileName(self.parent,
                                                           directory=self.parent.session[SessionKeys.top_folder],
                                                           caption="Select session file ...",
                                                           filter="session (*.json)",
                                                           initialFilter="session")
            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            config_file_name = config_file_name
            self.config_file_name = config_file_name
            show_status_message(parent=self.parent,
                                message=f"Loading {config_file_name} ...",
                                status=StatusMessageStatus.ready)

            with open(config_file_name, "r") as read_file:
                session = json.load(read_file)
                o_get = Get(parent=self.parent)
                maverick_current_version = o_get.version()
                if session[SessionKeys.version] == maverick_current_version:
                    self.parent.session = session
                    self.load_to_ui()
                    self.logger.info(f"Loaded from {config_file_name}")
                    self.load_successful = True
                else:
                    self.logger.info(f"Session file is out of date!")
                    self.logger.info(f"-> expected version: {maverick_current_version}")
                    self.logger.info(f"-> session version: {session[SessionKeys.version]}")
                    self.load_successful = False

                if not self.load_successful:
                    show_status_message(parent=self.parent,
                                        message=f"{config_file_name} not loaded! (check log for more information)",
                                        status=StatusMessageStatus.ready,
                                        duration_s=10)

                else:
                    self.logger.info(f"Loading {config_file_name} ... Done!")
                    show_status_message(parent=self.parent,
                                        message=f"Loaded {config_file_name} ... Done!",
                                        status=StatusMessageStatus.ready,
                                        duration_s=10)

        else:
            self.load_successful = False
            show_status_message(parent=self.parent,
                                message=f"{config_file_name} not loaded! (check log for more information)",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
