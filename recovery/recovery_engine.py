import os
import shutil
import pwd
import grp
from datetime import datetime

from database.connection import create_connection
from integrity.hasher import calculate_sha256


def permissions_to_mode(permissions):
    mode = 0

    values = {
        "r": 4,
        "w": 2,
        "x": 1
    }

    for index, position in enumerate(range(1, 10)):
        character = permissions[position]

        if character in values:
            mode += values[character] << (3 * (2 - index // 3))

    return mode


def get_trusted_version(cursor, file_id):
    cursor.execute(
        """
        SELECT
            version_number,
            backup_path,
            file_hash,
            permissions,
            owner_name,
            group_name
        FROM file_versions
        WHERE file_id = %s
        ORDER BY version_number DESC
        """,
        (file_id,)
    )

    versions = cursor.fetchall()

    for version in versions:
        (
            version_number,
            backup_path,
            expected_hash,
            permissions,
            owner_name,
            group_name
        ) = version

        if not os.path.exists(backup_path):
            continue

        actual_hash = calculate_sha256(backup_path)

        if actual_hash == expected_hash:
            return version

    return None


def restore_file(file_id):
    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()
    recovery_id = None

    try:
        cursor.execute(
            """
            SELECT file_path
            FROM files
            WHERE id = %s
            """,
            (file_id,)
        )

        file_record = cursor.fetchone()

        if file_record is None:
            print("File record not found.")
            return False

        destination_path = file_record[0]

        version = get_trusted_version(
            cursor,
            file_id
        )

        if version is None:
            print("No trusted backup version found.")
            return False

        (
            version_number,
            backup_path,
            expected_hash,
            permissions,
            owner_name,
            group_name
        ) = version

        cursor.execute(
            """
            INSERT INTO recovery_logs (
                file_id,
                recovery_source,
                destination_path,
                recovery_type,
                status,
                started_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                file_id,
                backup_path,
                destination_path,
                "file",
                "started",
                datetime.now()
            )
        )

        recovery_id = cursor.lastrowid
        connection.commit()

        destination_directory = os.path.dirname(destination_path)

        if destination_directory:
            os.makedirs(destination_directory, exist_ok=True)

        shutil.copy2(
            backup_path,
            destination_path
        )

        if permissions:
            os.chmod(
                destination_path,
                permissions_to_mode(permissions)
            )

        if owner_name and group_name:
            try:
                uid = pwd.getpwnam(owner_name).pw_uid
                gid = grp.getgrnam(group_name).gr_gid
                os.chown(destination_path, uid, gid)
            except PermissionError:
                pass

        actual_hash = calculate_sha256(destination_path)

        if actual_hash != expected_hash:
            cursor.execute(
                """
                UPDATE recovery_logs
                SET status = %s,
                    message = %s,
                    completed_at = %s
                WHERE id = %s
                """,
                (
                    "failed",
                    "SHA-256 verification failed after recovery.",
                    datetime.now(),
                    recovery_id
                )
            )

            connection.commit()

            print("Recovery failed: SHA-256 verification mismatch.")
            return False

        cursor.execute(
            """
            UPDATE files
            SET current_hash = %s,
                status = %s,
                last_scanned_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                actual_hash,
                "active",
                file_id
            )
        )

        cursor.execute(
            """
            UPDATE recovery_logs
            SET status = %s,
                message = %s,
                completed_at = %s
            WHERE id = %s
            """,
            (
                "completed",
                f"Version {version_number} restored and SHA-256 verification succeeded.",
                datetime.now(),
                recovery_id
            )
        )

        connection.commit()

        print("File recovery completed successfully.")
        print(f"Restored version: {version_number}")
        print(f"Restored file: {destination_path}")
        print(f"Verified SHA-256: {actual_hash}")

        return True

    except Exception as error:
        connection.rollback()

        if recovery_id is not None:
            cursor.execute(
                """
                UPDATE recovery_logs
                SET status = %s,
                    message = %s,
                    completed_at = %s
                WHERE id = %s
                """,
                (
                    "failed",
                    str(error),
                    datetime.now(),
                    recovery_id
                )
            )

            connection.commit()

        print(f"File recovery failed: {error}")

        return False

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    print("Use restore_file(file_id) to recover a file.")