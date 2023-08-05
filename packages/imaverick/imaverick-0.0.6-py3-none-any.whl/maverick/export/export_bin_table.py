from qtpy.QtWidgets import QFileDialog
import json
import logging

from ..utilities.get import Get
from ..session import SessionKeys
from .utilities import create_bin_tab_output_file_name
from ..utilities.status_message_config import StatusMessageStatus, show_status_message


class ExportBinTable:
    """
    this class will export as a json file the dictionary of bins (file_index, tof and lambda)
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):

        working_dir = self.parent.session[SessionKeys.top_folder]
        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to ExportImages the Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            self.logger.info("User cancel export bin table!")
            return

        o_get = Get(parent=self.parent)
        current_bin_name_activated = o_get.current_bins_name_activated()
        self.logger.info(f"{current_bin_name_activated} bins table will be exported to {_folder}!")

        current_bins = o_get.current_bins_activated()
        output_file_name = create_bin_tab_output_file_name(folder=_folder,
                                                           bin_name=current_bin_name_activated)

        with open(output_file_name, 'w') as json_file:
            json.dump(current_bins, json_file)

        show_status_message(parent=self.parent,
                            message=f"Exported bin table as {output_file_name} ... Done!",
                            status=StatusMessageStatus.ready,
                            duration_s=10)
        self.logger.info(f"Bin table {current_bin_name_activated} has been exported as {output_file_name}")
