#!/usr/bin/env python3
"""
Data Migration Script: SQLite → PostgreSQL + R2
Migrates 386 plaques + 1,157 images from prototype to v2.0
"""
import sqlite3
import json
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

# Configuration
SQLITE_DB = "blue_plaques.db"
IMAGES_DIR = "static/images"
PG_URL = os.getenv("DATABASE_URL")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# Initialize R2 client
s3 = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def extract_plaques():
    """Extract plaques from SQLite"""
    print("📦 Extracting plaques from SQLite...")
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    
    plaques = conn.execute('''
        SELECT id, title, url, image_url, location, description,
               local_image_path, geo_location, address, categories
        FROM plaques
        WHERE geo_location IS NOT NULL
    ''').fetchall()
    
    result = []
    for p in plaques:
        try:
            geo = json.loads(p['geo_location'])
            result.append({
                'old_id': p['id'],
                'title': p['title'],
                'description': p['description'],
                'address': p['address'],
                'lat': float(geo['lat']),
                'lon': float(geo['lon']),
                'source_url': p['url'],
                'main_image': p['local_image_path'],
                'categories': p['categories'].split(', ') if p['categories'] else []
            })
        except Exception as e:
            print(f"⚠️  Skipping plaque {p['id']}: {e}")
    
    conn.close()
    print(f"✅ Extracted {len(result)} plaques")
    return result

def extract_images():
    """Extract images from SQLite"""
    print("📦 Extracting images from SQLite...")
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    
    images = conn.execute('''
        SELECT id, plaque_id, image_url, local_image_path, 
               image_title, image_order
        FROM plaque_images
        ORDER BY plaque_id, image_order
    ''').fetchall()
    
    result = []
    for img in images:
        if img['local_image_path']:
            result.append({
                'old_id': img['id'],
                'old_plaque_id': img['plaque_id'],
                'local_path': img['local_image_path'],
                'caption': img['image_title'],
                'order': img['image_order'] or 0
            })
    
    conn.close()
    print(f"✅ Extracted {len(result)} images")
    return result

def upload_to_r2(local_path):
    """Upload image to R2 and return public URL"""
    if not local_path or not os.path.exists(local_path):
        return None
    
    filename = os.path.basename(local_path)
    
    try:
        with open(local_path, 'rb') as f:
            s3.put_object(
                Bucket=R2_BUCKET,
                Key=filename,
                Body=f,
                ContentType='image/jpeg'
            )
        return f"{R2_PUBLIC_URL}/{filename}"
    except Exception as e:
        print(f"⚠️  Failed to upload {filename}: {e}")
        return None

def migrate_plaques(plaques):
    """Insert plaques into PostgreSQL"""
    print("🚀 Migrating plaques to PostgreSQL...")
    conn = psycopg2.connect(PG_URL)
    cur = conn.cursor()
    
    id_mapping = {}
    
    for p in plaques:
        cur.execute('''
            INSERT INTO plaques (title, description, latitude, longitude, location, address, source_url)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
            RETURNING id
        ''', (
            p['title'],
            p['description'],
            p['lat'],
            p['lon'],
            p['lon'],
            p['lat'],
            p['address'],
            p['source_url']
        ))
        new_id = cur.fetchone()[0]
        id_mapping[p['old_id']] = new_id
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Migrated {len(plaques)} plaques")
    return id_mapping

def migrate_images(images, id_mapping):
    """Upload images to R2 and insert records into PostgreSQL"""
    print("🚀 Migrating images to R2 and PostgreSQL...")
    conn = psycopg2.connect(PG_URL)
    cur = conn.cursor()
    
    uploaded = 0
    failed = 0
    
    for img in images:
        new_plaque_id = id_mapping.get(img['old_plaque_id'])
        if not new_plaque_id:
            failed += 1
            continue
        
        # Upload to R2
        url = upload_to_r2(img['local_path'])
        if not url:
            failed += 1
            continue
        
        # Insert into PostgreSQL
        cur.execute('''
            INSERT INTO images (plaque_id, url, caption, display_order)
            VALUES (%s, %s, %s, %s)
        ''', (new_plaque_id, url, img['caption'], img['order']))
        
        uploaded += 1
        if uploaded % 100 == 0:
            print(f"  📤 Uploaded {uploaded}/{len(images)} images...")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Migrated {uploaded} images ({failed} failed)")
    return uploaded

def verify_migration():
    """Verify migration success"""
    print("🔍 Verifying migration...")
    conn = psycopg2.connect(PG_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM plaques")
    plaque_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM images")
    image_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    print(f"✅ Verification complete:")
    print(f"   Plaques: {plaque_count}")
    print(f"   Images: {image_count}")
    
    return plaque_count, image_count

def main():
    print("=" * 60)
    print("Blue Plaques Data Migration")
    print("SQLite → PostgreSQL + CloudFlare R2")
    print("=" * 60)
    
    # Extract
    plaques = extract_plaques()
    images = extract_images()
    
    # Migrate
    id_mapping = migrate_plaques(plaques)
    migrate_images(images, id_mapping)
    
    # Verify
    plaque_count, image_count = verify_migration()
    
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print(f"   {plaque_count} plaques migrated")
    print(f"   {image_count} images migrated")
    print("=" * 60)

if __name__ == "__main__":
    main()
