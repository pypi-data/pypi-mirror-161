import pytest

from maverick.combine_bin_cli import CombineCLI


class TestMaverickCombineCLI:

    def test_wrong_number_of_files(self):
        algorithm = 'median'
        output_folder = '/Users/j35/Desktop/test_maverick_cli'
        input_folders = ['/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56305/',
                         '/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56307/']
        str_input_folders = " ".join(input_folders)

        with pytest.raises(ValueError) as exc:
            CombineCLI(list_of_folders=input_folders)

    def test_not_enough_folders(self):
        algorithm = 'median'
        output_folder = '/Users/j35/Desktop/test_maverick_cli'

        # only 1 folder
        input_folders = ['/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56305/']
        str_input_folders = " ".join(input_folders)

        with pytest.raises(ValueError) as exc:
            CombineCLI(list_of_folders=input_folders)

        # 0 folder given
        with pytest.raises(ValueError) as exc:
            CombineCLI(list_of_folders=[])
