import random
from fastmcp import FastMCP
import csv
import pandas as pd
from pymongo import MongoClient
from db_config import DB_CONFIG
import mysql.connector

mcp = FastMCP(name="DB Reader")

# @mcp.tool()
# def roll_dice(n_dice: int) -> list[int]:
#     """Roll `n_dice` 6-sided dice and return the results."""
#     return [random.randint(1, 6) for _ in range(n_dice)]

# @mcp.tool()
# def sum_of_range(start: int, end: int) -> int:
#     """Calculate the sum of integers from `start` to `end` (inclusive)."""
#     if start > end:
#         raise ValueError("Start must be less than or equal to end.")
#     return sum(range(start, end + 1))

# @mcp.tool()
# def get_student_detail(name: str) -> dict:
#     """Retrieve details for a student by name from the CSV file."""
#     with open("data.csv", newline="") as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if row["Name"].lower() == name.lower():
#                 return row
    # return {"error": "Student not found"}

# @mcp.tool()
# def get_student_by_roll(roll_number: str) -> dict:
#     """Retrieve details for a student by roll number from the CSV file."""
#     with open("data.csv", newline="") as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if row["RollNumber"] == roll_number:
#                 return row
#     return {"error": "Student not found"}

# @mcp.tool()
# def list_all_students() -> list[dict]:
#     """List all students from the CSV file."""
#     with open("data.csv", newline="") as csvfile:
#         reader = csv.DictReader(csvfile)
#         return list(reader)

# @mcp.tool()
# def search_students_by_age(age: int) -> list[dict]:
#     """Retrieve all students with the given age."""
#     results = []
#     with open("data.csv", newline="") as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if int(row["Age"]) == age:
#                 results.append(row)
#     return results

# @mcp.tool()
# def query_data_csv(sql_query: str) -> list[dict]:
#     """
#     Query the student database (data.csv) using a pandas query string.
#     Example: 'Age < 22' will return all students younger than 22.
#     Use this tool to answer any question about the students, such as filtering, searching, or aggregating data.
#     Example usage:
#       - To get all students older than 20: 'Age > 20'
#       - To find a student named Alice: 'Name == "Alice"'
#       - To get students with RollNumber starting with '10': 'RollNumber.str.startswith("10")'
#     The input should be a valid pandas DataFrame query string.
#     """
#     df = pd.read_csv("data.csv")
#     df.columns = [col.strip() for col in df.columns]
#     try:
#         result = df.query(sql_query, engine='python')
#         return result.to_dict(orient="records")
#     except Exception as e:
#         return [{"error": str(e)}]

@mcp.tool()
def query_students_db(query: str) -> list[dict]:
    
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