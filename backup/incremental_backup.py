import os
import shutil
from datetime import datetime

from database.connection import create_connection
from integrity.hasher import calculate_sha256
from versioning.version_manager import create_version
from scanner.scanner import get_file_metadata


def get_previous_backup_files(connection):
    cursor = connection.cursor()

    query = """
        SELECT source_path, file_hash
        FROM backup_items
        WHERE id IN (
            SELECT MAX(id)
            FROM backup_items
            GROUP BY file_id
        )
    """

    cursor.execute(query)

    previous_files = {}

    for source_path, file_hash in cursor.fetchall():
        previous_files[source_path] = file_hash

    cursor.close()

    return previous_files


def get_file_record(connection, file_path):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, status
        FROM files
        WHERE file_path = %s
        """,
        (file_path,)
    )

    result = cursor.fetchone()

    cursor.close()

    return result


def create_incremental_backup(source_directory):
    connection = create_connection()

    if connection is None:
        return

    backup_root = os.path.abspath("storage/incremental")
    backup_directory = os.path.join(
        backup_root,
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    cursor = connection.cursor()

    try:
        previous_files = get_previous_backup_files(connection)

        changed_files = []

        for root, directories, filenames in os.walk(source_directory):
            for filename in filenames:
                source_path = os.path.join(root, filename)

                file_record = get_file_record(
                    connection,
                    source_path
                )

                if file_record is None:
                    print(
                        f"Skipping unregistered file: {source_path}"
                    )
                    continue

                file_id, status = file_record

                if status == "corrupted":
                    print(
                        f"Skipping corrupted file: {source_path}"
                    )
                    continue

                current_hash = calculate_sha256(source_path)

                if source_path in previous_files:
                    if current_hash == previous_files[source_path]:
                        continue

                changed_files.append(
                    (
                        source_path,
                        current_hash,
                        file_id
                    )
                )

        if not changed_files:
            print("No files changed since the previous backup.")
            return

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
                "incremental",
                backup_directory,
                started_at,
                "running"
            )
        )

        backup_id = cursor.lastrowid
        connection.commit()

        total_files = 0
        total_size = 0

        for source_path, current_hash, file_id in changed_files:
            relative_path = os.path.relpath(
                source_path,
                source_directory
            )

            destination_path = os.path.join(
                backup_directory,
                relative_path
            )

            destination_directory = os.path.dirname(
                destination_path
            )

            os.makedirs(
                destination_directory,
                exist_ok=True
            )

            shutil.copy2(
                source_path,
                destination_path
            )

            file_size = os.path.getsize(source_path)

            metadata = get_file_metadata(source_path)

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
                    current_hash,
                    file_size
                )
            )

            version_number = create_version(
                connection,
                file_id,
                current_hash,
                file_size,
                destination_path,
                metadata["permissions"],
                metadata["owner_name"],
                metadata["group_name"]
            )

            cursor.execute(
                """
                UPDATE files
                SET current_hash = %s,
                    file_size = %s,
                    permissions = %s,
                    owner_name = %s,
                    group_name = %s,
                    modified_time = %s,
                    accessed_time = %s,
                    status = %s,
                    last_scanned_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    current_hash,
                    metadata["file_size"],
                    metadata["permissions"],
                    metadata["owner_name"],
                    metadata["group_name"],
                    metadata["modified_time"],
                    metadata["accessed_time"],
                    "active",
                    file_id
                )
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

        print("Incremental backup completed successfully.")
        print(f"Backup location: {backup_directory}")
        print(f"Changed files: {total_files}")
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

        print(f"Incremental backup failed: {error}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    source_directory = os.path.expanduser(
        "~/lfts-test-data"
    )

    create_incremental_backup(source_directory)