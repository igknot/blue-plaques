#!/usr/bin/env python3
"""Local migration: SQLite → PostgreSQL (no cloud storage)"""
import sqlite3
import json
import psycopg2
import os

SQLITE_DB = "blue_plaques.db"
PG_URL = os.getenv("DATABASE_URL")

def migrate():
    # Connect to both databases
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(PG_URL)
    pg_cur = pg_conn.cursor()
    
    print("🚀 Starting local migration...")
    
    # Extract categories
    print("\n[1/3] Extracting categories...")
    categories_set = set()
    for row in sqlite_conn.execute("SELECT categories FROM plaques WHERE categories IS NOT NULL"):
        if row['categories']:
            categories_set.update([c.strip() for c in row['categories'].split(',')])
    
    # Insert categories
    category_map = {}
    for cat_name in sorted(categories_set):
        slug = cat_name.lower().replace(' ', '-').replace(',', '')
        pg_cur.execute(
            "INSERT INTO categories (name, slug) VALUES (%s, %s) ON CONFLICT (slug) DO UPDATE SET name = %s RETURNING id",
            (cat_name, slug, cat_name)
        )
        category_map[cat_name] = pg_cur.fetchone()[0]
    
    pg_conn.commit()
    print(f"✓ Migrated {len(category_map)} categories")
    
    # Extract and insert plaques
    print("\n[2/3] Migrating plaques...")
    plaque_map = {}
    plaques = sqlite_conn.execute("""
        SELECT id, title, description, address, geo_location, categories, url
        FROM plaques 
        WHERE geo_location IS NOT NULL
    """).fetchall()
    
    for row in plaques:
        geo = json.loads(row['geo_location'])
        lat = float(geo['lat'])
        lon = float(geo['lon'])
        
        pg_cur.execute("""
            INSERT INTO plaques (title, description, address, latitude, longitude, location, source_url)
            VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
            RETURNING id
        """, (row['title'], row['description'], row['address'], lat, lon, lon, lat, row['url']))
        
        new_id = pg_cur.fetchone()[0]
        plaque_map[row['id']] = new_id
        
        # Link categories
        if row['categories']:
            for cat_name in [c.strip() for c in row['categories'].split(',')]:
                if cat_name in category_map:
                    pg_cur.execute(
                        "INSERT INTO plaque_categories (plaque_id, category_id) VALUES (%s, %s)",
                        (new_id, category_map[cat_name])
                    )
    
    pg_conn.commit()
    print(f"✓ Migrated {len(plaque_map)} plaques")
    
    # Extract and insert images
    print("\n[3/3] Migrating images...")
    images = sqlite_conn.execute("""
        SELECT plaque_id, image_url, image_title, image_order
        FROM plaque_images
        ORDER BY plaque_id, image_order
    """).fetchall()
    
    image_count = 0
    for row in images:
        if row['plaque_id'] in plaque_map and row['image_url']:
            pg_cur.execute("""
                INSERT INTO images (plaque_id, url, caption, display_order)
                VALUES (%s, %s, %s, %s)
            """, (plaque_map[row['plaque_id']], row['image_url'], row['image_title'], row['image_order']))
            image_count += 1
    
    pg_conn.commit()
    print(f"✓ Migrated {image_count} images")
    
    # Verify
    print("\n📊 Verification:")
    pg_cur.execute("SELECT COUNT(*) FROM plaques")
    print(f"  Plaques: {pg_cur.fetchone()[0]}")
    pg_cur.execute("SELECT COUNT(*) FROM categories")
    print(f"  Categories: {pg_cur.fetchone()[0]}")
    pg_cur.execute("SELECT COUNT(*) FROM images")
    print(f"  Images: {pg_cur.fetchone()[0]}")
    
    sqlite_conn.close()
    pg_cur.close()
    pg_conn.close()
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate()
