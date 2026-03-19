from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord
from PySide6.QtCore import QCoreApplication
import sys

def connect_to_postgres():
    # Define connection parameters
    host = "localhost"  # Adjust if your PostgreSQL server is on a different host
    database = "mydatabase"  # Default PostgreSQL database
    username = "postgres"
    password = "andrea"

    # Initialize the database connection
    db = QSqlDatabase.addDatabase("QPSQL")
    db.setHostName(host)
    db.setDatabaseName(database)
    db.setUserName(username)
    db.setPassword(password)

    # Attempt to open the database
    if db.open():
        print("Connection successful!")
        print(f"Connected to database: {db.databaseName()} on host: {db.hostName()}")
    else:
        print("Connection failed!")
        print(f"Error: {db.lastError().text()}")
        return

    query = QSqlQuery()

    # Execute the query
    if not query.exec("SELECT * FROM users"):  # Replace 'your_table_name'
        print(f"Query execution failed: {query.lastError().text()}")
        return

    # Fetch and print data
    if query.next():  # Move to the first (or next) record
        record = query.record()
        field_count = record.count()

        print("Field Names and Values:")
        for i in range(field_count):
            field_name = record.fieldName(i)  # Get field name
            field_value = query.value(i)  # Fetch field value
            print(f"{field_name}: {field_value}")
    else:
        print("No records found. Please check your table and query.")

    # Close the database
    if db.isOpen():
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)  # Initialize QCoreApplication

    # Check if the Qt SQL driver is available
    drivers = QSqlDatabase.drivers()
    print(f"Available drivers: {drivers}")
    if "QPSQL" not in drivers:
        print("Error: QPSQL driver not available.")
        sys.exit(1)

    # Attempt to connect to the database
    connect_to_postgres()