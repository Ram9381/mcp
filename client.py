import os
os.environ["GEMINI_API_KEY"] = "AIzaSyClzy2W2CWILgQan4rIx5wMqNyxU-A4Y2U"

from fastmcp import Client
from google import genai
import asyncio
import mysql.connector
from server import query_database, get_weather  # Make sure get_weather exists in server.py

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
        context_window = context_window[-8:]  # Limit context window to the last 8 messages

        while True:  # Inner loop to handle clarifications and tool selection
            # Instruct Gemini to decide which tool (SQL or weather) to use and return a tool call instruction
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=(
                    f"Based on the following conversation context: {context_window}. "
                    f"Decide which tool to use for the following user request: '{user_prompt}'. "
                    f"You have access to two tools: "
                    f"1. SQL database (schemas: {schemas}) for student/teacher/course queries. "
                    f"2. Weather API (call as: WEATHER(location)) for weather-related queries. "
                    f"If the request is ambiguous, ask the user for clarification by providing options. "
                    f"Start the clarification question with 'Clarification Question:'. "
                    f"If you know which tool to use, respond ONLY with either a valid SQL query or WEATHER(location), "
                    f"with no extra explanation or formatting."
                ),
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[],
                ),
            )
            response_text = response.text.strip()
            response_text = response_text.replace("```sql", "").replace("```", "").strip()

            # Check if the response is a clarification question
            if response_text.startswith("Clarification Question:"):
                print(f"{response_text}")
                clarification = input("Your response: ")
                context_window.append({"role": "user", "content": clarification})
                user_prompt = clarification
                continue

            # Add the Gemini response to the context window
            context_window.append({"role": "assistant", "content": response_text})

            # Tool invocation logic
            if response_text.upper().startswith("WEATHER(") and response_text.endswith(")"):
                location = response_text[len("WEATHER("):-1].strip().strip("'\"")
                weather_result = get_weather(location)
                print(f"Weather for {location}:")
                print(weather_result)
            else:
                print(response_text)
                results = query_database(response_text)
                print(results)
            break  # Exit the inner loop after successful tool invocation

# Example usage of the function



if __name__ == "__main__":
    asyncio.run(main())