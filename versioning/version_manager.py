def create_version(
    connection,
    file_id,
    file_hash,
    file_size,
    backup_path,
    permissions,
    owner_name,
    group_name
):
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT MAX(version_number)
            FROM file_versions
            WHERE file_id = %s
            """,
            (file_id,)
        )

        result = cursor.fetchone()

        if result[0] is None:
            version_number = 1
        else:
            version_number = result[0] + 1

        cursor.execute(
            """
            INSERT INTO file_versions (
                file_id,
                version_number,
                file_hash,
                file_size,
                backup_path,
                permissions,
                owner_name,
                group_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                file_id,
                version_number,
                file_hash,
                file_size,
                backup_path,
                permissions,
                owner_name,
                group_name
            )
        )

        return version_number

    finally:
        cursor.close()