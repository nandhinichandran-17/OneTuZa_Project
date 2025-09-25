# Java JDBC

Java Database Connectivity (JDBC) is an API that enables Java applications to interact with relational databases. It provides a standard interface for sending SQL statements, retrieving results, and managing database connections.

## Key Components
- **DriverManager**: Manages a list of database drivers.
- **Connection**: Represents a session with a database.
- **Statement**: Used to execute SQL queries.
- **ResultSet**: Represents the result of a query.

## Workflow
1. Load the JDBC driver.
2. Establish a connection using `DriverManager.getConnection()`.
3. Create a `Statement` or `PreparedStatement`.
4. Execute SQL queries.
5. Process results using `ResultSet`.
6. Close resources to avoid leaks.

## Use Cases
- Connecting Java applications with MySQL, PostgreSQL, Oracle DB.
- CRUD operations (Create, Read, Update, Delete).
- Transaction management in enterprise systems.
