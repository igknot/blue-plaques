from fastapi import APIRouter, HTTPException
from typing import List
from collections import Counter
from ...database import supabase
from ...schemas import CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories():
    """Get all categories with plaque counts"""
    cats = supabase.table("categories").select("*").execute()
    pc = supabase.table("plaque_categories").select("category_id").execute()
    counts = Counter(row["category_id"] for row in pc.data)
    return [
        CategoryResponse(
            id=c["id"],
            name=c["name"],
            slug=c["slug"],
            description=c.get("description"),
            plaque_count=counts.get(c["id"], 0),
        )
        for c in cats.data
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):
    """Get single category"""
    response = supabase.table("categories").select("*").eq("id", category_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Category not found")
    cat = response.data[0]
    pc = supabase.table("plaque_categories").select("id", count="exact").eq("category_id", category_id).execute()
    return CategoryResponse(
        id=cat["id"],
        name=cat["name"],
        slug=cat["slug"],
        description=cat.get("description"),
        plaque_count=pc.count or 0,
    )
