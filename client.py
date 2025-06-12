import os
os.environ["GEMINI_API_KEY"] = "AIzaSyClzy2W2CWILgQan4rIx5wMqNyxU-A4Y2U"

from fastmcp import Client
from google import genai
import asyncio
import mysql.connector
from server import query_database , get_weather
import ast  # Import the ast module for safe literal evaluation

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
async def invoke_tool(response_text):
    """Second agent to invoke the appropriate MCP tool based on the response."""
    second_agent_instruction = f"""
    You are a tool invocation assistant.
    Based on the following response: '{response_text}', invoke the appropriate MCP tool.
    Use the `get_weather` tool for weather-related queries and the `query_database` tool for database-related queries.
    return the output from the tool.
    """

    # Send the response to the second Gemini agent
    second_response = await gemini_client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=second_agent_instruction,
        config=genai.types.GenerateContentConfig(
            temperature=0,
            tools=[get_weather, query_database],  # Pass callable objects for tools
        ),
    )

    # Extract the tool invocation from the second agent's response
    tool_invocation = second_response.text.strip()
    print(f"Second Agent Response: {tool_invocation}")

    # Parse the tool invocation and invoke the appropriate MCP tool
async def main():
    # Fetch schemas dynamically from the schemas_of_db function
    schemas = schemas_of_db()
    context_window = []  # Initialize the context window to track conversation history
    system_instruction = f"""
    You are a helpful assistant.
    You can answer questions about student and teacher data from a database.
    Use the following database schemas as context for SQL queries, and generate valid SQL for the `query_database` tool: {schemas}.
    You can also provide weather information for any city using the `get_weather` tool.
    If a database request is ambiguous, ask the user for clarification by providing options. Start the clarification question with 'Clarification Question:'.
    Be concise in your responses.
    If you are answering a question about the weather, the response should be in the format:
    Weather in city: weather description, temperature: temperature°C, humidity: humidity%, wind speed: wind_speed m/s.
    If you are answering a question about the database, the response should be in the format:
    Database Query Result: result, where result is the SQL query.
    """

    while True:
        user_prompt = input("Ask me anything (or type 'exit' to quit): ")
        if user_prompt.strip().lower() == "exit":
            break

        # Add the user's input to the context window
        context_window.append({"role": "user", "content": user_prompt})
        context_window = context_window[-8:]  # Limit context window to the last 8 messages

        while True:  # Inner loop to handle clarifications
            # Send prompt to the first Gemini agent for response generation
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=system_instruction + "\n" + "\n".join(
                    f"{msg['role']}: {msg['content']}" for msg in context_window
                ),
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[],  # No tools for the first agent
                ),
            )
            # Extract the response from the first Gemini agent
            response_text = response.text.strip()

            # Check if the response is a clarification question
            if response_text.startswith("Clarification Question:"):
                print(f"{response_text}")
                clarification = input("Your response: ")
                context_window.append({"role": "user", "content": clarification})
                user_prompt = clarification  # Update the user prompt with the clarification
                continue  # Retry with the clarification added to the context

            # Add the Gemini response to the context window
            context_window.append({"role": "assistant", "content": response_text})

            # Pass the response to the second agent for tool invocation
            await invoke_tool(response_text)
            break  # Exit the inner loop after invoking the tool

# Example usage of the function



if __name__ == "__main__":
    asyncio.run(main())