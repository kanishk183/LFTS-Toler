import os
import stat
import pwd
import grp
from datetime import datetime


def get_file_metadata(file_path):
    file_info = os.stat(file_path)

    metadata = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "file_size": file_info.st_size,
        "permissions": stat.filemode(file_info.st_mode),
        "owner_name": pwd.getpwuid(file_info.st_uid).pw_name,
        "group_name": grp.getgrgid(file_info.st_gid).gr_name,
        "created_time": datetime.fromtimestamp(file_info.st_ctime),
        "modified_time": datetime.fromtimestamp(file_info.st_mtime),
        "accessed_time": datetime.fromtimestamp(file_info.st_atime)
    }

    return metadata


def scan_directory(directory_path):
    files = []

    for root, directories, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(get_file_metadata(file_path))

    return files


if __name__ == "__main__":
    test_directory = os.path.expanduser("~/lfts-test-data")

    scanned_files = scan_directory(test_directory)

    for file_info in scanned_files:
        print(file_info)