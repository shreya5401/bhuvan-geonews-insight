import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

# Database connection parameters
DB_NAME = "news"
DB_USER = "postgres"
DB_PASSWORD = "shiro123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected successfully")
        return conn
    except psycopg2.OperationalError as e:
        print(f"An error occurred: {e}")
        return None

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scraped_db (
                id SERIAL PRIMARY KEY,
                title TEXT,
                publication_date TIMESTAMP,
                content TEXT,
                url TEXT UNIQUE
            );
        """)
        conn.commit()

def insert_article(conn, title, publication_date, content, url):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO scraped_db (title, publication_date, content, url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
            """, (title, publication_date, content, url))
            conn.commit()
    except psycopg2.Error as e:
        conn.rollback()  # Rollback the transaction on error
        print(f"Error inserting article into database: {e}")

def scrape_article(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to load page {url}")
        
        article_soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_tag = article_soup.find('h1')
        if not title_tag:
            return None, None, None
        title = title_tag.get_text(strip=True)

        # Extract publication date
        publication_date = None
        publication_date_tag = article_soup.find(['meta'], {'itemprop': 'datePublished'}) or \
                               article_soup.find(['meta'], {'name': 'publish-date'}) or \
                               article_soup.find(['meta'], {'property': 'article:published_time'})
        if publication_date_tag:
            publication_date = publication_date_tag.get('content')
            publication_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00')) if publication_date else None

        # Extract content
        paragraphs = article_soup.find_all('p')
        content = ' '.join(p.get_text(strip=True) for p in paragraphs)

        return title, publication_date, content
    except requests.exceptions.RequestException as e:
        print(f"Request error extracting data from {url}: {e}")
        return None, None, None
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None, None, None

def scrape_section(url, site):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to load page {url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')

        article_links = []
        
        if site == 'Indian Express':
            # Extract article links for Indian Express
            articles = soup.find_all('div', class_='articles')
            for article in articles:
                a_tag = article.find('a', href=True)
                if a_tag:
                    article_links.append(a_tag['href'])
        elif site == 'NDTV':
            # Extract article links for NDTV
            articles = soup.find_all('div', class_='news_Itm')
            for article in articles:
                a_tag = article.find('a', href=True)
                if a_tag:
                    article_links.append(a_tag['href'])
        elif site == 'India TV':
            # Extract article links for India TV
            articles = soup.find_all('h3', class_='titel')
            # articles = soup.find_all('li', class_='p_news eventTracking')
            for article in articles:
                a_tag = article.find('a', href=True)
                if a_tag:
                    article_links.append(a_tag['href'])
            # Extract article links for India TV
            articles = soup.find_all('h3', class_='title')
            # articles = soup.find_all('li', class_='p_news eventTracking')
            for article in articles:
                a_tag = article.find('a', href=True)
                if a_tag:
                    article_links.append(a_tag['href'])
        elif site == 'India Today':
            # Extract article links for India Today
            articles = soup.find_all('article', class_='B1S3_story__card__A_fhi')
            for article in articles:
                a_tag = article.find('a', href=True)
                if a_tag:
                    article_links.append('https://www.indiatoday.in/india'+'/'+a_tag['href'])

        return article_links
    except Exception as e:
        print(f"Error scraping section: {e}")
        return []

def main():
    news_sites = {
        'Indian Express': 'https://indianexpress.com/section/india/',
        'NDTV': 'https://www.ndtv.com/india',
        'India TV': 'https://www.indiatvnews.com/india',
        'India Today': 'https://www.indiatoday.in/india'
    }
    
    conn = None
    try:
        conn = connect_to_db()
        if conn is not None:
            create_table(conn)
            for site, url in news_sites.items():
                article_links = scrape_section(url, site)
                unique_urls = set()
                for link in article_links:
                    if link not in unique_urls:
                        unique_urls.add(link)
                        try:
                            title, publication_date, content = scrape_article(link)
                            if title and publication_date and content:
                                insert_article(conn, title, publication_date, content, link)
                                print(f"Article '{title}' from site '{site}' inserted successfully")
                        except Exception as e:
                            print(f"Failed to scrape article at {link}: {e}")
            print("All articles inserted successfully")
        else:
            print("Failed to connect to the database")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
