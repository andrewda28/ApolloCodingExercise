import psycopg2

conn = psycopg2.connect(database = 'postgres', host = 'localhost', user= "postgres", password = 'password', port = "5432")
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

conn.commit()  # Commit changes        to the database
print("Table created successfully!")

# Close the cursor and connection
cur.close()
conn.close()