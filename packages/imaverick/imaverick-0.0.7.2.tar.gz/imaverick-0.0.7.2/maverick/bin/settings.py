from qtpy.QtWidgets import QDialog
import os

from .. import load_ui
from ..session import SessionKeys, CombineAlgorithm


class Settings(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui', 'ui_bin_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.initialization()

    def initialization(self):
        if self.parent.session[SessionKeys.bin_algorithm] == CombineAlgorithm.mean:
            self.ui.bin_mean_radioButton.setChecked(True)
        elif self.parent.session[SessionKeys.bin_algorithm] == CombineAlgorithm.median:
            self.ui.bin_median_radioButton.setChecked(True)
        else:
            raise NotImplementedError("radio button bin algo not implemented!")

    def bin_algorithm_changed(self):
        if self.ui.bin_mean_radioButton.isChecked():
            self.parent.session[SessionKeys.bin_algorithm] = CombineAlgorithm.mean
        elif self.ui.bin_median_radioButton.isChecked():
            self.parent.session[SessionKeys.bin_algorithm] = CombineAlgorithm.median
        else:
            raise NotImplementedError("bin algorithm not implemented!")

        self.parent.update_statistics()
