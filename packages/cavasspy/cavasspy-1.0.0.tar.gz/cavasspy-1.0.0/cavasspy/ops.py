import os
import time
import uuid
from typing import Optional, Iterable

from hammer.io import load_mat, save_mat

# CAVASS build path, default in installation is ~/cavass-build
CAVASS_PROFILE_PATH = None


def setup():
    if CAVASS_PROFILE_PATH is not None:
        os.environ['PATH'] = f'{os.environ["PATH"]}:{os.path.expanduser(CAVASS_PROFILE_PATH)}'
        os.environ['VIEWNIX_ENV'] = os.path.expanduser(CAVASS_PROFILE_PATH)


def execute_cmd(cavass_cmd):
    setup()
    r = os.popen(cavass_cmd).readlines()
    if 'ERROR:' in r:
        print(f'Process failed {r} of command {cavass_cmd}')
    return r


def get_slice_numbers(input_file):
    """
    Get the start and the last slice index of the given CAVASS file.
    Note that the first slice starts from 0, while it starts from 1 in CAVASS software.
    """
    r = execute_cmd(f'get_slicenumber {input_file}')
    r = r[0]
    r = r.split(' ')
    return int(r[0]), int(r[1])


def get_ct_resolution(input_file):
    """
    Get (H,W,D) resolution of input_file.
    """
    r = execute_cmd(f'get_slicenumber {input_file} -s')
    r = r[2].split(' ')
    r = tuple(map(lambda x: int(x), r))
    return r


def load_cavass_file(input_file, first_slice=None, last_slice=None, sleep_time=1, ):
    """
    Load data of input_file.
    Use the assigned slice indices if both the first slice and the last slice are given.
    Args:
        sleep_time: set a sleep_time between saving and loading temp mat to avoid system IO error.
        first_slice: Loading from the first slice (included). Load from the inferior slice to the superior slice if first_slice is None.
        last_slice: Loading end at the last_slice (included). Load from the inferior slice to the superior slice if last_slice is None.
    """
    tmp_path = '/tmp/cavass'
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path, exist_ok=True)

    output_file = os.path.join(tmp_path, f'{uuid.uuid1()}.mat')
    if first_slice is None or last_slice is None:
        cvt2mat = f"exportMath {input_file} matlab {output_file} `get_slicenumber {input_file}`"
    else:
        cvt2mat = f"exportMath {input_file} matlab {output_file} {first_slice} {last_slice}"
    execute_cmd(cvt2mat)
    time.sleep(sleep_time)
    ct = load_mat(output_file)
    os.remove(output_file)
    return ct


def copy_pose(skew_file, good_file, output_file):
    execute_cmd(f"copy_pose {skew_file} {good_file} {output_file}")


def save_cavass_file(output_file, data, binary=False, size: Optional[Iterable] = None,
                     spacing: Optional[Iterable] = None,
                     reference_file=None):
    """
    Save data as CAVASS format. Do not provide spacing and reference_file at the same time.
    Recommend to use binary for mask files and reference_file to copy all properties.
    Args:
        binary: Save as binary data if True.
        size: Size for converting with dimensions of (H,W,D), default: the size of input data.
        spacing: Spacing for converted CAVASS file with dimensions of (H,W,D), default: 1mm.
        reference_file: Copy pose from the given file.
    """
    assert spacing is None or reference_file is None

    if size is None:
        size = data.shape
    size = ' '.join(list(map(lambda x: str(x), size)))

    spacing = ' '.join(list(map(lambda x: str(x), spacing))) if spacing is not None else ''

    tmp_files = []
    output_path = os.path.split(output_file)[0]
    tmp_mat = os.path.join(output_path, f"tmp_{uuid.uuid1()}.mat")
    tmp_files.append(tmp_mat)
    save_mat(tmp_mat, data)

    if not binary:
        if reference_file is None:
            execute_cmd(f"importMath {tmp_mat} matlab {output_file} {size} {spacing}")
        else:
            tmp_file = os.path.join(output_path, f"tmp_{uuid.uuid1()}.IM0")
            tmp_files.append(tmp_file)
            execute_cmd(f"importMath {tmp_mat} matlab {tmp_file} {size}")
            copy_pose(tmp_file, reference_file, output_file)
    if binary:
        if reference_file is None:
            tmp_file = os.path.join(output_path, f"tmp_{uuid.uuid1()}.IM0")
            tmp_files.append(tmp_file)
            execute_cmd(f"importMath {tmp_mat} matlab {tmp_file} {size} {spacing}")
            execute_cmd(f"ndthreshold {tmp_file} {output_file} 0 1 1")
        else:
            tmp_file = os.path.join(output_path, f"tmp_{uuid.uuid1()}.IM0")
            tmp_files.append(tmp_file)
            execute_cmd(f"importMath {tmp_mat} matlab {tmp_file} {size}")

            tmp_file1 = os.path.join(output_path, f"tmp_{uuid.uuid1()}.BIM")
            tmp_files.append(tmp_file1)
            execute_cmd(f"ndthreshold {tmp_file} {tmp_file1} 0 1 1")
            copy_pose(tmp_file1, reference_file, output_file)

    for each in tmp_files:
        os.remove(each)


def bin_ops(input_file_1, input_file_2, output_file, op):
    """
    Execute binary operations.
    Args:
        op: Supported options: or, nor, xor, xnor, and, nand, a-b
    """
    cmd_str = f'bin_ops {input_file_1} {input_file_2} {output_file} {op}'
    execute_cmd(cmd_str)


def median2d(input_file, output_path, mode=0):
    """
    Perform median filter.
    Args:
        mode: 0 for foreground, 1 for background, default is 0
    """
    execute_cmd(f"median2d {input_file} {output_path} {mode}")


def dicom2cavass(input_dicom_path, output_file):
    execute_cmd(f'from_dicom {input_dicom_path}/* {output_file}')
