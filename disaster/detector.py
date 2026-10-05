from database.connection import create_connection
from scanner.scanner import scan_directory
from scanner.metadata import save_scanned_files


def detect_disasters(directory_path):
    scanned_files = scan_directory(directory_path)

    save_scanned_files(
        directory_path,
        scanned_files
    )

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                file_path,
                status
            FROM files
            WHERE status IN ('modified', 'deleted', 'corrupted')
            ORDER BY status, file_path
            """
        )

        detected_files = cursor.fetchall()

        print()
        print("LFTS-Toler Disaster Detection")
        print("==============================")

        if not detected_files:
            print("No filesystem faults detected.")
            return

        for file_path, status in detected_files:
            print(f"{status.upper()}: {file_path}")

    except Exception as error:
        print(f"Disaster detection failed: {error}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    import os

    source_directory = os.path.expanduser(
        "~/lfts-test-data"
    )

    detect_disasters(source_directory)
