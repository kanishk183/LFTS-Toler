import os

from database.connection import create_connection
from integrity.hasher import calculate_sha256


def get_expected_hash(cursor, file_id):
    cursor.execute(
        """
        SELECT file_hash
        FROM file_versions
        WHERE file_id = %s
        ORDER BY version_number DESC
        LIMIT 1
        """,
        (file_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        SELECT file_hash
        FROM backup_items
        WHERE file_id = %s
        ORDER BY backup_id DESC
        LIMIT 1
        """,
        (file_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None


def verify_file(file_id):
    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT file_path
            FROM files
            WHERE id = %s
            """,
            (file_id,)
        )

        result = cursor.fetchone()

        if result is None:
            print("File record not found.")
            return False

        file_path = result[0]

        expected_hash = get_expected_hash(
            cursor,
            file_id
        )

        if expected_hash is None:
            print("No trusted backup hash found.")
            return False

        if not os.path.exists(file_path):
            cursor.execute(
                """
                INSERT INTO integrity_checks (
                    file_id,
                    expected_hash,
                    actual_hash,
                    result
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    file_id,
                    expected_hash,
                    None,
                    "missing"
                )
            )

            cursor.execute(
                """
                UPDATE files
                SET status = 'deleted'
                WHERE id = %s
                """,
                (file_id,)
            )

            connection.commit()

            print("Integrity check: file is missing.")
            return False

        actual_hash = calculate_sha256(file_path)

        if actual_hash == expected_hash:
            result_status = "match"
            print("Integrity check: MATCH")
        else:
            result_status = "mismatch"
            print("Integrity check: MISMATCH")

        cursor.execute(
            """
            INSERT INTO integrity_checks (
                file_id,
                expected_hash,
                actual_hash,
                result
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                file_id,
                expected_hash,
                actual_hash,
                result_status
            )
        )

        if result_status == "mismatch":
            cursor.execute(
                """
                UPDATE files
                SET status = 'corrupted'
                WHERE id = %s
                """,
                (file_id,)
            )
        else:
            cursor.execute(
                """
                UPDATE files
                SET status = 'active',
                    current_hash = %s
                WHERE id = %s
                """,
                (
                    actual_hash,
                    file_id
                )
            )

        connection.commit()

        return result_status == "match"

    except Exception as error:
        connection.rollback()
        print(f"Integrity check failed: {error}")
        return False

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    print("Use verify_file(file_id) to perform an integrity check.")