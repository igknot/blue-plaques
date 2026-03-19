# API Contracts - Blue Plaques Map

**Base URL:** `/api/v1`
**Authentication:** JWT Bearer Token (admin endpoints only)

## Public Endpoints

### Plaques

#### List Plaques
```
GET /plaques
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number (≥1) |
| `page_size` | int | 50 | Results per page (1-1000) |
| `search` | string | — | Search title, description, address |
| `category_ids` | string | — | Comma-separated category IDs |

**Response:** `PlaqueListResponse`
```json
{
  "total": 386,
  "page": 1,
  "page_size": 50,
  "plaques": [
    {
      "id": 1,
      "title": "Desmond Tutu's House",
      "description": "...",
      "latitude": -26.2041,
      "longitude": 28.0473,
      "address": "123 Main St, Johannesburg",
      "year_erected": 2010,
      "organization": "Heritage Foundation",
      "source_url": "https://heritageportal.co.za/...",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "images": [...],
      "categories": [...]
    }
  ]
}
```

#### Get Single Plaque
```
GET /plaques/{plaque_id}
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `plaque_id` | int | Plaque ID |

**Response:** `PlaqueResponse`

**Errors:**
- `404` - Plaque not found

#### Find Nearby Plaques
```
GET /plaques/nearby
```

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `lat` | float | Yes | Latitude (-90 to 90) |
| `lng` | float | Yes | Longitude (-180 to 180) |
| `radius` | int | No | Radius in meters (100-50000, default: 5000) |

**Response:** `List[PlaqueResponse]`

### Categories

#### List Categories
```
GET /categories
```

**Response:** `List[CategoryResponse]`
```json
[
  {
    "id": 1,
    "name": "Churches, Religious Buildings",
    "slug": "churches-religious-buildings",
    "description": null,
    "plaque_count": 42
  }
]
```

#### Get Single Category
```
GET /categories/{category_id}
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `category_id` | int | Category ID |

**Response:** `CategoryResponse`

**Errors:**
- `404` - Category not found

### Health Check

#### Health Status
```
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Admin Endpoints (JWT Required)

All admin endpoints require `Authorization: Bearer <token>` header.

### Authentication

#### Login
```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "[email]",
  "password": "[password]"
}
```

**Response:** `Token`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Incorrect email or password
- `403` - Inactive user

### Plaque Management

#### Create Plaque
```
POST /plaques
```

**Request Body:** `PlaqueCreate`
```json
{
  "title": "New Heritage Site",
  "description": "Historical significance...",
  "latitude": -26.2041,
  "longitude": 28.0473,
  "address": "456 Heritage Ave",
  "year_erected": 2024,
  "organization": "Heritage Foundation",
  "source_url": "https://...",
  "category_ids": [1, 5, 12]
}
```

**Response:** `PlaqueResponse`

#### Update Plaque
```
PUT /plaques/{plaque_id}
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `plaque_id` | int | Plaque ID |

**Request Body:** `PlaqueUpdate` (all fields optional)
```json
{
  "title": "Updated Title",
  "latitude": -26.2050,
  "category_ids": [1, 2]
}
```

**Response:** `PlaqueResponse`

**Errors:**
- `404` - Plaque not found

#### Delete Plaque
```
DELETE /plaques/{plaque_id}
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `plaque_id` | int | Plaque ID |

**Response:**
```json
{
  "message": "Plaque deleted"
}
```

**Errors:**
- `404` - Plaque not found

### Image Management

#### Upload Image
```
POST /images/plaques/{plaque_id}/images
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `plaque_id` | int | Plaque ID |

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | Image file |
| `caption` | string | No | Image caption |
| `photographer` | string | No | Photographer name |
| `year_taken` | int | No | Year photo was taken |

**Response:** `ImageResponse`
```json
{
  "id": 1,
  "plaque_id": 123,
  "url": "/static/images/abc123.jpg",
  "caption": "Front view",
  "photographer": "John Doe",
  "year_taken": 2023,
  "display_order": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors:**
- `400` - File must be an image
- `404` - Plaque not found

#### Delete Image
```
DELETE /images/{image_id}
```

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `image_id` | int | Image ID |

**Response:**
```json
{
  "message": "Image deleted"
}
```

**Errors:**
- `404` - Image not found

---

## Data Models

### PlaqueBase
```typescript
{
  title: string;           // 1-255 chars, required
  description?: string;
  inscription?: string;
  latitude: number;        // -90 to 90, required
  longitude: number;       // -180 to 180, required
  address?: string;
  year_erected?: number;
  organization?: string;
  source_url?: string;
}
```

### PlaqueResponse
```typescript
PlaqueBase & {
  id: number;
  created_at: string;      // ISO 8601
  updated_at: string;      // ISO 8601
  images: ImageResponse[];
  categories: CategoryResponse[];
}
```

### ImageResponse
```typescript
{
  id: number;
  plaque_id: number;
  url: string;
  caption?: string;
  photographer?: string;
  year_taken?: number;
  display_order: number;
  created_at: string;
}
```

### CategoryResponse
```typescript
{
  id: number;
  name: string;
  slug: string;
  description?: string;
  plaque_count: number;
}
```

### Token
```typescript
{
  access_token: string;
  token_type: "bearer";
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

| Status | Description |
|--------|-------------|
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Missing or invalid token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource doesn't exist |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error |

---

## Rate Limiting

- **Limit:** 60 requests per minute per IP
- **Header:** `X-RateLimit-Remaining` (when implemented)
- **Response:** `429 Too Many Requests` when exceeded
