from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ...database import get_db
from ...schemas import CategoryResponse
from ...models import Category, Plaque, plaque_categories

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Get all categories with plaque counts"""
    categories = db.query(
        Category,
        func.count(plaque_categories.c.plaque_id).label('plaque_count')
    ).outerjoin(
        plaque_categories, Category.id == plaque_categories.c.category_id
    ).group_by(Category.id).all()
    
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            plaque_count=count
        )
        for cat, count in categories
    ]

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get single category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
