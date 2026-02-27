# Blue Plaques Map - Functional Specification

## Overview
An interactive web application that displays heritage blue plaques on a map, allowing users to explore historical sites, search by location or category, and view detailed information including images and descriptions.

## System Architecture

### Backend
- **Technology**: Python Flask
- **Database**: SQLite (`blue_plaques.db`)
- **Port**: 5000 (localhost)

### Frontend
- **Technology**: HTML5, CSS3, JavaScript
- **Mapping Library**: Leaflet.js 1.9.4
- **Map Tiles**: OpenStreetMap

### Data Storage
- **Database Tables**:
  - `plaques`: Main plaque information (id, title, url, image_url, location, description, local_image_path, local_html_path, geo_location, address, categories)
  - `plaque_images`: Additional images for each plaque (id, plaque_id, image_url, local_image_path, image_title, image_order)
- **File Storage**: `offline_copy/` directory containing images and HTML files

## Core Features

### 1. Interactive Map Display
- **Map Provider**: OpenStreetMap with Leaflet.js
- **Default View**: Centered on Johannesburg (-26.178, 28.039) at zoom level 13
- **Markers**: Each plaque displayed as a map marker at its geo-location
- **Zoom Controls**: Positioned at bottom-right corner

### 2. Plaque Information Display

#### Hover Tooltip
- Displays when hovering over a marker
- Shows:
  - Plaque thumbnail image (150x150px)
  - Plaque title

#### Click Popup
- Opens when clicking a marker
- Contains:
  - Plaque title (bold, 18px)
  - Address (gray text)
  - Description
  - Category tags (gray pills)
  - Thumbnail images (100x100px grid)
  - Link to Heritage Portal (external)

### 3. Image Lightbox Carousel
- **Trigger**: Click any image in the popup
- **Features**:
  - Full-screen overlay with dark background
  - Large image display (max 90% viewport)
  - Navigation arrows (previous/next)
  - Close button (X)
  - Image caption display
  - Keyboard controls:
    - Left/Right arrows: Navigate images
    - Escape: Close lightbox
- **Image Sources**: 
  - Local files from `offline_copy/images/`
  - Fallback to online URLs if local file unavailable

### 4. Hamburger Menu & Sidebar

#### Hamburger Button
- **Position**: Top-left corner
- **Size**: 50x50px white rounded square
- **Animation**: Transforms to X when sidebar is open
- **Action**: Toggles sidebar visibility

#### Sidebar Panel
- **Position**: Slides in from left
- **Width**: 320px
- **Height**: Full viewport
- **Contents**:
  - Search box
  - "Find Near Me" button
  - Category filter section
  - Select All / Clear All buttons
  - Scrollable category checkboxes

### 5. Search Functionality
- **Input**: Text search box in sidebar
- **Search Fields**: 
  - Plaque title
  - Description
  - Address
- **Behavior**: 
  - Real-time filtering (on input)
  - Case-insensitive
  - Updates map markers dynamically

### 6. Category Filtering
- **Display**: Checkboxes for all available categories
- **Categories Include**:
  - Follow the Flags Trail
  - Homes, Mansions
  - Military, South African War
  - Architects, People
  - Railways, Johannesburg Centenary
  - And more...
- **Behavior**:
  - All categories checked by default
  - Only shows plaques matching selected categories
  - Markers removed from map when category unchecked
- **Bulk Actions**:
  - "Select All": Checks all categories
  - "Clear All": Unchecks all categories

### 7. Find Near Me
- **Technology**: Browser Geolocation API
- **Functionality**:
  - Requests user's current location
  - Displays blue dot marker at user's position
  - Centers map on user location (zoom level 14)
  - Filters to show 10 nearest plaques
  - Calculates distance using Euclidean distance
- **Error Handling**:
  - Alert if geolocation not supported
  - Alert if location access denied

### 8. Responsive Design
- **Mobile-Friendly**: Sidebar slides over map on small screens
- **Touch Support**: All interactions work on touch devices
- **Viewport Scaling**: Adapts to different screen sizes

## API Endpoints

### GET /
- Returns: `index.html`
- Description: Main application page

### GET /api/plaques
- Returns: JSON array of all plaques with geo-location
- Response Format:
```json
[
  {
    "id": 1,
    "title": "Plaque Title",
    "lat": -26.1780822,
    "lon": 28.0392237,
    "address": "Street Address",
    "categories": ["Category1", "Category2"],
    "description": "Description text",
    "mainImage": "offline_copy/images/image.jpg",
    "images": [
      {"path": "offline_copy/images/image1.jpg", "title": "Image Title"},
      {"path": "https://example.com/image2.jpg", "title": "Image Title"}
    ],
    "url": "https://heritageportal.co.za/..."
  }
]
```

### GET /offline_copy/<path:path>
- Returns: Static file from offline_copy directory
- Description: Serves local images and HTML files

### GET /favicon.svg
- Returns: SVG favicon
- Description: Blue circular plaque icon with "BP HERITAGE" text

## Data Model

### Plaques Table
- `id`: INTEGER PRIMARY KEY
- `title`: TEXT
- `url`: TEXT (Heritage Portal link)
- `image_url`: TEXT (original online URL)
- `location`: TEXT
- `description`: TEXT
- `local_image_path`: TEXT
- `local_html_path`: TEXT
- `geo_location`: TEXT (JSON: {"lat": "...", "lon": "..."})
- `address`: TEXT
- `categories`: TEXT (comma-separated)

### Plaque Images Table
- `id`: INTEGER PRIMARY KEY
- `plaque_id`: INTEGER (FOREIGN KEY)
- `image_url`: TEXT
- `local_image_path`: TEXT
- `image_title`: TEXT
- `image_order`: INTEGER

## User Workflows

### 1. Browse All Plaques
1. Open application
2. View all 386 plaques on map
3. Hover over markers to preview
4. Click marker to see details

### 2. Search for Specific Plaque
1. Click hamburger menu
2. Type search term in search box
3. Map updates to show matching plaques only
4. Click marker to view details

### 3. Filter by Category
1. Click hamburger menu
2. Scroll to category filters
3. Uncheck unwanted categories
4. Map updates to show only selected categories

### 4. Find Nearby Plaques
1. Click hamburger menu
2. Click "Find Near Me" button
3. Allow location access
4. View 10 nearest plaques
5. Blue dot shows your location

### 5. View Plaque Images
1. Click plaque marker
2. Click any thumbnail in popup
3. Lightbox opens with full-size image
4. Use arrows or keyboard to navigate
5. Press Escape or X to close

## Technical Requirements

### Browser Support
- Modern browsers with ES6 support
- Geolocation API support (for Find Near Me)
- SVG support (for favicon)

### Dependencies
- Python 3.x
- Flask
- SQLite3
- Leaflet.js 1.9.4 (CDN)
- OpenStreetMap tiles (CDN)

### Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
python3 server.py
```

### Access
- URL: http://localhost:5000
- No authentication required

## Performance Considerations
- All 386 plaques loaded on initial page load
- Client-side filtering (no server requests)
- Images lazy-loaded by browser
- Fallback to online images if local unavailable
- Map tiles cached by browser

## Future Enhancements (Not Implemented)
- Clustering for dense marker areas
- Route planning between plaques
- User favorites/bookmarks
- Share plaque links
- Print-friendly view
- Multi-language support
- Admin interface for data management

## Version Information
- Version: 1.0
- Last Updated: February 27, 2026
- Total Plaques: 386
- Total Images: 1,157
