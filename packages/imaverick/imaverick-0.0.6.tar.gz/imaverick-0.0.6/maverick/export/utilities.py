from pathlib import Path
from ..bin import TO_ANGSTROMS_UNITS, TO_MICROS_UNITS


def create_bin_tab_output_file_name(folder=None,
                                    bin_name=None):
    bin_name += "_bin_table.json"
    full_file_name = Path(folder) / bin_name
    return full_file_name


def create_output_file_name(folder=None,
                            bin_index=0,
                            sample_position=0,
                            list_file_index=None,
                            list_tof=None,
                            list_lambda=None):

    sample_position = str(sample_position).replace(".", "_")
    bin_index = f"{bin_index:02d}"

    if len(list_file_index) == 1:
        str_file = f"file_#{list_file_index[0]}"

        str_tof_value = convert_to_user_friendly_micros_units(list_tof[0])
        str_tof = f"tof_{str_tof_value}_micros"

        str_lambda_value = convert_to_user_friendly_angstroms_units(list_lambda[0])
        str_lambda = f"lambda_{str_lambda_value}_angstroms"

    elif len(list_file_index) == 2:
        str_file = f"file_{list_file_index[0]}_#{list_file_index[1]}"

        from_str_tof_value = convert_to_user_friendly_micros_units(list_tof[0])
        to_str_tof_value = convert_to_user_friendly_micros_units(list_tof[1])
        str_tof = f"from_tof_{from_str_tof_value}_to_{to_str_tof_value}_micros"

        from_str_lambda_value = convert_to_user_friendly_angstroms_units(list_lambda[0])
        to_str_lambda_value = convert_to_user_friendly_angstroms_units(list_lambda[1])
        str_lambda = f"from_lambda_{from_str_lambda_value}_to_{to_str_lambda_value}_angstroms"

    else:
        str_file = f"from_file_#{list_file_index[0]}_to_file_#{list_file_index[-1]}"

        from_str_tof_value = convert_to_user_friendly_micros_units(list_tof[0])
        to_str_tof_value = convert_to_user_friendly_micros_units(list_tof[-1])
        str_tof = f"from_tof_{from_str_tof_value}_to_{to_str_tof_value}_micros"

        from_str_lambda_value = convert_to_user_friendly_angstroms_units(list_lambda[0])
        to_str_lambda_value = convert_to_user_friendly_angstroms_units(list_lambda[-1])
        str_lambda = f"from_lambda_{from_str_lambda_value}_to_{to_str_lambda_value}_angstroms"

    str_bin = f"bin#_{bin_index}"
    str_sample_position = f"sample_position_{sample_position}_mm"

    file_name = f"image_{str_bin}_{str_sample_position}_{str_file}_{str_tof}_{str_lambda}.tiff"

    full_file_name = Path(folder) / file_name

    return full_file_name


def convert_to_user_friendly_angstroms_units(value):
    angstroms_str = f"{value * TO_ANGSTROMS_UNITS:.2f}"
    new_angstroms_str = angstroms_str.replace(".", "_")
    return new_angstroms_str


def convert_to_user_friendly_micros_units(value):
    tof_str = f"{value * TO_MICROS_UNITS:.2f}"
    new_tof_str = tof_str.replace(".", "_")
    return new_tof_str
