from database.connection import create_connection


def initialize_database():
    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        with open("database/schema.sql", "r") as file:
            schema = file.read()

        statements = schema.split(";")

        for statement in statements:
            statement = statement.strip()

            if statement:
                cursor.execute(statement)

        connection.commit()
        print("Database tables created successfully.")

    except Exception as error:
        connection.rollback()
        print(f"Database initialization failed: {error}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    initialize_database()