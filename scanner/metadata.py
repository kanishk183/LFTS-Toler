import hashlib

from database.connection import create_connection
from integrity.hasher import calculate_sha256


def calculate_path_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()


def get_monitored_path_id(connection, directory_path):
    cursor = connection.cursor()

    query = """
        SELECT id
        FROM monitored_paths
        WHERE path = %s
    """

    cursor.execute(query, (directory_path,))
    result = cursor.fetchone()

    if result:
        cursor.close()
        return result[0]

    query = """
        INSERT INTO monitored_paths (path, description)
        VALUES (%s, %s)
    """

    cursor.execute(
        query,
        (directory_path, "LFTS-Toler monitored directory")
    )

    connection.commit()

    monitored_path_id = cursor.lastrowid

    cursor.close()

    return monitored_path_id


def save_file_metadata(connection, metadata):
    cursor = connection.cursor()

    file_hash = calculate_sha256(metadata["file_path"])
    file_path_hash = calculate_path_hash(metadata["file_path"])

    query = """
        SELECT id, current_hash, status
        FROM files
        WHERE file_path = %s
    """

    cursor.execute(query, (metadata["file_path"],))
    existing_file = cursor.fetchone()

    if existing_file is None:
        query = """
            INSERT INTO files (
                monitored_path_id,
                file_path,
                file_path_hash,
                file_name,
                file_size,
                permissions,
                owner_name,
                group_name,
                created_time,
                modified_time,
                accessed_time,
                current_hash,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        cursor.execute(
            query,
            (
                metadata["monitored_path_id"],
                metadata["file_path"],
                file_path_hash,
                metadata["file_name"],
                metadata["file_size"],
                metadata["permissions"],
                metadata["owner_name"],
                metadata["group_name"],
                metadata["created_time"],
                metadata["modified_time"],
                metadata["accessed_time"],
                file_hash,
                "active"
            )
        )

        print(f"New file detected: {metadata['file_path']}")

    else:
        file_id, previous_hash, previous_status = existing_file

        if previous_status == "corrupted":
            status = "corrupted"
        elif previous_hash != file_hash:
            status = "modified"
            print(f"Modified file detected: {metadata['file_path']}")
        else:
            status = "active"

        query = """
            UPDATE files
            SET file_name = %s,
                file_size = %s,
                permissions = %s,
                owner_name = %s,
                group_name = %s,
                created_time = %s,
                modified_time = %s,
                accessed_time = %s,
                current_hash = %s,
                status = %s,
                last_scanned_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        cursor.execute(
            query,
            (
                metadata["file_name"],
                metadata["file_size"],
                metadata["permissions"],
                metadata["owner_name"],
                metadata["group_name"],
                metadata["created_time"],
                metadata["modified_time"],
                metadata["accessed_time"],
                file_hash,
                status,
                file_id
            )
        )

    connection.commit()
    cursor.close()


def mark_deleted_files(connection, monitored_path_id, scanned_paths):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, file_path
        FROM files
        WHERE monitored_path_id = %s
          AND status != 'deleted'
        """,
        (monitored_path_id,)
    )

    database_files = cursor.fetchall()

    for file_id, file_path in database_files:
        if file_path not in scanned_paths:
            cursor.execute(
                """
                UPDATE files
                SET status = 'deleted',
                    last_scanned_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (file_id,)
            )

            print(f"Deleted file detected: {file_path}")

    connection.commit()
    cursor.close()


def save_scanned_files(directory_path, scanned_files):
    connection = create_connection()

    if connection is None:
        return

    try:
        monitored_path_id = get_monitored_path_id(
            connection,
            directory_path
        )

        scanned_paths = set()

        for metadata in scanned_files:
            metadata["monitored_path_id"] = monitored_path_id
            scanned_paths.add(metadata["file_path"])
            save_file_metadata(connection, metadata)

        mark_deleted_files(
            connection,
            monitored_path_id,
            scanned_paths
        )

        print("Scanned file metadata saved successfully.")

    except Exception as error:
        print(f"Failed to save file metadata: {error}")

    finally:
        connection.close()