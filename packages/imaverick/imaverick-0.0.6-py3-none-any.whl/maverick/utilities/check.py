from ..log.log_launcher import LogHandler


class Check:

    def __init__(self, parent=None):
        self.parent = parent

    def log_file_size(self):
        o_handler = LogHandler(parent=self.parent,
                               log_file_name=self.parent.log_file_name)
        o_handler.cut_log_size_if_bigger_than_buffer()
