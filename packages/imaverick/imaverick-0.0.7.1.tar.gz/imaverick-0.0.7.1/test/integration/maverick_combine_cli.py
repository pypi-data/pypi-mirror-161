import subprocess


algorithm = 'median'
table_bin_file = '/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/log_bin_table.json'
output_folder = '/Users/j35/Desktop/test_maverick_cli'
input_folders = ['/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56306/',
                 '/Volumes/Buffalo/IPTS/IPTS-30023-Matteo-Simon/scan4/Run_56307/']
str_input_folders = " ".join(input_folders)

cmd = f"python -m maverick/maverick_combine_and_bin_cli.py -algorithm {algorithm} " \
      f"{table_bin_file} {output_folder} {str_input_folders}"
proc = subprocess.Popen(cmd,
                        shell=True,
                        stdin=subprocess.PIPE,
                        universal_newlines=True,
                        cwd=output_folder)
proc.communicate()
