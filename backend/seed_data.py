#!/usr/bin/env python3
"""Seed database with sample plaques for testing"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

SAMPLE_PLAQUES = [
    {
        "title": "Desmond Tutu House",
        "description": "Former residence of Archbishop Desmond Tutu, Nobel Peace Prize laureate and anti-apartheid activist.",
        "address": "Orlando West, Soweto, Johannesburg",
        "lat": -26.2381,
        "lon": 27.8974,
        "categories": ["Political", "Religious"]
    },
    {
        "title": "Nelson Mandela House",
        "description": "The modest home where Nelson Mandela lived before his imprisonment. Now a museum.",
        "address": "8115 Vilakazi Street, Orlando West, Soweto",
        "lat": -26.2389,
        "lon": 27.8967,
        "categories": ["Political", "Historical"]
    },
    {
        "title": "Constitution Hill",
        "description": "Former prison complex, now home to South Africa's Constitutional Court.",
        "address": "11 Kotze Street, Braamfontein, Johannesburg",
        "lat": -26.1867,
        "lon": 28.0364,
        "categories": ["Political", "Historical", "Legal"]
    },
    {
        "title": "Castle of Good Hope",
        "description": "The oldest surviving colonial building in South Africa, built 1666-1679.",
        "address": "Corner of Buitenkant and Strand Streets, Cape Town",
        "lat": -33.9275,
        "lon": 18.4289,
        "categories": ["Historical", "Military", "Colonial"]
    },
    {
        "title": "Robben Island",
        "description": "Island prison where Nelson Mandela was held for 18 years. Now a UNESCO World Heritage Site.",
        "address": "Robben Island, Table Bay, Cape Town",
        "lat": -33.8070,
        "lon": 18.3700,
        "categories": ["Political", "Historical", "UNESCO"]
    }
]

def seed():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    print("🌱 Seeding database...")
    
    # Create categories
    categories = {}
    for cat_name in ["Political", "Religious", "Historical", "Legal", "Military", "Colonial", "UNESCO"]:
        slug = cat_name.lower()
        cur.execute(
            "INSERT INTO categories (name, slug) VALUES (%s, %s) ON CONFLICT (slug) DO UPDATE SET name = %s RETURNING id",
            (cat_name, slug, cat_name)
        )
        categories[cat_name] = cur.fetchone()[0]
    
    conn.commit()
    print(f"✓ Created {len(categories)} categories")
    
    # Insert plaques
    for plaque in SAMPLE_PLAQUES:
        cur.execute('''
            INSERT INTO plaques (title, description, address, latitude, longitude, location)
            VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            RETURNING id
        ''', (plaque["title"], plaque["description"], plaque["address"], 
              plaque["lat"], plaque["lon"], plaque["lon"], plaque["lat"]))
        
        plaque_id = cur.fetchone()[0]
        
        # Link categories
        for cat_name in plaque["categories"]:
            cur.execute(
                "INSERT INTO plaque_categories (plaque_id, category_id) VALUES (%s, %s)",
                (plaque_id, categories[cat_name])
            )
        
        print(f"✓ {plaque['title']}")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n✅ Seeded {len(SAMPLE_PLAQUES)} plaques")

if __name__ == "__main__":
    seed()
