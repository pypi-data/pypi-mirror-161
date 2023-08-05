from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QHBoxLayout, QRadioButton
from qtpy.QtWidgets import QSpacerItem, QSizePolicy, QWidget
from qtpy.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from .utilities.table_handler import TableHandler
from .utilities.matplotlibview import MatplotlibView
from . import MICRO, LAMBDA, ANGSTROMS, DELTA
from . import combine_image, bin_image, auto_image, manual_image, settings_image, more_infos_image
from . import stats_table_image, stats_plot_image


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.pyqtgraph_combine()
        self.pyqtgraph_bin()
        self.plot_widgets()
        self.statusbar()
        self.splitter()
        self.table()
        self.labels()
        self.tab()
        self.combobox()
        self.widgets()

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

    def splitter(self):
        self.parent.ui.combine_horizontal_splitter.setSizes([200, 500])
        self.parent.ui.bin_horizontal_splitter.setSizes([300, 800])
        self.parent.ui.bin_vertical_splitter.setSizes([500, 50])

    def combobox(self):
        list_of_options = ['mean', 'median', 'std', 'min', 'max']
        self.parent.ui.bin_stats_comboBox.addItems(list_of_options)

    def table(self):
        # combine table
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        column_sizes = [50, 50, 500]
        o_table.set_column_sizes(column_sizes=column_sizes)

        # bin auto table
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        column_sizes = [40, 35, 60, 115, 115]
        o_table.set_column_sizes(column_sizes=column_sizes)
        column_names = ['use?',
                        'bin #',
                        'file #',
                        'tof range (' + MICRO + "s)",
                        LAMBDA + " range (" + ANGSTROMS + ")"]
        o_table.set_column_names(column_names=column_names)

        # bin manual table
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        column_sizes = [35, 80, 130, 130]
        o_table.set_column_sizes(column_sizes=column_sizes)
        column_names = column_names[1:]
        o_table.set_column_names(column_names=column_names)

        # statistics
        o_table = TableHandler(table_ui=self.parent.ui.statistics_tableWidget)
        column_names = ['bin #',
                        'file #',
                        'tof range (' + MICRO + "s)",
                        LAMBDA + " range (" + ANGSTROMS + ")",
                        'mean',
                        'median',
                        'std',
                        'min',
                        'max',
                        ]
        o_table.set_column_names(column_names=column_names)
        column_sizes = [35, 80, 130, 130, 130, 130, 130, 130, 130]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def labels(self):
        # combine tab
        self.parent.ui.combine_detector_offset_units.setText(MICRO + "s")
        self.parent.ui.bin_tof_radioButton.setText("TOF (" + MICRO + "s)")
        self.parent.ui.bin_lambda_radioButton.setText(LAMBDA + " (" + ANGSTROMS + ")")
        # bin tab
        self.parent.ui.bin_auto_log_file_index_radioButton.setText(DELTA + "file_index/file_index")
        self.parent.ui.bin_auto_log_tof_radioButton.setText(DELTA + "tof")
        self.parent.ui.bin_auto_log_lambda_radioButton.setText(DELTA + LAMBDA + "/" + LAMBDA)

        self.parent.ui.auto_linear_file_index_radioButton.setText(DELTA + " file index")
        self.parent.ui.auto_linear_tof_radioButton.setText(DELTA + " tof")
        self.parent.ui.auto_linear_lambda_radioButton.setText(DELTA + LAMBDA)
        self.parent.ui.bin_auto_linear_tof_units_label.setText(MICRO + 's')
        self.parent.ui.bin_auto_linear_lambda_units_label.setText(ANGSTROMS)

    def tab(self):
        self.parent.ui.combine_bin_tabWidget.setTabIcon(0, QIcon(combine_image))
        self.parent.ui.combine_bin_tabWidget.setTabIcon(1, QIcon(bin_image))
        self.parent.ui.bin_tabWidget.setTabIcon(0, QIcon(auto_image))
        self.parent.ui.bin_tabWidget.setTabIcon(1, QIcon(manual_image))
        self.parent.ui.combine_bottom_tabWidget.setTabIcon(2, QIcon(settings_image))
        self.parent.ui.stats_tabWidget.setTabIcon(0, QIcon(stats_table_image))
        self.parent.ui.stats_tabWidget.setTabIcon(1, QIcon(stats_plot_image))
        self.parent.ui.combine_bin_tabWidget.setTabEnabled(1, False)

    def plot_widgets(self):
        graphics_view_layout = QVBoxLayout()
        statistics_plot = MatplotlibView(self.parent)
        graphics_view_layout.addWidget(statistics_plot)
        self.parent.ui.statistics_plot_widget.setLayout(graphics_view_layout)
        self.parent.statistics_plot = statistics_plot

    def pyqtgraph_bin(self):
        bin_view = pg.PlotWidget(title="")
        bin_view.plot()
        self.parent.bin_profile_view = bin_view
        layout = QVBoxLayout()
        layout.addWidget(bin_view)
        self.parent.ui.bin_widget.setLayout(layout)

    def pyqtgraph_combine(self):
        area = DockArea()
        self.parent.ui.area = area
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("ROI profile", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        # preview - top widget
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.combine_image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_combine_image_preview)
        d1.addWidget(image_view)

        # plot and x-axis radio buttons - bottom widgets
        profile = pg.PlotWidget(title="")
        profile.plot()
        self.parent.combine_profile_view = profile
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(profile)
        # xaxis radio buttons
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        file_index_radio_button = QRadioButton("File Index")
        file_index_radio_button.setChecked(True)
        self.parent.combine_file_index_radio_button = file_index_radio_button
        self.parent.combine_file_index_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        tof_radio_button = QRadioButton("TOF (" + MICRO + "s)")
        self.parent.tof_radio_button = tof_radio_button
        self.parent.tof_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        lambda_radio_button = QRadioButton(LAMBDA + " (" + ANGSTROMS + ")")
        self.parent.lambda_radio_button = lambda_radio_button
        self.parent.lambda_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        axis_layout = QHBoxLayout()
        axis_layout.addItem(spacer_left)
        axis_layout.addWidget(file_index_radio_button)
        axis_layout.addWidget(tof_radio_button)
        axis_layout.addWidget(lambda_radio_button)
        axis_layout.addItem(spacer_right)
        bottom_widget = QWidget()
        bottom_widget.setLayout(axis_layout)
        bottom_layout.addWidget(bottom_widget)
        widget = QWidget()
        widget.setLayout(bottom_layout)
        d2.addWidget(widget)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(area)
        self.parent.ui.combine_widget.setLayout(vertical_layout)
        self.parent.ui.combine_widget.setEnabled(False)

    def widgets(self):
        self.parent.ui.visualize_auto_bins_axis_generated_pushButton.setIcon(QIcon(more_infos_image))
        self.parent.ui.visualize_auto_bins_axis_generated_pushButton.setToolTip("Display full original bin axis")
        self.parent.ui.bin_settings_pushButton.setIcon(QIcon(settings_image))
        self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(False)
