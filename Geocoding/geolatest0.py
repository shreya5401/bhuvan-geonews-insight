import psycopg2
from geopy.geocoders import Nominatim

# Define database connection parameters
DB_NAME = "news"
DB_USER = "postgres"
DB_PASSWORD = "shiro123"
DB_HOST = "localhost"
DB_PORT = "5432"  # Replace with the actual port number of your PostgreSQL server

# Function to check if the geocode column exists in news_articles table
def check_geocode_column():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Check if the geocode column exists
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scraped_db' AND column_name = 'geocode')")
        exists = cur.fetchone()[0]

        # If geocode column doesn't exist, create it
        if not exists:
            cur.execute("ALTER TABLE scraped_db ADD COLUMN geocode VARCHAR(255)")

        # Commit the transaction
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error checking/creating geocode column: {e}")

# Function to fetch most frequent from the database
def fetch_most_frequent():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute a query to fetch id and most_frequent columns where geocode is NULL
        cur.execute("SELECT id, most_frequent FROM scraped_db WHERE geocode IS NULL")

        # Retrieve query results
        rows = cur.fetchall()

        # Close communication with the database
        cur.close()
        conn.close()

        return rows

    except Exception as e:
        print(f"Error fetching most frequent: {e}")
        return []

# Function to update geocode in the database
def update_geocode(place_id, geocode):
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute update query to set geocode for the given place_id
        cur.execute("UPDATE scraped_db SET geocode = %s WHERE id = %s", (geocode, place_id))

        # Commit the transaction
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error updating geocode: {e}")

# Function to check if a location is in India using geopy
def is_location_in_india(location_name):
    try:
        # Initialize geolocator
        geolocator = Nominatim(user_agent="your_app_name")
        
        # Get location information
        location = geolocator.geocode(location_name, country_codes='IN')

        return location is not None

    except Exception as e:
        print(f"Error checking location: {e}")
        return False

# Main function to fetch most frequent and update geocode
def main():
    # Check and create geocode column if it doesn't exist
    check_geocode_column()

    # Fetch most frequent from the database
    most_frequent_entries = fetch_most_frequent()
    if not most_frequent_entries:
        return

    # Initialize geolocator
    geolocator = Nominatim(user_agent="your_app_name")

    for place_id, place_name in most_frequent_entries:
        if not place_name:  # Skip if place_name is empty or None
            update_geocode(place_id, None)
            print(f"No entry for place_id {place_id}, leaving geocode empty.")
            continue

        try:
            # Check if the location is in India
            if is_location_in_india(place_name):
                # Get the location
                location = geolocator.geocode(place_name)
                if location:
                    geocode = f"{location.latitude}, {location.longitude}"
                    # Update the geocode in the database
                    update_geocode(place_id, geocode)
                    print(f"Updated geocode for {place_name}: {geocode}")
                else:
                    update_geocode(place_id, None)
                    print(f"Could not geocode {place_name}, leaving geocode empty.")
            else:
                update_geocode(place_id, None)
                print(f"{place_name} is not in India, leaving geocode empty.")
        
        except Exception as e:
            update_geocode(place_id, None)
            print(f"Error geocoding {place_name}: {e}, leaving geocode empty.")

if __name__ == "__main__":
    main()
