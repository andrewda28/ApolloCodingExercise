import pytest
from app import app
import psycopg2

@pytest.fixture
def client():
    # Set up a test client for the Flask application and prepare the test database
    app.config['TESTING'] = True

    # Connect to the PostgreSQL database and reset it
    conn = psycopg2.connect(database="postgres", host="localhost", user="postgres", password="password", port="5432")
    cur = conn.cursor()

    # Clear any existing data in the 'vehicles' table
    cur.execute('TRUNCATE TABLE vehicles;')

    # Create the 'vehicles' table if it doesn't already exist
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

    # Insert a sample vehicle into the table for testing
    cur.execute('''
    INSERT INTO vehicles (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
    VALUES ('1HGCM82633A123456', 'Honda', 'A reliable car', 200, 'Civic', 2022, 25000.00, 'Gasoline')
    ON CONFLICT (vin) DO NOTHING; -- Avoid duplicate entries
    ''')

    conn.commit()
    cur.close()
    conn.close()

    with app.test_client() as client:
        yield client

# Test if the database initialization endpoint works correctly
def test_init_db(client):
    response = client.get('/init')
    assert response.status_code == 200
    assert response.get_json()['message'] == "Table created successfully!"

# Test creating a unique vehicle
def test_create_vehicle_unique(client):
    vehicle_data = {
        "vin": "1HGCM82633A654321",
        "manufacturer_name": "Lamborghini",
        "description": "A luxury sports car",
        "horse_power": 770,
        "model_name": "Aventador",
        "model_year": 2023,
        "purchase_price": 500000.00,
        "fuel_type": "Gasoline"
    }
    response = client.post('/vehicle', json=vehicle_data)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Vehicle created successfully!"

# Test creating a vehicle with a duplicate VIN
def test_create_vehicle_duplicate(client):
    vehicle_data = {
        "vin": "1HGCM82633A123456",
        "manufacturer_name": "Honda",
        "description": "A reliable car",
        "horse_power": 200,
        "model_name": "Civic",
        "model_year": 2022,
        "purchase_price": 25000.00,
        "fuel_type": "Gasoline"
    }
    response = client.post('/vehicle', json=vehicle_data)
    assert response.status_code == 422
    assert response.get_json()["message"] == "VIN already exists"

# Test creating a vehicle with a missing required field
def test_create_vehicle_missing_field(client):
    vehicle_data = {
        "vin": "1HGCM82633A123456",
        "manufacturer_name": "Honda",
        # Missing "description"
        "horse_power": 200,
        "model_name": "Civic",
        "model_year": 2022,
        "purchase_price": 25000.00,
        "fuel_type": "Gasoline"
    }
    response = client.post('/vehicle', json=vehicle_data)
    assert response.status_code == 400
    assert "Missing required field: description" in response.get_json()["message"]

# Test creating a vehicle with an invalid field value
def test_create_vehicle_invalid_field(client):
    vehicle_data = {
        "vin": "1HGCM82633A123451",
        "manufacturer_name": "Ford",
        "description": "A durable and reliable truck",
        "horse_power": -200,  # Invalid value
        "model_name": "F-150",
        "model_year": 2022,
        "purchase_price": 40000.00,
        "fuel_type": "Gasoline"
    }
    response = client.post('/vehicle', json=vehicle_data)
    assert response.status_code == 422
    assert "Invalid horse_power" in response.get_json()["message"]

# Test retrieving all vehicles from the database
def test_get_vehicles(client):
    response = client.get('/vehicle')
    assert response.status_code == 200
    vehicles = response.get_json()
    assert isinstance(vehicles, list)  # Ensure the response is a list
    assert len(vehicles) >= 1  # At least one vehicle should exist

# Test retrieving vehicles when the table is empty
def test_get_vehicles_empty_table(client):
    # Clear the table
    conn = psycopg2.connect(database="postgres", host="localhost", user="postgres", password="password", port="5432")
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE vehicles;')
    conn.commit()
    cur.close()
    conn.close()

    response = client.get('/vehicle')
    assert response.status_code == 200
    vehicles = response.get_json()
    assert isinstance(vehicles, list)
    assert len(vehicles) == 0 

# Test retrieving a vehicle by its VIN
def test_get_vehicle_by_vin(client):
    vin = "1HGCM82633A123456"
    response = client.get(f'/vehicle/{vin}')
    assert response.status_code == 200
    vehicle = response.get_json()
    assert vehicle['vin'] == vin

# Test retrieving a vehicle by a non-existent VIN
def test_get_vehicle_by_nonexistent_vin(client):
    vin = "NONEXISTENTVIN123"
    response = client.get(f'/vehicle/{vin}')
    assert response.status_code == 404

# Test updating an existing vehicle
def test_update_vehicle(client):
    vin = "1HGCM82633A123456"
    updated_data = {
        "manufacturer_name": "Honda Updated",
        "description": "An updated reliable car",
        "horse_power": 210,
        "model_name": "Civic",
        "model_year": 2023,
        "purchase_price": 26000.00,
        "fuel_type": "Gasoline"
    }
    response = client.put(f'/vehicle/{vin}', json=updated_data)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Vehicle updated successfully!"

# Test updating a vehicle with an invalid field
def test_update_vehicle_invalid_field(client):
    vin = "1HGCM82633A123456"
    updated_data = {
        "manufacturer_name": "Honda Updated",
        "description": "Updated car with invalid horsepower",
        "horse_power": -100,  # Invalid value
        "model_name": "Civic",
        "model_year": 2023,
        "purchase_price": 26000.00,
        "fuel_type": "Gasoline"
    }
    response = client.put(f'/vehicle/{vin}', json=updated_data)
    assert response.status_code == 422
    assert "Invalid horse_power" in response.get_json()["message"]

# Test deleting a vehicle by its VIN
def test_delete_vehicle(client):
    vin = "1HGCM82633A123456"
    response = client.delete(f'/vehicle/{vin}')
    assert response.status_code == 204

# Test deleting a vehicle and verifying it no longer exists
def delete_then_get_vehicle(client):
    vin = "1HGCM82633A123456"
    response = client.delete(f'/vehicle/{vin}')
    assert response.status_code == 204
    response = client.get(f'/vehicle/{vin}')
    assert response.status_code == 404

# Test deleting a vehicle with a non-existent VIN
def test_delete_vehicle_nonexistent_vin(client):
    vin = "NONEXISTENTVIN123"
    response = client.delete(f'/vehicle/{vin}')
    assert response.status_code == 404
    assert "Vehicle not found" in response.get_json()["message"]