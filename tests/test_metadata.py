import os

from scanner.scanner import scan_directory
from scanner.metadata import save_scanned_files


test_directory = os.path.expanduser("~/lfts-test-data")

scanned_files = scan_directory(test_directory)

save_scanned_files(test_directory, scanned_files)