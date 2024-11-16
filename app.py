from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="your_password",  # Replace with the password you set
        host="localhost",
        port="5432"
    )

# Initialize the database (optional route)
@app.route('/init', methods=['GET'])
def init_db():
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

# GET all vehicles
@app.route('/vehicle', methods=['GET'])
def get_vehicles():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM vehicles;')
        vehicles = cur.fetchall()
        cur.close()
        conn.close()

        # Convert result to JSON
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

# POST a new vehicle
@app.route('/vehicle', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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

# GET a vehicle by VIN
@app.route('/vehicle/<string:vin>', methods=['GET'])
def get_vehicle(vin):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM vehicles WHERE vin = %s;', (vin,))
        vehicle = cur.fetchone()
        cur.close()
        conn.close()
        if vehicle:
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
            return jsonify({"error": "Vehicle not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PUT update a vehicle
@app.route('/vehicle/<string:vin>', methods=['PUT'])
def update_vehicle(vin):
    data = request.get_json()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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

# DELETE a vehicle
@app.route('/vehicle/<string:vin>', methods=['DELETE'])
def delete_vehicle(vin):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM vehicles WHERE vin = %s;', (vin,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port = 5000, debug=True)