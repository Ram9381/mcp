import requests
import json
import uuid
from typing import Dict, Any, Optional

class MCPClient:
    """Client for interacting with FastMCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
        self.headers = {
            'Accept': 'application/json, text/event-stream',
            'X-Session-Id': self.session_id,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, tool_name: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to MCP server using MCP protocol"""
        url = f"{self.base_url}/mcp/"
        
        # MCP protocol payload
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract the actual result from MCP response
            if "result" in result:
                return result["result"]
            else:
                return result
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def print_hello(self) -> Dict[str, Any]:
        """Call the print_hello tool"""
        return self._make_request('print_hello')
    
    def query_database(self, query: str, values_only: bool = False) -> Dict[str, Any]:
        """Execute a SQL SELECT query on the database
        
        Args:
            query: SQL SELECT query string
            values_only: If True, returns list of row values only
        """
        params = {
            "query": query,
            "values_only": values_only
        }
        return self._make_request('query_database', params)
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Fetch weather data for a given city
        
        Args:
            city: Name of the city to get weather information for
        """
        params = {"city": city}
        return self._make_request('get_weather', params)

def main():
    """Example usage of the MCP client"""
    # Initialize client
    client = MCPClient("http://localhost:8000")
    
    print("=== MCP Client Demo ===\n")
    
    # Test 1: Print Hello
    print("1. Testing print_hello:")
    result = client.print_hello()
    print(f"Result: {result}\n")
    
    # Test 2: Query Database - Get all products
    print("2. Testing database query - Get all products:")
    result = client.query_database("SELECT * FROM products LIMIT 5")
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 3: Query Database - Get products with low stock
    print("3. Testing database query - Products with low stock:")
    result = client.query_database("SELECT name, price, stock_quantity FROM products WHERE stock_quantity < 20")
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 4: Query Database - Complex JOIN query
    print("4. Testing database query - Orders with product details:")
    query = """
    SELECT o.customer_name, p.name as product_name, oi.quantity, oi.item_price 
    FROM orders o 
    JOIN order_items oi ON o.order_id = oi.order_id 
    JOIN products p ON p.product_id = oi.product_id 
    LIMIT 5
    """
    result = client.query_database(query)
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 5: Get Weather
    print("5. Testing weather API:")
    result = client.get_weather("Mumbai")
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 6: Query with values_only=True
    print("6. Testing database query with values_only=True:")
    result = client.query_database("SELECT name FROM products LIMIT 3", values_only=True)
    print(f"Result: {result}\n")

# Interactive mode
def interactive_mode():
    """Interactive mode to test different queries"""
    client = MCPClient("http://localhost:8000")
    
    print("=== Interactive MCP Client ===")
    print("Available commands:")
    print("1. hello - Test print_hello")
    print("2. query <sql> - Execute SQL query")
    print("3. weather <city> - Get weather for city")
    print("4. quit - Exit")
    print()
    
    while True:
        try:
            command = input("Enter command: ").strip()
            
            if command.lower() == 'quit':
                break
            elif command.lower() == 'hello':
                result = client.print_hello()
                print(f"Result: {result}")
            elif command.startswith('query '):
                sql_query = command[6:]  # Remove 'query ' prefix
                result = client.query_database(sql_query)
                print(f"Result: {json.dumps(result, indent=2)}")
            elif command.startswith('weather '):
                city = command[8:]  # Remove 'weather ' prefix
                result = client.get_weather(city)
                print(f"Result: {json.dumps(result, indent=2)}")
            else:
                print("Unknown command. Available: hello, query <sql>, weather <city>, quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run the demo
    main()
    
    # Uncomment the line below to run in interactive mode
    # interactive_mode()