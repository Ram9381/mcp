import random
from fastmcp import FastMCP
import mysql.connector
from db_config import DB_CONFIG
import requests  # For making API requests

mcp = FastMCP(name="DB Reader")


@mcp.tool()
def query_database(query: str, values_only: bool = False) -> list:
    """Query the database (students or teachers) using a SQL query."""
    try:
        # Ensure the query string is properly escaped
        #query = query[1:-1]
        
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


@mcp.tool()
def get_weather(city: str) -> dict:
    """Fetch weather data for a given city using a weather API."""
    try:
        # Replace with your actual weather API endpoint and API key
        api_key = "e435336b0503ce3004bff40375003377"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}

        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        weather_data = response.json()

        # Extract relevant weather information
        return {
            "city": weather_data.get("name"),
            "temperature": weather_data["main"].get("temp"),
            "description": weather_data["weather"][0].get("description"),
            "humidity": weather_data["main"].get("humidity"),
            "wind_speed": weather_data["wind"].get("speed"),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()