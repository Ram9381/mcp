import random
from fastmcp import FastMCP
import mysql.connector
from db_config import DB_CONFIG
import requests  # For making API requests

mcp = FastMCP(name="Database_Reader")

@mcp.tool()
def print_hello() -> str:
    """Prints 'Hello, World!'"""
    return "Hello, World!"
@mcp.tool()
def query_database(query: str, values_only: bool = False) -> list:
    """Execute a SQL SELECT query on the 'products', 'orders', or 'order_items' tables.
    Supported Tables and Schemas:
    1. products
       - product_id (INT, primary key)
       - name (VARCHAR)
       - price (DECIMAL)
       - stock_quantity (INT)
    2. orders
       - order_id (INT, primary key)
       - customer_name (VARCHAR)
       - total_amount (DECIMAL)
    3. order_items
       - item_id (INT, primary key)
       - order_id (INT, foreign key to orders.order_id)
       - product_id (INT, foreign key to products.product_id)
       - quantity (INT)
       - item_price (DECIMAL)
     Usage:
    - Use valid column names as per the schemas above.
    - You may use JOINs between the supported tables.
    Parameters:
    - query (str): A valid SQL SELECT query string.
    - values_only (bool): If True, returns list of row values only.
                          If False (default), returns list of dicts with column names.
    Examples:
    - query="SELECT * FROM orders WHERE total_amount > 10000"
    - query="SELECT name, price FROM products WHERE stock_quantity < 20"
    - query="SELECT o.customer_name, p.name, oi.quantity FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id"
    """
    try:

        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            auth_plugin=DB_CONFIG['auth_plugin']
        )
        cursor = conn.cursor()
        cursor.execute(query)  
        if query.strip().lower().startswith("update"):
            conn.commit() 
            return [{"success": True, "message": "Update successful"}]
        results = cursor.fetchall()
        conn.close()
        if values_only:
            return [row[0] for row in results]  
        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_weather(city: str) -> dict:
    """Fetch weather data for a given city using a weather API.
    
    Use this tool when the user asks about:
    - Current weather conditions in any city
    - Temperature, humidity, wind speed for a location
    - Weather descriptions or forecasts
    - Climate information for travel or planning
    
    Args:
        city: Name of the city to get weather information for."""
    try:
        
        api_key = "e435336b0503ce3004bff40375003377"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}

        response = requests.get(base_url, params=params)
        response.raise_for_status()  
        weather_data = response.json()

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