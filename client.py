import os
os.environ["GEMINI_API_KEY"] = "AIzaSyClzy2W2CWILgQan4rIx5wMqNyxU-A4Y2U"

from fastmcp import Client
from google import genai
import asyncio
import mysql.connector

# Initialize MCP client (adjust URL if needed)
mcp_client = Client("server.py")
gemini_client = genai.Client()

# Initialize MySQL connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database':  'abhidb'


}

async def main():
    while True:
        user_prompt = input("Ask me anything (or type 'exit' to quit): ")
        if user_prompt.strip().lower() == "exit":
            break

        # Send prompt to Gemini for SQL query generation
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Generate a valid SQL query for the following request: '{user_prompt}'. Only return the SQL query without any explanation or additional text.",
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=[],
            ),
        )
       
        try:
            if response.text and any(keyword in response.text.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
                sql_query = response.text.strip()
                
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                # Debug cleaned query
                # print(f"Cleaned SQL Query: {sql_query}")
            else:
                raise ValueError("Invalid response format")
        except Exception as e:
            print(f"Error: Gemini did not return a valid query. Falling back to manual query input. ({e})")
            sql_query = input("Enter SQL query manually (e.g., SELECT * FROM students WHERE age < 22): ")

        print(f"Generated SQL Query:{sql_query}")

        # Execute SQL query
        try:
           
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            cursor = conn.cursor()
           
            cursor.execute(sql_query)  # Use dynamically generated query
            result = cursor.fetchall()
            print(result)
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        
        finally:
            if conn:
                conn.close()  # Ensure connection is closed

if __name__ == "__main__":
    asyncio.run(main())