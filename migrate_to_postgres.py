#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL for Render deployment
"""
import sqlite3
import psycopg2
import os
import sys

def migrate_data(sqlite_path, postgres_url):
    """Copy data from SQLite to PostgreSQL"""
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(postgres_url)
    pg_cursor = pg_conn.cursor()
    
    print("Connected to databases")
    
    # Migrate categories
    print("Migrating categories...")
    categories = sqlite_conn.execute("SELECT * FROM categories").fetchall()
    for cat in categories:
        pg_cursor.execute(
            "INSERT INTO categories (id, name, slug, description) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (cat['id'], cat['name'], cat['slug'], cat['description'])
        )
    
    # Migrate plaques
    print("Migrating plaques...")
    plaques = sqlite_conn.execute("SELECT * FROM plaques").fetchall()
    for plaque in plaques:
        pg_cursor.execute("""
            INSERT INTO plaques (id, title, description, inscription, latitude, longitude, 
                               address, year_erected, organization, source_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            plaque['id'], plaque['title'], plaque['description'], plaque.get('inscription'),
            plaque['latitude'], plaque['longitude'], plaque.get('address'),
            plaque.get('year_erected'), plaque.get('organization'), plaque.get('source_url'),
            plaque.get('created_at'), plaque.get('updated_at')
        ))
    
    # Migrate plaque_categories
    print("Migrating plaque-category relationships...")
    relations = sqlite_conn.execute("SELECT * FROM plaque_categories").fetchall()
    for rel in relations:
        pg_cursor.execute(
            "INSERT INTO plaque_categories (plaque_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (rel['plaque_id'], rel['category_id'])
        )
    
    # Migrate images
    print("Migrating images...")
    images = sqlite_conn.execute("SELECT * FROM images").fetchall()
    for img in images:
        pg_cursor.execute("""
            INSERT INTO images (id, plaque_id, url, caption, photographer, year_taken, display_order, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            img['id'], img['plaque_id'], img['url'], img.get('caption'),
            img.get('photographer'), img.get('year_taken'), img.get('display_order', 0),
            img.get('created_at')
        ))
    
    pg_conn.commit()
    print("Migration complete!")
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    sqlite_path = os.getenv("SQLITE_PATH", "blue_plaques.db")
    postgres_url = os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite database not found at {sqlite_path}")
        sys.exit(1)
    
    migrate_data(sqlite_path, postgres_url)
