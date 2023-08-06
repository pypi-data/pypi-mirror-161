import os
import tarfile
from typing import List


def make_executable(file_path):
    mode = os.stat(file_path).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(file_path, mode)


def create_file_from_content(file_path, content, executable=False):
    with open(file_path, "w") as text_file:
        text_file.write(content)
    if executable:
        make_executable(file_path)


def make_tarfile(
    output_filename, source_dir, additional_directories: List, ignore_list=None
):
    ignore_list = ignore_list or []
    with tarfile.open(output_filename, "w:gz") as tar:
        _add_directory_in_tar(ignore_list, source_dir, tar)
        for additional_directory in additional_directories:
            _add_directory_in_tar(ignore_list, additional_directory, tar)


def _add_directory_in_tar(ignore_list, source_dir, tar):
    for fn in os.listdir(source_dir):
        if fn not in ignore_list:
            p = os.path.join(source_dir, fn)
            tar.add(p, arcname=fn)
        else:
            print(f"Ignoring {fn}")
