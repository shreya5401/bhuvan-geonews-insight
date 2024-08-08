import spacy
import psycopg2

# Load custom-trained SpaCy model
nlp = spacy.load(r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\NLP_Places\Model\model-best')

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="news",
    user="postgres",
    password="shiro123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Check if the places column exists, if not, create it
cursor.execute("""
    DO
    $do$
    BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scraped_db' AND column_name = 'places') THEN
        ALTER TABLE scraped_db ADD COLUMN places TEXT[];
    END IF;
    END
    $do$
""")

# Retrieve data from PostgreSQL database
cursor.execute("SELECT id, content FROM scraped_db")
rows = cursor.fetchall()

# Process text with SpaCy and extract Indian cities
for article_id, content in rows:
    doc = nlp(content)
    indian_cities = [ent.text for ent in doc.ents if ent.label_ == "CITY"]

    # Update database with extracted places
    cursor.execute(
        "UPDATE scraped_db SET places = %s WHERE id = %s",
        (indian_cities, article_id)
    )

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()