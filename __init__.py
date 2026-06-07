import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ.get("DB_NAME", "kitchendump"),
    user=os.environ.get("DB_USER", "admin"),
    password=os.environ.get("DB_PASSWORD", "password"),
    host="127.0.0.1",
    port=5432
)
db_cursor = conn.cursor(cursor_factory=RealDictCursor)