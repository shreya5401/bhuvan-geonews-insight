import psycopg2
from collections import Counter

# Database connection parameters
db_params = {
    'dbname': 'news',
    'user': 'postgres',
    'password': 'shiro123',
    'host': 'localhost',
    'port': '5432'
}

def get_most_frequent(places):
    if not places or places == '{}':
        return None
    counter = Counter(places)
    most_common = counter.most_common()
    max_frequency = most_common[0][1]
    candidates = [place for place, count in most_common if count == max_frequency]
    return candidates[0] if candidates else None

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    # Check if the 'most_frequent' column exists, if not, create it
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scraped_db' AND column_name='most_frequent') THEN
                ALTER TABLE scraped_db ADD COLUMN most_frequent TEXT;
            END IF;
        END
        $$;
    """)
    
    # Select only rows where 'most_frequent' is NULL
    cur.execute("SELECT id, places FROM scraped_db WHERE most_frequent IS NULL")
    rows = cur.fetchall()

    # Update each row with the most frequent place or delete the row if most_frequent is None
    for row in rows:
        row_id, places = row
        if places is None:
            places = []
        most_frequent = get_most_frequent(places)
        if most_frequent is None:
            cur.execute("DELETE FROM scraped_db WHERE id = %s", (row_id,))
            print(f"Deleted row {row_id} because most_frequent is NULL")
        else:
            cur.execute("UPDATE scraped_db SET most_frequent = %s WHERE id = %s", (most_frequent, row_id))
            print(f"Updated row {row_id} with most frequent place: {most_frequent}")

    # Commit the changes
    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
