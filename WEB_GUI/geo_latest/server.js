const express = require('express');
const { Pool } = require('pg');
const app = express();
const port = 3000;

const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'news',
  password: 'shiro123',
  port: 5432,
});

app.use(express.static('public'));

app.get('/api/locations', async (req, res) => {
  try {
    const result = await pool.query('SELECT title, publication_date, most_frequent, geocode, url FROM scraped_db WHERE geocode IS NOT NULL AND sentiment = 1;');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database query error' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});