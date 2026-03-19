# Data Models - Blue Plaques Map

**Database:** Supabase (PostgreSQL)
**Access:** PostgREST API via Supabase Python Client

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│   plaques   │───────│ plaque_categories│───────│  categories │
│             │  1:N  │                  │  N:1  │             │
│ id (PK)     │       │ plaque_id (FK)   │       │ id (PK)     │
│ title       │       │ category_id (FK) │       │ name        │
│ description │       └──────────────────┘       │ slug        │
│ latitude    │                                  │ description │
│ longitude   │                                  └─────────────┘
│ address     │
│ ...         │       ┌─────────────┐
│             │───────│   images    │
│             │  1:N  │             │
└─────────────┘       │ id (PK)     │
                      │ plaque_id   │
                      │ url         │
                      │ caption     │
                      │ ...         │
                      └─────────────┘

┌─────────────┐
│    users    │
│             │
│ id (PK)     │
│ email       │
│ hashed_pwd  │
│ is_active   │
└─────────────┘
```

## Tables

### plaques

Primary table storing heritage plaque information.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | No | auto | Primary key |
| `title` | VARCHAR(255) | No | — | Plaque title |
| `description` | TEXT | Yes | NULL | Historical description |
| `inscription` | TEXT | Yes | NULL | Text on the plaque |
| `latitude` | DECIMAL(10,8) | No | — | GPS latitude |
| `longitude` | DECIMAL(11,8) | No | — | GPS longitude |
| `address` | VARCHAR(500) | Yes | NULL | Physical address |
| `year_erected` | INTEGER | Yes | NULL | Year plaque was installed |
| `organization` | VARCHAR(255) | Yes | NULL | Installing organization |
| `source_url` | VARCHAR(500) | Yes | NULL | Heritage Portal link |
| `created_at` | TIMESTAMPTZ | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | No | NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Spatial index on `(latitude, longitude)` for nearby queries

**Constraints:**
- `latitude` between -90 and 90
- `longitude` between -180 and 180
- `title` minimum 1 character

**Statistics:**
- **386** total plaques

---

### images

Stores plaque images with metadata.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | No | auto | Primary key |
| `plaque_id` | INTEGER | No | — | Foreign key to plaques |
| `url` | VARCHAR(500) | No | — | Image URL/path |
| `caption` | VARCHAR(500) | Yes | NULL | Image caption |
| `photographer` | VARCHAR(255) | Yes | NULL | Photographer credit |
| `year_taken` | INTEGER | Yes | NULL | Year photo was taken |
| `display_order` | INTEGER | No | 0 | Sort order for gallery |
| `created_at` | TIMESTAMPTZ | No | NOW() | Upload timestamp |

**Indexes:**
- Primary key on `id`
- Foreign key index on `plaque_id`

**Constraints:**
- `plaque_id` references `plaques(id)` ON DELETE CASCADE

**Statistics:**
- **1,157** total images

---

### categories

Category taxonomy for plaques.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | No | auto | Primary key |
| `name` | VARCHAR(255) | No | — | Display name |
| `slug` | VARCHAR(255) | No | — | URL-friendly identifier |
| `description` | TEXT | Yes | NULL | Category description |

**Indexes:**
- Primary key on `id`
- Unique index on `slug`

**Statistics:**
- **104** total categories

**Sample Categories:**
- Churches, Religious Buildings
- Homes, Mansions
- Military, South African War
- Railways
- Schools, Educational Institutions
- Follow the Flags Trail
- Johannesburg Centenary

---

### plaque_categories

Junction table for many-to-many relationship.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `plaque_id` | INTEGER | No | — | Foreign key to plaques |
| `category_id` | INTEGER | No | — | Foreign key to categories |

**Indexes:**
- Composite primary key on `(plaque_id, category_id)`
- Index on `category_id` for reverse lookups

**Constraints:**
- `plaque_id` references `plaques(id)` ON DELETE CASCADE
- `category_id` references `categories(id)` ON DELETE CASCADE

---

### users

Admin user accounts for authenticated operations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | No | auto | Primary key |
| `email` | VARCHAR(255) | No | — | Unique email address |
| `hashed_password` | VARCHAR(255) | No | — | bcrypt hash |
| `is_active` | BOOLEAN | No | TRUE | Account status |
| `created_at` | TIMESTAMPTZ | No | NOW() | Registration timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `email`

---

## Row Level Security (RLS)

### Public Access

| Table | SELECT | INSERT | UPDATE | DELETE |
|-------|--------|--------|--------|--------|
| `plaques` | ✅ All | ❌ | ❌ | ❌ |
| `images` | ✅ All | ❌ | ❌ | ❌ |
| `categories` | ✅ All | ❌ | ❌ | ❌ |
| `plaque_categories` | ✅ All | ❌ | ❌ | ❌ |
| `users` | ❌ | ❌ | ❌ | ❌ |

### Authenticated Access

Users table allows authenticated users to read their own record only.

### Service Role (Admin)

Service role key bypasses all RLS policies for admin operations.

---

## Database Functions

### nearby_plaques

PostgreSQL function for geolocation search using Haversine formula.

```sql
CREATE OR REPLACE FUNCTION nearby_plaques(
  lat DECIMAL,
  lng DECIMAL,
  radius_m INTEGER
)
RETURNS TABLE (
  id INTEGER,
  distance_m DECIMAL
)
AS $$
  SELECT 
    id,
    (6371000 * acos(
      cos(radians(lat)) * cos(radians(latitude)) *
      cos(radians(longitude) - radians(lng)) +
      sin(radians(lat)) * sin(radians(latitude))
    )) AS distance_m
  FROM plaques
  WHERE (6371000 * acos(
    cos(radians(lat)) * cos(radians(latitude)) *
    cos(radians(longitude) - radians(lng)) +
    sin(radians(lat)) * sin(radians(latitude))
  )) <= radius_m
  ORDER BY distance_m;
$$ LANGUAGE SQL;
```

**Usage:**
```python
supabase.rpc("nearby_plaques", {
    "lat": -26.2041,
    "lng": 28.0473,
    "radius_m": 5000
}).execute()
```

---

## Query Patterns

### List with Embedded Relations

```python
PLAQUE_SELECT = "*, images(*), categories!plaque_categories(*)"

supabase.table("plaques")
    .select(PLAQUE_SELECT)
    .range(0, 49)
    .execute()
```

### Search with OR Conditions

```python
query.or_(
    f"title.ilike.%{search}%,"
    f"description.ilike.%{search}%,"
    f"address.ilike.%{search}%"
)
```

### Filter by Category

```python
# Get plaque IDs for categories
link_resp = supabase.table("plaque_categories")
    .select("plaque_id")
    .in_("category_id", [1, 2, 3])
    .execute()

plaque_ids = [r["plaque_id"] for r in link_resp.data]

# Filter plaques
query.in_("id", plaque_ids)
```

### Count with Exact

```python
supabase.table("plaques")
    .select("id", count="exact")
    .execute()
# Returns: resp.count = 386
```

---

## Data Migration

Original data was migrated from SQLite (`blue_plaques.db`) to Supabase PostgreSQL.

**Migration Steps:**
1. Export SQLite tables to CSV
2. Create Supabase tables with matching schema
3. Import CSV data via Supabase dashboard
4. Create RLS policies
5. Create `nearby_plaques` function
6. Verify data integrity

**Backup:**
- SQLite backup kept at `blue_plaques.db` in project root
