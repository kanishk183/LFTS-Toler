import os

from scanner.scanner import scan_directory
from scanner.metadata import save_scanned_files
from backup.full_backup import create_full_backup
from backup.incremental_backup import create_incremental_backup
from verification.integrity_checker import verify_file
from recovery.recovery_engine import restore_file
from reporting.report import generate_system_report
from disaster.detector import detect_disasters


SOURCE_DIRECTORY = os.path.expanduser("~/lfts-test-data")


def scan_files():
    files = scan_directory(SOURCE_DIRECTORY)
    save_scanned_files(SOURCE_DIRECTORY, files)


def main():
    while True:
        print()
        print("LFTS-Toler")
        print("==========")
        print("1. Scan filesystem")
        print("2. Full backup")
        print("3. Incremental backup")
        print("4. Check file integrity")
        print("5. Restore file")
        print("6. Generate system report")
        print("7. Detect disasters")
        print("8. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            scan_files()

        elif choice == "2":
            scan_files()
            create_full_backup(SOURCE_DIRECTORY)

        elif choice == "3":
            scan_files()
            create_incremental_backup(SOURCE_DIRECTORY)

        elif choice == "4":
            file_id = int(input("Enter file ID: "))
            verify_file(file_id)

        elif choice == "5":
            file_id = int(input("Enter file ID: "))
            restore_file(file_id)

        elif choice == "6":
            generate_system_report()

        elif choice == "7":
            detect_disasters(SOURCE_DIRECTORY)

        elif choice == "8":
            print("Exiting LFTS-Toler.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()