import mysql.connector
from db_config import DB_CONFIG

def test_connection():
    try:
        # Establish connection to MySQL
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()
        cursor.execute("SELECT * from students")
        result1 = cursor.fetchall()

        print(f"Connected to database: {result[0]}")
        print(f"{result1}")
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    test_connection()