import psycopg2
from collections import Counter

# Database connection parameters
db_params = {
    'dbname': 'news',
    'user': 'postgres',
    'password': 'NKarwal',
    'host': 'localhost',
    'port': '5432'
}

def get_most_frequent(places):
    if not places or places == '{}':
        return 'Delhi'
    counter = Counter(places)
    most_common = counter.most_common()
    max_frequency = most_common[0][1]
    candidates = [place for place, count in most_common if count == max_frequency]
    return candidates[0] if candidates else 'Delhi'

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
    
    # Select all rows from the 'news_articles' table
    cur.execute("SELECT id, places FROM scraped_db")
    rows = cur.fetchall()

    # Update each row with the most frequent place
    for row in rows:
        row_id, places = row
        if places is None:
            places = []
        most_frequent = get_most_frequent(places)
        cur.execute("UPDATE scraped_db SET most_frequent = %s WHERE id = %s", (most_frequent, row_id))

    # Commit the changes
    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()

