-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Create plaques table
CREATE TABLE plaques (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    inscription TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOMETRY(POINT, 4326),
    address VARCHAR(500),
    year_erected INTEGER,
    organization VARCHAR(255),
    source_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX idx_plaques_location ON plaques USING GIST(location);
CREATE INDEX idx_plaques_title ON plaques(title);

-- Create images table
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    plaque_id INTEGER NOT NULL REFERENCES plaques(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    caption VARCHAR(500),
    photographer VARCHAR(255),
    year_taken INTEGER,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_images_plaque_id ON images(plaque_id);

-- Create plaque_categories junction table
CREATE TABLE plaque_categories (
    plaque_id INTEGER NOT NULL REFERENCES plaques(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (plaque_id, category_id)
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Insert default categories
INSERT INTO categories (name, slug, description) VALUES
('People', 'people', 'Plaques commemorating notable individuals'),
('Buildings', 'buildings', 'Historic buildings and structures'),
('Events', 'events', 'Significant historical events'),
('Organizations', 'organizations', 'Important organizations and institutions'),
('Cultural Heritage', 'cultural-heritage', 'Cultural and heritage sites'),
('Education', 'education', 'Schools and educational institutions'),
('Religion', 'religion', 'Churches, temples, and religious sites'),
('Sports', 'sports', 'Sports venues and achievements'),
('Arts', 'arts', 'Arts and cultural venues'),
('Military', 'military', 'Military history and sites');
