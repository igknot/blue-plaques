# Data Migration Plan

**Critical**: This migration preserves all 386 plaques and 1,157 images without data loss.

---

## Migration Overview

```
SQLite Database (blue_plaques.db)
        ↓
Extract & Transform
        ↓
PostgreSQL + R2 Storage
```

**Timeline**: 1 day  
**Risk**: LOW (read-only migration, original data preserved)

---

## Phase 1: Data Extraction

### Extract Plaques

```python
# scripts/migrate_data.py
import sqlite3
import json
from typing import List, Dict

def extract_plaques() -> List[Dict]:
    conn = sqlite3.connect('blue_plaques.db')
    conn.row_factory = sqlite3.Row
    
    plaques = conn.execute('''
        SELECT id, title, url, image_url, location, description,
               local_image_path, geo_location, address, categories
        FROM plaques
        WHERE geo_location IS NOT NULL
    ''').fetchall()
    
    result = []
    for plaque in plaques:
        geo = json.loads(plaque['geo_location'])
        result.append({
            'old_id': plaque['id'],
            'title': plaque['title'],
            'description': plaque['description'],
            'address': plaque['address'],
            'lat': float(geo['lat']),
            'lon': float(geo['lon']),
            'heritage_portal_url': plaque['url'],
            'main_image_path': plaque['local_image_path'],
            'categories': plaque['categories'].split(', ') if plaque['categories'] else []
        })
    
    conn.close()
    return result

# Extract: 386 plaques
plaques = extract_plaques()
print(f"Extracted {len(plaques)} plaques")
```

### Extract Images

```python
def extract_images() -> List[Dict]:
    conn = sqlite3.connect('blue_plaques.db')
    conn.row_factory = sqlite3.Row
    
    images = conn.execute('''
        SELECT id, plaque_id, image_url, local_image_path, 
               image_title, image_order
        FROM plaque_images
        ORDER BY plaque_id, image_order
    ''').fetchall()
    
    result = []
    for img in images:
        if img['local_image_path'] or img['image_url']:
            result.append({
                'old_id': img['id'],
                'old_plaque_id': img['plaque_id'],
                'local_path': img['local_image_path'],
                'url': img['image_url'],
                'title': img['image_title'],
                'order': img['image_order']
            })
    
    conn.close()
    return result

# Extract: 1,157 images
images = extract_images()
print(f"Extracted {len(images)} images")
```

### Extract Categories

```python
def extract_categories(plaques: List[Dict]) -> List[str]:
    categories = set()
    for plaque in plaques:
        categories.update(plaque['categories'])
    return sorted(categories)

# Extract: ~20 unique categories
categories = extract_categories(plaques)
print(f"Extracted {len(categories)} categories")
```

---

## Phase 2: Image Migration to R2

### Upload Images to CloudFlare R2

```python
import boto3
from PIL import Image
import io
import os
from pathlib import Path

# R2 client (S3-compatible)
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('R2_SECRET_KEY')
)

BUCKET = 'blue-plaques'
CDN_BASE = 'https://cdn.blueplaques.co.za'

def optimize_image(image_path: str) -> bytes:
    """Optimize image: resize, compress, convert to WebP"""
    img = Image.open(image_path)
    
    # Resize if too large
    max_size = (1200, 1200)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Convert to WebP
    buffer = io.BytesIO()
    img.save(buffer, format='WEBP', quality=85, optimize=True)
    return buffer.getvalue()

def upload_image(local_path: str, plaque_uuid: str, image_uuid: str) -> Dict:
    """Upload image to R2 and return metadata"""
    if not os.path.exists(local_path):
        print(f"Warning: {local_path} not found")
        return None
    
    # Optimize image
    image_data = optimize_image(local_path)
    
    # Generate R2 key
    storage_key = f"plaques/{plaque_uuid}/{image_uuid}.webp"
    
    # Upload to R2
    s3.put_object(
        Bucket=BUCKET,
        Key=storage_key,
        Body=image_data,
        ContentType='image/webp',
        CacheControl='public, max-age=31536000'  # 1 year
    )
    
    # Get image dimensions
    img = Image.open(io.BytesIO(image_data))
    width, height = img.size
    
    return {
        'storage_key': storage_key,
        'cdn_url': f"{CDN_BASE}/{storage_key}",
        'width': width,
        'height': height,
        'file_size': len(image_data)
    }

# Migrate all images
def migrate_images(images: List[Dict], plaque_mapping: Dict) -> List[Dict]:
    """Migrate all images to R2"""
    migrated = []
    
    for i, img in enumerate(images, 1):
        print(f"Migrating image {i}/{len(images)}: {img['local_path']}")
        
        # Get new plaque UUID
        plaque_uuid = plaque_mapping[img['old_plaque_id']]
        image_uuid = str(uuid.uuid4())
        
        # Upload to R2
        metadata = upload_image(img['local_path'], plaque_uuid, image_uuid)
        
        if metadata:
            migrated.append({
                'id': image_uuid,
                'plaque_id': plaque_uuid,
                'title': img['title'],
                'display_order': img['order'],
                **metadata
            })
    
    print(f"Successfully migrated {len(migrated)}/{len(images)} images")
    return migrated
```

