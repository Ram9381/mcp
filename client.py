import os
os.environ["GEMINI_API_KEY"] = "AIzaSyClzy2W2CWILgQan4rIx5wMqNyxU-A4Y2U"

from fastmcp import Client
from google import genai
import asyncio
import mysql.connector
from server import query_database

# Initialize MCP client (adjust URL if needed)
mcp_client = Client("server.py")
gemini_client = genai.Client()

# Initialize MySQL connection

def schemas_of_db():
    schemas = {
        "students": {
            "columns": {
                "student_id": "int PK",
                "name": "varchar(50)",
                "course": "varchar(50)",
                "branch": "varchar(50)",
                "year": "int",
                "studentemailid": "varchar(50)",
                "fees": "decimal(10,2)",
                "grade": "varchar(2)",
                "sop": "tinyint(1)"
            }
        },
        "teachers": {
            "columns": {
                "teacher_id": "int PK",
                "name": "varchar(50)",
                "course": "varchar(50)"
            }
        },
        "relationships": {
            "students.course": "teachers.course"
        }
    }
    return schemas
async def main():
    # Fetch schemas dynamically from the schemas_of_db function
    schemas = schemas_of_db()
    context_window = []  # Initialize the context window to track conversation history

    while True:
        user_prompt = input("Ask me anything (or type 'exit' to quit): ")
        if user_prompt.strip().lower() == "exit":
            break

        # Add the user's input to the context window
        context_window.append({"role": "user", "content": user_prompt})
        context_window = context_window[-5:]  # Limit context window to the last 5 messages

        while True:  # Inner loop to handle clarifications
            # Send prompt to Gemini for SQL query generation
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Based on the following conversation context: {context_window}. Generate a valid SQL query for the following request: '{user_prompt}'. Use the following schemas and relationships as context: {schemas}. If the request is ambiguous, ask the user for clarification by providing options. Start the clarification question with 'Clarification Question:'. Return only the SQL query or the clarification question as plain text without any formatting, explanation, or additional text.",
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[],
                ),
            )
            # Extract the response from the Gemini client
            response_text = response.text.strip()  # Ensure no extra formatting
            response_text = response_text.replace("```sql", "").replace("```", "").strip()  # Remove formatting artifacts

            # Check if the response is a clarification question
            if response_text.startswith("Clarification Question:"):
                print(f"{response_text}")
                clarification = input("Your response: ")
                context_window.append({"role": "user", "content": clarification})
                user_prompt = clarification  # Update the user prompt with the clarification
                continue  # Retry with the clarification added to the context

            # Add the Gemini response to the context window
            context_window.append({"role": "assistant", "content": response_text})

            # Execute the SQL query and display results
            print(response_text)
            results = query_database(response_text)
            print(results)
            break  # Exit the inner loop after successful query execution

# Example usage of the function



if __name__ == "__main__":
    asyncio.run(main())