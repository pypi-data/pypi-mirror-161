import os
import logging

from .utilities.get import Get
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def automatically_load_previous_session(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self.parent)
            load_session_ui.show()
        else:
            o_session = SessionHandler(parent=self.parent)
            self.session = o_session.session
