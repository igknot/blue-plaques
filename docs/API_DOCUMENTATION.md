# Blue Plaques API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication

⚠️ **Current State**: No server-side authentication implemented. Admin endpoints rely on client-side password check only.

**Security Risk**: Anyone can call admin endpoints directly, bypassing the client-side password.

**Recommended**: Implement JWT or session-based authentication before production deployment.

---

## Public Endpoints

### Get All Plaques

Retrieves all plaques with geo-location data, including images and metadata.

**Endpoint**: `GET /api/plaques`

**Authentication**: None required

**Query Parameters**: None

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "title": "Tutu House",
    "lat": -26.1780822,
    "lon": 28.0392237,
    "address": "6309 Vilakazi Street, Orlando West, Soweto",
    "categories": [
      "Homes, Mansions",
      "Architects, People"
    ],
    "description": "Home of Archbishop Desmond Tutu from 1975 to 1997...",
    "mainImage": "static/images/Tutu_House_Blue_Plaque.png",
    "images": [
      {
        "path": "static/images/Tutu_House_Blue_Plaque.png",
        "title": "Tutu House Blue Plaque"
      },
      {
        "path": "static/images/Tutu_House_Front.jpg",
        "title": "House Front View"
      }
    ],
    "url": "https://heritageportal.co.za/article/tutu-house"
  }
]
```

**Response Fields**:
- `id` (integer): Unique plaque identifier
- `title` (string): Plaque title
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate
- `address` (string|null): Physical address
- `categories` (array): Category tags
- `description` (string|null): Plaque description
- `mainImage` (string|null): Primary image path
- `images` (array): Additional images with titles
- `url` (string|null): Heritage Portal link

**Error Responses**:

`500 Internal Server Error`
```json
{
  "error": "Database error"
}
```

**Example Request**:
```bash
curl http://localhost:5000/api/plaques
```

**Notes**:
- Returns all plaques with non-null geo_location
- Plaques with malformed geo_location are skipped with warning log
- Images array includes both local paths and external URLs
- Response size: ~200KB for 386 plaques

---

## Admin Endpoints

⚠️ **WARNING**: These endpoints have NO server-side authentication. Implement auth before production.

### Report Plaque for Review

Marks a plaque as needing review (sets `to_review = 1` in database).

**Endpoint**: `POST /api/plaques/<plaque_id>/report`

**Authentication**: ⚠️ None (should require admin auth)

**Path Parameters**:
- `plaque_id` (integer): ID of plaque to report

**Request Body**: None

**Response**: `200 OK`

```json
{
  "success": true,
  "message": "Plaque marked for review"
}
```

**Error Responses**:

`500 Internal Server Error`
```json
{
  "error": "Failed to report plaque"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/plaques/123/report
```

**Use Cases**:
- User reports incorrect information
- User reports inappropriate content
- Admin flags plaque for verification

**Database Impact**:
```sql
UPDATE plaques SET to_review = 1 WHERE id = ?
```

---

### Update Plaque Position

Updates the geo-location of a plaque.

**Endpoint**: `PUT /api/plaques/<plaque_id>/position`

**Authentication**: ⚠️ None (should require admin auth)

**Path Parameters**:
- `plaque_id` (integer): ID of plaque to update

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "lat": -26.1780822,
  "lon": 28.0392237
}
```

**Request Fields**:
- `lat` (float): New latitude coordinate
- `lon` (float): New longitude coordinate

**Response**: `200 OK`

```json
{
  "success": true
}
```

**Error Responses**:

`500 Internal Server Error`
```json
{
  "error": "Failed to update position"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:5000/api/plaques/123/position \
  -H "Content-Type: application/json" \
  -d '{"lat": -26.178, "lon": 28.039}'
```

**Use Cases**:
- Admin corrects incorrect plaque location
- Admin moves marker after field verification
- Bulk position corrections

**Database Impact**:
```sql
UPDATE plaques 
SET geo_location = '{"lat": "-26.178", "lon": "28.039"}' 
WHERE id = ?
```

**Validation Issues**:
- ⚠️ No validation on lat/lon ranges
- ⚠️ No check if plaque_id exists
- ⚠️ No audit trail of position changes

---

### Add New Plaque

Creates a new plaque with photo upload.

**Endpoint**: `POST /api/plaques`

**Authentication**: ⚠️ None (should require admin auth)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "New Heritage Site",
  "description": "Historical significance description",
  "address": "123 Main Street, Johannesburg",
  "categories": "Homes, Mansions, Architects, People",
  "lat": -26.1780822,
  "lon": 28.0392237,
  "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Request Fields**:
- `title` (string, required): Plaque title
- `description` (string, required): Plaque description
- `address` (string, required): Physical address
- `categories` (string, required): Comma-separated categories
- `lat` (float, required): Latitude coordinate
- `lon` (float, required): Longitude coordinate
- `photo` (string, required): Base64-encoded JPEG image with data URI prefix

**Response**: `200 OK`

```json
{
  "success": true
}
```

**Error Responses**:

`500 Internal Server Error`
```json
{
  "error": "Failed to add plaque"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/plaques \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Plaque",
    "description": "Test description",
    "address": "Test address",
    "categories": "Test Category",
    "lat": -26.178,
    "lon": 28.039,
    "photo": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

**File Storage**:
- Photos saved to `static/uploads/`
- Filename format: `{title_with_underscores}.jpg`
- No size limits enforced
- No image validation

**Database Impact**:
```sql
INSERT INTO plaques (
  title, description, address, categories, 
  geo_location, local_image_path
) VALUES (?, ?, ?, ?, ?, ?)
```

**Security Issues**:
- ⚠️ No file size limit (DoS risk)
- ⚠️ No image format validation
- ⚠️ No malware scanning
- ⚠️ Filename collision possible
- ⚠️ No input sanitization
- ⚠️ Directory traversal possible

**Recommended Improvements**:
1. Validate image format and size
2. Generate unique filenames (UUID)
3. Resize images to standard dimensions
4. Scan for malware
5. Sanitize all text inputs
6. Add rate limiting

---

## Static File Endpoints

### Serve Static Files

Serves images and other static assets.

**Endpoint**: `GET /static/<path>`

**Authentication**: None required

**Path Parameters**:
- `path` (string): Relative path to file

**Response**: File content with appropriate MIME type

**Example Requests**:
```bash
# Serve plaque image
curl http://localhost:5000/static/images/Tutu_House.jpg

# Serve uploaded image
curl http://localhost:5000/static/uploads/New_Plaque.jpg
```

**Security Considerations**:
- ⚠️ No access control on uploaded files
- ⚠️ Directory traversal possible
- ⚠️ No rate limiting

---

### Get Favicon

Returns application favicon.

**Endpoint**: `GET /favicon.svg`

**Authentication**: None required

**Response**: SVG image

**Example Request**:
```bash
curl http://localhost:5000/favicon.svg
```

---

## Error Handling

All endpoints use consistent error response format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes**:
- `200 OK`: Successful request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Logging**:
- All errors logged to stdout with timestamp
- Stack traces included in logs (not in responses)
- Database errors logged separately

---

## Rate Limiting

⚠️ **Current State**: No rate limiting implemented

**Recommended Limits**:
- Public endpoints: 100 requests/minute per IP
- Admin endpoints: 10 requests/minute per IP
- File uploads: 5 requests/hour per IP

**Implementation**: Use Flask-Limiter

---

## CORS Policy

**Current State**: No CORS headers set (same-origin only)

**For API Access**: Add CORS headers if needed:
```python
response.headers['Access-Control-Allow-Origin'] = '*'
```

---

## Versioning

**Current State**: No API versioning

**Recommended**: Implement versioned endpoints:
- `/api/v1/plaques`
- `/api/v2/plaques`

---

## Pagination

**Current State**: All plaques returned in single response (~200KB)

**Recommended**: Implement pagination for large datasets:
```
GET /api/plaques?page=1&limit=50
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 386,
    "pages": 8
  }
}
```

---

## Filtering & Search

**Current State**: Client-side filtering only

**Recommended**: Server-side filtering:
```
GET /api/plaques?category=Homes,Mansions&search=tutu
```

---

## Testing

**Example Test Cases**:

```python
import requests

BASE_URL = "http://localhost:5000"

# Test get all plaques
response = requests.get(f"{BASE_URL}/api/plaques")
assert response.status_code == 200
assert isinstance(response.json(), list)

# Test report plaque
response = requests.post(f"{BASE_URL}/api/plaques/1/report")
assert response.status_code == 200
assert response.json()["success"] == True

# Test update position
response = requests.put(
    f"{BASE_URL}/api/plaques/1/position",
    json={"lat": -26.178, "lon": 28.039}
)
assert response.status_code == 200
```

---

## Security Checklist

Before production deployment:

- [ ] Implement authentication (JWT/sessions)
- [ ] Add authorization checks to admin endpoints
- [ ] Validate all inputs
- [ ] Add rate limiting
- [ ] Implement CSRF protection
- [ ] Validate file uploads
- [ ] Add audit logging
- [ ] Use HTTPS only
- [ ] Sanitize error messages
- [ ] Add API key for external access
