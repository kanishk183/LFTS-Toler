import os
import shutil
from datetime import datetime

from database.connection import create_connection
from integrity.hasher import calculate_sha256
from versioning.version_manager import create_version
from scanner.scanner import get_file_metadata


def create_full_backup(source_directory):
    connection = create_connection()

    if connection is None:
        return

    backup_root = os.path.abspath("storage/full")
    backup_directory = os.path.join(
        backup_root,
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    cursor = connection.cursor()

    try:
        os.makedirs(backup_directory, exist_ok=True)

        started_at = datetime.now()

        cursor.execute(
            """
            INSERT INTO backups (
                backup_type,
                backup_path,
                started_at,
                status
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                "full",
                backup_directory,
                started_at,
                "running"
            )
        )

        backup_id = cursor.lastrowid
        connection.commit()

        total_files = 0
        total_size = 0

        for root, directories, filenames in os.walk(source_directory):
            relative_root = os.path.relpath(root, source_directory)

            if relative_root == ".":
                destination_root = backup_directory
            else:
                destination_root = os.path.join(
                    backup_directory,
                    relative_root
                )

            os.makedirs(destination_root, exist_ok=True)

            for filename in filenames:
                source_path = os.path.join(root, filename)
                destination_path = os.path.join(
                    destination_root,
                    filename
                )

                shutil.copy2(source_path, destination_path)

                file_hash = calculate_sha256(source_path)
                file_size = os.path.getsize(source_path)

                cursor.execute(
                    """
                    SELECT id
                    FROM files
                    WHERE file_path = %s
                    """,
                    (source_path,)
                )

                result = cursor.fetchone()

                if result is None:
                    continue

                file_id = result[0]

                cursor.execute(
                    """
                    INSERT INTO backup_items (
                        backup_id,
                        file_id,
                        source_path,
                        backup_path,
                        file_hash,
                        file_size
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        backup_id,
                        file_id,
                        source_path,
                        destination_path,
                        file_hash,
                        file_size
                    )
                )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM file_versions
                    WHERE file_id = %s
                    """,
                    (file_id,)
                )

                version_count = cursor.fetchone()[0]

                if version_count == 0:
                    metadata = get_file_metadata(source_path)

                    version_number = create_version(
                        connection,
                        file_id,
                        file_hash,
                        file_size,
                        destination_path,
                        metadata["permissions"],
                        metadata["owner_name"],
                        metadata["group_name"]
                    )

                    print(
                        f"Version {version_number} created for file ID {file_id}."
                    )

                total_files += 1
                total_size += file_size

        completed_at = datetime.now()

        cursor.execute(
            """
            UPDATE backups
            SET completed_at = %s,
                status = %s,
                total_files = %s,
                total_size = %s
            WHERE id = %s
            """,
            (
                completed_at,
                "completed",
                total_files,
                total_size,
                backup_id
            )
        )

        connection.commit()

        print("Full backup completed successfully.")
        print(f"Backup location: {backup_directory}")
        print(f"Total files: {total_files}")
        print(f"Total size: {total_size} bytes")

    except Exception as error:
        connection.rollback()

        if "backup_id" in locals():
            cursor.execute(
                """
                UPDATE backups
                SET status = %s,
                    completed_at = %s
                WHERE id = %s
                """,
                (
                    "failed",
                    datetime.now(),
                    backup_id
                )
            )

            connection.commit()

        print(f"Full backup failed: {error}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    source_directory = os.path.expanduser("~/lfts-test-data")
    create_full_backup(source_directory)