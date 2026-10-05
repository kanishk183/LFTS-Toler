from database.connection import create_connection


def generate_system_report():
    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        print()
        print("LFTS-Toler System Report")
        print("========================")

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM files
            """
        )

        total_files = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM files
            WHERE status = 'active'
            """
        )

        active_files = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM files
            WHERE status = 'modified'
            """
        )

        modified_files = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM files
            WHERE status = 'deleted'
            """
        )

        deleted_files = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM files
            WHERE status = 'corrupted'
            """
        )

        corrupted_files = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM backups
            WHERE status = 'completed'
            """
        )

        completed_backups = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM file_versions
            """
        )

        total_versions = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM recovery_logs
            WHERE status = 'completed'
            """
        )

        successful_recoveries = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM integrity_checks
            WHERE result = 'match'
            """
        )

        integrity_matches = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM integrity_checks
            WHERE result = 'mismatch'
            """
        )

        integrity_mismatches = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM integrity_checks
            WHERE result = 'missing'
            """
        )

        integrity_missing = cursor.fetchone()[0]

        print(f"Total files: {total_files}")
        print(f"Active files: {active_files}")
        print(f"Modified files: {modified_files}")
        print(f"Deleted files: {deleted_files}")
        print(f"Corrupted files: {corrupted_files}")
        print(f"Completed backups: {completed_backups}")
        print(f"Total versions: {total_versions}")
        print(f"Successful recoveries: {successful_recoveries}")
        print(f"Integrity matches: {integrity_matches}")
        print(f"Integrity mismatches: {integrity_mismatches}")
        print(f"Missing files detected: {integrity_missing}")

    except Exception as error:
        print(f"Report generation failed: {error}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    generate_system_report()