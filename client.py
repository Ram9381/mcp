import os
os.environ["GEMINI_API_KEY"] = "AIzaSyClzy2W2CWILgQan4rIx5wMqNyxU-A4Y2U"

from fastmcp import Client
from google import genai
import asyncio
import mysql.connector
from server import query_students

# Initialize MCP client (adjust URL if needed)
mcp_client = Client("server.py")
gemini_client = genai.Client()

# Initialize MySQL connection


async def main():
    while True:
        user_prompt = input("Ask me anything (or type 'exit' to quit): ")
        if user_prompt.strip().lower() == "exit":
            break

        # Send prompt to Gemini for SQL query generation
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Generate a valid SQL query for the following request: '{user_prompt}'. Return only the SQL query as plain text without any formatting, explanation, or additional text.",
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=[],
            ),
        )
        # Extract the SQL query string from the response object
        sql_query = response.text.strip()  # Ensure no extra formatting
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()  # Remove formatting artifacts
        print(sql_query)
        results = query_students(sql_query)
        print(results)
        
# Example usage of the function



if __name__ == "__main__":
    asyncio.run(main())