import pytest
from app import app

@pytest.fixture
def client():
    # Use Flask's test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_init_db(client):
    response = client.get('/init')
    assert response.status_code == 200
    assert response.get_json()['message'] == "Table created successfully!"

def test_create_vehicle(client):
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
    assert response.status_code == 201
    assert response.get_json()["message"] == "Vehicle created successfully!"

def test_get_vehicles(client):
    response = client.get('/vehicle')
    assert response.status_code == 200
    vehicles = response.get_json()
    assert isinstance(vehicles, list)  # Ensure the response is a list
    assert len(vehicles) >= 1  # At least one vehicle should exist

def test_get_vehicle_by_vin(client):
    vin = "1HGCM82633A123456"
    response = client.get(f'/vehicle/{vin}')
    assert response.status_code == 200
    vehicle = response.get_json()
    assert vehicle['vin'] == vin

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

def test_delete_vehicle(client):
    vin = "1HGCM82633A123456"
    response = client.delete(f'/vehicle/{vin}')
    assert response.status_code == 204
