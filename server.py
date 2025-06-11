import random
from fastmcp import FastMCP
import mysql.connector
from db_config import DB_CONFIG
mcp = FastMCP(name="DB Reader")


@mcp.tool()
def query_database(query: str, values_only: bool = False) -> list:
    """Query the database (students or teachers) using a SQL query."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        cursor.execute(query)  # Execute SQL query
        if query.strip().lower().startswith("update"):
            conn.commit()  # Commit changes for UPDATE queries
            return [{"success": True, "message": "Update successful"}]
        results = cursor.fetchall()
        conn.close()
        if values_only:
            return [row[0] for row in results]  # Return only the first column's values
        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    mcp.run()