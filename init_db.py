import psycopg2

# Database connection
def get_db_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

# Initialize the database
def init_db():
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
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