---

## Phase 3: Database Migration

### Create PostgreSQL Schema

```sql
-- Run schema from REBUILD_SPECIFICATION.md
-- Creates: plaques, categories, plaque_categories, images, users, etc.
```

### Insert Categories

```python
import asyncpg
import asyncio

async def insert_categories(categories: List[str]):
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    category_mapping = {}
    for cat in categories:
        slug = cat.lower().replace(' ', '-').replace(',', '')
        row = await conn.fetchrow('''
            INSERT INTO categories (name, slug)
            VALUES ($1, $2)
            RETURNING id
        ''', cat, slug)
        category_mapping[cat] = row['id']
    
    await conn.close()
    return category_mapping

# Insert: 20 categories
category_mapping = asyncio.run(insert_categories(categories))
```

### Insert Plaques

```python
async def insert_plaques(plaques: List[Dict], category_mapping: Dict):
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    plaque_mapping = {}  # old_id -> new_uuid
    
    for plaque in plaques:
        # Insert plaque
        row = await conn.fetchrow('''
            INSERT INTO plaques (
                title, description, address, location, heritage_portal_url
            ) VALUES (
                $1, $2, $3, ST_SetSRID(ST_MakePoint($4, $5), 4326), $6
            )
            RETURNING id
        ''', 
            plaque['title'],
            plaque['description'],
            plaque['address'],
            plaque['lon'],
            plaque['lat'],
            plaque['heritage_portal_url']
        )
        
        plaque_uuid = row['id']
        plaque_mapping[plaque['old_id']] = plaque_uuid
        
        # Insert category associations
        for cat_name in plaque['categories']:
            cat_id = category_mapping.get(cat_name)
            if cat_id:
                await conn.execute('''
                    INSERT INTO plaque_categories (plaque_id, category_id)
                    VALUES ($1, $2)
                ''', plaque_uuid, cat_id)
    
    await conn.close()
    return plaque_mapping

# Insert: 386 plaques
plaque_mapping = asyncio.run(insert_plaques(plaques, category_mapping))
```

### Insert Images

```python
async def insert_images(images: List[Dict]):
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    for img in images:
        await conn.execute('''
            INSERT INTO images (
                id, plaque_id, storage_key, cdn_url, title,
                display_order, width, height, file_size
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ''',
            img['id'],
            img['plaque_id'],
            img['storage_key'],
            img['cdn_url'],
            img['title'],
            img['display_order'],
            img['width'],
            img['height'],
            img['file_size']
        )
    
    await conn.close()

# Insert: 1,157 images
asyncio.run(insert_images(migrated_images))
```

---

## Phase 4: Verification

### Verify Data Integrity

