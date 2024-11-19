from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Establish a connection to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",  
        host="localhost",
        port="5432"
    )

# Create the database table if it doesn't exist
@app.route('/init', methods=['GET'])
def init_db():
    """
    Input: None (Triggered by a GET request to /init)
    Output: JSON response with a success or error message
        - If the database connection fails, it will return a 500 status code with the error message.
        - If the table already exists, the operation is idempotent (no duplicate errors).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                vin VARCHAR PRIMARY KEY,
                manufacturer_name VARCHAR NOT NULL,
                description TEXT,
                horse_power INTEGER NOT NULL,
                model_name VARCHAR NOT NULL,
                model_year INTEGER NOT NULL,
                purchase_price DECIMAL NOT NULL,
                fuel_type VARCHAR NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Table created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch all vehicles from the database
@app.route('/vehicle', methods=['GET'])
def get_vehicles():
    """
    Input: None (Triggered by a GET request to /vehicle)
    Output: JSON response containing a list of all vehicles or an error message
        - If the database connection fails, it returns a 500 status code with error message.
        - If no vehicles exist in the table, it returns an empty list.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM vehicles;')
        vehicles = cur.fetchall()
        cur.close()
        conn.close()

        # Format the vehicles as JSON
        vehicle_list = [
            {
                "vin": row[0],
                "manufacturer_name": row[1],
                "description": row[2],
                "horse_power": row[3],
                "model_name": row[4],
                "model_year": row[5],
                "purchase_price": float(row[6]),
                "fuel_type": row[7]
            }
            for row in vehicles
        ]
        return jsonify(vehicle_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Retrieve a specific vehicle by its VIN
@app.route('/vehicle/<string:vin>', methods=['GET'])
def get_vehicle(vin):
    """
    Input: VIN (via the URL parameter /vehicle/<vin>)
    Output: JSON response with vehicle details or an error message
        - If the VIN does not exist in the database, it returns a 404 status code with a "Vehicle not found" message.
        - If the database connection fails, it returns a 500 status code with error message.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM vehicles WHERE vin = %s;', (vin,))
        vehicle = cur.fetchone()
        cur.close()
        conn.close()
        if vehicle:
            # Format the vehicle data as JSON
            vehicle_data = {
                "vin": vehicle[0],
                "manufacturer_name": vehicle[1],
                "description": vehicle[2],
                "horse_power": vehicle[3],
                "model_name": vehicle[4],
                "model_year": vehicle[5],
                "purchase_price": float(vehicle[6]),
                "fuel_type": vehicle[7]
            }
            return jsonify(vehicle_data), 200
        else:
            return jsonify({"message": "Vehicle not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Add a new vehicle to the database
@app.route('/vehicle', methods=['POST'])
def create_vehicle():
    """
    Input: JSON object containing vehicle details
        Required fields: vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type
    Output: JSON response with success or error message
        - If any required field is missing, it returns a 400 status code with the missing field.
        - If the VIN already exists in the database, it returns a 422 status code with a "VIN already exists" message.
        - If any field contains invalid data (e.g., negative purchase price), it returns a 422 status code with a validation error message.
        - If the database connection fails, it returns a 500 status code with  error message.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ["vin", "manufacturer_name", "description", "horse_power", "model_name", "model_year", "purchase_price", "fuel_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()

    # Check for duplicate VIN
    vin = data.get('vin')
    cur.execute('SELECT COUNT(*) FROM vehicles WHERE vin = %s;', (vin,))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return jsonify({"message": "VIN already exists"}), 422

    # Validate fields
    if not isinstance(data.get("horse_power"), int) or data.get("horse_power") <= 0:
        return jsonify({"message": "Invalid horse_power"}), 422

    if not isinstance(data.get("purchase_price"), (float, int)) or data.get("purchase_price") <= 0:
        return jsonify({"message": "Invalid purchase_price"}), 422
    
    try:
        # Insert the vehicle into the database
        cur.execute('''
            INSERT INTO vehicles (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        ''', (
            data['vin'], data['manufacturer_name'], data['description'],
            data['horse_power'], data['model_name'], data['model_year'],
            data['purchase_price'], data['fuel_type']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Vehicle created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 422
    
# Update an existing vehicle's details
@app.route('/vehicle/<string:vin>', methods=['PUT'])
def update_vehicle(vin):
    """
    Input: VIN (via the URL parameter /vehicle/<vin>) and JSON object containing updated vehicle details
        Required fields: manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type
    Output: JSON response with success or error message
        - If any required field is missing, it returns a 400 status code with the missing field.
        - If the VIN does not exist in the database, it returns a 404 status code with a "Vehicle not found" message.
        - If any field contains invalid data (e.g., negative purchase price), it returns a 422 status code with a validation error message.
        - If the database connection fails, it returns a 500 status code with the error message.
    """
    if not request.is_json:
        return jsonify({"message": "Invalid JSON"}), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ["manufacturer_name", "description", "horse_power", "model_name", "model_year", "purchase_price", "fuel_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400

    # Validate field values
    if not isinstance(data["horse_power"], int) or data["horse_power"] <= 0:
        return jsonify({"message": "Invalid horse_power"}), 422

    if not isinstance(data["purchase_price"], (int, float)) or data["purchase_price"] <= 0:
        return jsonify({"message": "Invalid purchase_price"}), 422
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Update the vehicle details in the database
        cur.execute('''
            UPDATE vehicles
            SET manufacturer_name = %s, description = %s, horse_power = %s,
                model_name = %s, model_year = %s, purchase_price = %s, fuel_type = %s
            WHERE vin = %s;
        ''', (
            data['manufacturer_name'], data['description'], data['horse_power'],
            data['model_name'], data['model_year'], data['purchase_price'],
            data['fuel_type'], vin
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Vehicle updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 422

# Remove a vehicle from the database
@app.route('/vehicle/<string:vin>', methods=['DELETE'])
def delete_vehicle(vin):
    """
    Input: VIN (via the URL parameter /vehicle/<vin>)
    Output: Empty response with a 204 status code on success or an error message
        - If the VIN does not exist in the database, it returns a 404 status code with a "Vehicle not found" message.
        - If the database connection fails, it returns a 500 status code with the error message.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the vehicle exists
        cur.execute('SELECT * FROM vehicles WHERE vin = %s;', (vin,))
        vehicle = cur.fetchone()

        if not vehicle:
            cur.close()
            conn.close()
            return jsonify({"message": "Vehicle not found"}), 404
        
        # Delete the vehicle
        cur.execute('DELETE FROM vehicles WHERE vin = %s;', (vin,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application
    app.run(port = 5000, debug=True)