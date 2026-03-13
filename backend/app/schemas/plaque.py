from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ImageBase(BaseModel):
    url: str
    caption: Optional[str] = None
    photographer: Optional[str] = None
    year_taken: Optional[int] = None
    display_order: int = 0

class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: int
    plaque_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    plaque_count: int = 0

    class Config:
        from_attributes = True

class PlaqueBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    inscription: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    year_erected: Optional[int] = None
    organization: Optional[str] = None
    source_url: Optional[str] = None

class PlaqueCreate(PlaqueBase):
    category_ids: List[int] = []

class PlaqueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    inscription: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    year_erected: Optional[int] = None
    organization: Optional[str] = None
    source_url: Optional[str] = None
    category_ids: Optional[List[int]] = None

class PlaqueResponse(PlaqueBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    categories: List[CategoryResponse] = []

    class Config:
        from_attributes = True

class PlaqueListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    plaques: List[PlaqueResponse]
