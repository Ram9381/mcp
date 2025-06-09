import os
os.environ["GEMINI_API_KEY"] = "AIzaSyAI4Afn95LTl-e1IM6zgFzmLoARBFnrNM0"

from fastmcp import Client
from google import genai
import asyncio

# Initialize MCP client (adjust URL if needed)
mcp_client = Client("server.py")
gemini_client = genai.Client()

async def main():
    async with mcp_client:
        while True:
            user_prompt = input("Ask me anything (or type 'exit' to quit): ")
            if user_prompt.strip().lower() == "exit":
                break

            # Send prompt to Gemini for SQL query generation
            response = await gemini_client.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[mcp_client.session],
                ),
            )

            # Extract SQL query from Gemini response
            sql_query = response.text.strip()
            print(f"Generated SQL Query: {sql_query}")

            # Send SQL query to MCP server
            result = await mcp_client.tools.query_students_db(sql_query=sql_query)
            print("Query Result:", result)

if __name__ == "__main__":
    asyncio.run(main())