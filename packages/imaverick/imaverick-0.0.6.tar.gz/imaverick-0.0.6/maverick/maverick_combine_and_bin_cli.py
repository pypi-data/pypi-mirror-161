import argparse
from tqdm import tqdm

from combine_bin_cli import CombineBinCLI


parser = argparse.ArgumentParser(description='''
Combine and bin a set of TOF folders,

Example:
    python maverick/maverick_combine_cli.py -algorithm mean log_table_bin.json ./ /folder1 /folder2 /folder3 
    python maverick/maverick_combine_cli.py log_table_bin.json ./ /folder1 /folder2 /folder3
    python maverick/maverick_combine_cli.py log_table_bin.json ./ /folder3 /folder2
''',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="NB: the list of input folders arguments must be last!")
parser.add_argument('-algorithm',
                    choices=["mean", "median"],
                    default="median",
                    help="Algorithm to use to combine the folders (default is median)")
parser.add_argument('bin_table_file_name',
                    help="file name of the table of bins created by the UI maverick")
parser.add_argument('export',
                    help="output folder where the combined data will be saved",
                    type=str)
parser.add_argument('folders',
                    help="list of folders to combine",
                    type=str,
                    nargs='+')
args = parser.parse_args()

# parsing arguments
algorithm = args.algorithm
bin_table_file_name = args.bin_table_file_name
export_folder = args.export
input_folders = args.folders

# load all the folders in memory
# combine using algorithm defined
# export all images into export folder using custom name
# move time stamp file from first folder to export folder using same custom name

# import time
# for i in tqdm(range(len(args.folders))):
#     time.sleep(1)

o_combine_bin = CombineBinCLI(list_of_folders=input_folders)
o_combine_bin.combine(algorithm)
o_combine_bin.bin(bin_table_file_name)
o_combine_bin.export(output_folder=export_folder)




## current command to run CLI and to test it using Buffalo
"""
python maverick/maverick_combine_and_bin_cli.py 
 /Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/log_bin_table.json 
 ~/Desktop/cli_output 
 /Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56306_light 
 /Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56307_light
"""