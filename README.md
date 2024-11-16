# Vehicle Management API

A simple Flask API to manage vehicles, built as part of Apollo's coding exercise.

## Features
- **Initialize Database:** `/init` (GET)
- **List Vehicles:** `/vehicle` (GET)
- **Add Vehicle:** `/vehicle` (POST)
- **Get Vehicle by VIN:** `/vehicle/<vin>` (GET)
- **Update Vehicle:** `/vehicle/<vin>` (PUT)
- **Delete Vehicle:** `/vehicle/<vin>` (DELETE)

---

## Requirements
- Python 3.10+
- PostgreSQL 12+
- Virtual environment

---

## Installation

1. **Clone the Repository**  
   Open your terminal and clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. **Set Up a Virtual Environment**  
   Create and activate a virtual environment:
   ```bash
    python3 -m venv venv
    source venv/bin/activat

3. **Install Dependencies**  
   Install the required Python dependencies::
   ```bash
    pip install -r requirements.txt

4. **Initialize the Database**  
  Create the database schema by running:
   ```bash
   python init_db.py

---

## Running the Application

1. **Start the Server** 
   ```bash
   flask run --port=5000
2. **Access the API**
   Open your browser or Postman and navigate to: 
   http://localhost:5000/insertcommandhere

---

## Running Tests

1. **Run Tests**
    To run all tests:
   ```bash
   pytest
   
---

## Example Data

Here is an example JSON payload for creating or updating a vehicle:
    To run all tests:
   ```json
   {
  "vin": "1HGCM82633A123456",
  "manufacturer_name": "Honda",
  "description": "A reliable car",
  "horse_power": 200,
  "model_name": "Civic",
  "model_year": 2022,
  "purchase_price": 25000.00,
  "fuel_type": "Gasoline"
}