```python
async def verify_migration():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Count plaques
    plaque_count = await conn.fetchval('SELECT COUNT(*) FROM plaques')
    print(f"✓ Plaques: {plaque_count} (expected 386)")
    assert plaque_count == 386
    
    # Count images
    image_count = await conn.fetchval('SELECT COUNT(*) FROM images')
    print(f"✓ Images: {image_count} (expected 1,157)")
    assert image_count == 1157
    
    # Count categories
    category_count = await conn.fetchval('SELECT COUNT(*) FROM categories')
    print(f"✓ Categories: {category_count}")
    
    # Verify all plaques have location
    no_location = await conn.fetchval(
        'SELECT COUNT(*) FROM plaques WHERE location IS NULL'
    )
    print(f"✓ Plaques without location: {no_location} (expected 0)")
    assert no_location == 0
    
    # Verify all images have CDN URLs
    no_url = await conn.fetchval(
        'SELECT COUNT(*) FROM images WHERE cdn_url IS NULL'
    )
    print(f"✓ Images without CDN URL: {no_url} (expected 0)")
    assert no_url == 0
    
    await conn.close()
    print("\n✅ Migration verification passed!")

asyncio.run(verify_migration())
```

### Sample Data Check

```python
async def sample_check():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get Tutu House
    tutu = await conn.fetchrow('''
        SELECT p.*, 
               ST_Y(p.location::geometry) as lat,
               ST_X(p.location::geometry) as lon,
               array_agg(c.name) as categories
        FROM plaques p
        LEFT JOIN plaque_categories pc ON p.id = pc.plaque_id
        LEFT JOIN categories c ON pc.category_id = c.id
        WHERE p.title ILIKE '%tutu%'
        GROUP BY p.id
    ''')
    
    print(f"\nSample: {tutu['title']}")
    print(f"  Location: {tutu['lat']}, {tutu['lon']}")
    print(f"  Categories: {tutu['categories']}")
    
    # Get images
    images = await conn.fetch('''
        SELECT * FROM images WHERE plaque_id = $1 ORDER BY display_order
    ''', tutu['id'])
    
    print(f"  Images: {len(images)}")
    for img in images:
        print(f"    - {img['cdn_url']}")
    
    await conn.close()

asyncio.run(sample_check())
```

---

## Complete Migration Script

```python
#!/usr/bin/env python3
"""
Complete data migration script
Migrates from SQLite to PostgreSQL + R2
"""

import asyncio
import sys

async def main():
    print("=" * 60)
    print("Blue Plaques Data Migration")
    print("=" * 60)
    
    # Phase 1: Extract
    print("\n[1/4] Extracting data from SQLite...")
    plaques = extract_plaques()
    images = extract_images()
    categories = extract_categories(plaques)
    print(f"  ✓ {len(plaques)} plaques")
    print(f"  ✓ {len(images)} images")
    print(f"  ✓ {len(categories)} categories")
    
    # Phase 2: Migrate images
    print("\n[2/4] Migrating images to R2...")
    # First insert plaques to get UUIDs
    category_mapping = await insert_categories(categories)
    plaque_mapping = await insert_plaques(plaques, category_mapping)
    
    # Now migrate images
    migrated_images = migrate_images(images, plaque_mapping)
    print(f"  ✓ {len(migrated_images)} images uploaded")
    
    # Phase 3: Insert images
    print("\n[3/4] Inserting image records...")
    await insert_images(migrated_images)
    print(f"  ✓ {len(migrated_images)} records inserted")
    
    # Phase 4: Verify
    print("\n[4/4] Verifying migration...")
    await verify_migration()
    await sample_check()
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Test API endpoints")
    print("  2. Verify images load in browser")
    print("  3. Keep SQLite backup for 30 days")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
```

---

## Rollback Plan

If migration fails:

```bash
# 1. Drop PostgreSQL tables
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 2. Delete R2 bucket contents
aws s3 rm s3://blue-plaques --recursive --endpoint-url=$R2_ENDPOINT

# 3. Original SQLite database remains untouched
# Can restart migration or continue using old system
```

---

## Post-Migration Checklist

- [ ] All 386 plaques migrated
- [ ] All 1,157 images uploaded to R2
- [ ] All images accessible via CDN
- [ ] All categories created
- [ ] Sample queries return correct data
- [ ] API endpoints return migrated data
- [ ] Frontend displays migrated data
- [ ] Keep SQLite backup for 30 days
- [ ] Document migration date and results
