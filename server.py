import random
from fastmcp import FastMCP
import csv
import pandas as pd
from pymongo import MongoClient
from db_config import DB_CONFIG
import mysql.connector

mcp = FastMCP(name="DB Reader")


def query_students_db(query: str) -> list[dict]:
    """Query the students database using a SQL query."""
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
        results = cursor.fetchall()
        conn.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    mcp.run()