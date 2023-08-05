from ..utilities import BinMode, CombineAlgorithm


class SessionKeys:
    """list of all sessions keys, to easily retrieve them"""

    top_folder = "top_folder"
    list_working_folders = "list_working_folders"
    list_working_folders_status = "list_working_folders_status"
    log_buffer_size = "log_buffer_size"
    version = "version"
    distance_source_detector = 'distance_source_detector'
    detector_offset = 'detector_offset'
    combine_algorithm = 'combine_algorithm'
    combine_roi = 'combine_roi'
    sample_position = 'sample_position'
    bin_mode = 'bin_mode'
    bin_algorithm = 'bin_algorithm'


session = {SessionKeys.top_folder: None,  # the base folder to start looking at images folder to combine
           SessionKeys.list_working_folders: None,  # list of working folders
           SessionKeys.list_working_folders_status: None,  # list of working folders status [True, True, False..]
           SessionKeys.log_buffer_size: 500,   # max size of the log file
           SessionKeys.version: "0.0.1",   # version of that config
           SessionKeys.distance_source_detector: 19.855,
           SessionKeys.detector_offset: 9600,
           SessionKeys.combine_algorithm: CombineAlgorithm.mean,
           SessionKeys.combine_roi: [50, 50, 200, 200],  # [x0,y0,width,height],
           SessionKeys.sample_position: 0,    # in the combine tab
           SessionKeys.bin_mode: BinMode.auto,   # 'auto' or 'manual',
           SessionKeys.bin_algorithm: CombineAlgorithm.mean,  # 'mean' or 'median'
           }
