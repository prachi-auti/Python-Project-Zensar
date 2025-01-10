from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
import json
from datetime import date, datetime
from decimal import Decimal

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "EventHallDB"
}

# Database Connection
def connect_to_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        raise Exception(f"Database connection failed: {e}")

# Custom JSON Encoder for Decimal and Date Handling
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# HTTP Request Handler
class EventHallRequestHandler(BaseHTTPRequestHandler):
    def send_json_response(self, status, message):
        """Helper function to send JSON responses."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(message, cls=CustomJSONEncoder).encode())

    def do_GET(self):
        db = None
        try:
            db = connect_to_db()
            cursor = db.cursor(dictionary=True)

            # Fetch all event halls
            if self.path == '/halls':
                cursor.execute("SELECT * FROM Event_Halls")
                result = cursor.fetchall()
                self.send_json_response(200, result)

            # Fetch all customers
            elif self.path == '/customers':
                cursor.execute("SELECT * FROM Customers")
                result = cursor.fetchall()
                self.send_json_response(200, result)

            # Fetch all bookings
            elif self.path == '/bookings':
                cursor.execute("""
                    SELECT b.Booking_ID, e.Hall_Name, c.Customer_Name, b.Event_Date, b.Booking_Status
                    FROM Bookings b
                    JOIN Event_Halls e ON b.Hall_ID = e.Hall_ID
                    JOIN Customers c ON b.Customer_ID = c.Customer_ID
                """)
                result = cursor.fetchall()
                self.send_json_response(200, result)

            # Fetch booking by ID
            elif self.path.startswith('/bookings/'):
                booking_id = self.path.split('/')[-1]
                if not booking_id.isdigit():
                    self.send_json_response(400, {"error": "Invalid booking ID"})
                    return

                cursor.execute("""
                    SELECT b.Booking_ID, e.Hall_Name, c.Customer_Name, b.Event_Date, b.Booking_Status
                    FROM Bookings b
                    JOIN Event_Halls e ON b.Hall_ID = e.Hall_ID
                    JOIN Customers c ON b.Customer_ID = c.Customer_ID
                    WHERE b.Booking_ID = %s
                """, (booking_id,))
                result = cursor.fetchone()
                if result:
                    self.send_json_response(200, result)
                else:
                    self.send_json_response(404, {"error": "Booking not found"})

            else:
                self.send_json_response(404, {"error": "Endpoint not found"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
        finally:
            if db:
                db.close()

    def do_POST(self):
        db = None
        try:
            db = connect_to_db()
            cursor = db.cursor()

            # Read and parse POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Add a new booking
            if self.path == '/add_booking':
                query = """
                    INSERT INTO Bookings (Hall_ID, Customer_ID, Event_Date, Booking_Status)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (data['hall_id'], data['customer_id'], data['event_date'], data.get('booking_status', 'Pending')))
                db.commit()
                self.send_json_response(201, {"message": "Booking added successfully"})

            # Add a new event hall
            elif self.path == '/add_hall':
                query = """
                    INSERT INTO Event_Halls (Hall_Name, Capacity, Location)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (data['hall_name'], data['capacity'], data['location']))
                db.commit()
                self.send_json_response(201, {"message": "Event hall added successfully"})

            # Add a new customer
            elif self.path == '/add_customer':
                query = """
                    INSERT INTO Customers (Customer_Name, Contact_Number, Email)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (data['customer_name'], data['contact_number'], data['email']))
                db.commit()
                self.send_json_response(201, {"message": "Customer added successfully"})

            else:
                self.send_json_response(404, {"error": "Endpoint not found"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})
        finally:
            if db:
                db.close()

# Run Server
def run(server_class=HTTPServer, handler_class=EventHallRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run()
