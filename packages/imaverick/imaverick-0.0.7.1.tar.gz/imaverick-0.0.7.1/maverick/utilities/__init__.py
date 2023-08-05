class TimeSpectraKeys:

    tof_array = 'tof_array'
    lambda_array = 'lambda_array'
    file_index_array = 'file_index_array'
    file_name = 'file_name'
    counts_array = 'counts_array'


class CombineAlgorithm:
    """list of algorithm used to combine the folders"""

    mean = 'mean'
    median = 'median'


class BinMode:
    """list of mode to bin the data"""

    auto = 'auto'
    manual = 'manual'
    settings = 'settings'


class BinAutoMode:

    log = 'log'
    linear = 'linear'


class BinAlgorithm:
    """list of algorithm used to bin the images"""

    mean = 'mean'
    median = 'median'
