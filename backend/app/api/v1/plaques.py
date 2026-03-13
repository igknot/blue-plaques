from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_Distance, ST_MakePoint
from typing import List, Optional
from ...database import get_db
from ...schemas import PlaqueResponse, PlaqueListResponse, PlaqueCreate, PlaqueUpdate
from ...models import Plaque, Category
from ...api.deps import get_admin_user

router = APIRouter(prefix="/plaques", tags=["plaques"])

@router.get("", response_model=PlaqueListResponse)
def list_plaques(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None,
    category_ids: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Plaque)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Plaque.title.ilike(search_term),
                Plaque.description.ilike(search_term),
                Plaque.address.ilike(search_term)
            )
        )
    
    if category_ids:
        cat_ids = [int(x) for x in category_ids.split(",")]
        query = query.join(Plaque.categories).filter(Category.id.in_(cat_ids)).distinct()
    
    total = query.count()
    plaques = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "plaques": plaques
    }

@router.get("/nearby", response_model=List[PlaqueResponse])
def nearby_plaques(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(5000, ge=100, le=50000),
    db: Session = Depends(get_db)
):
    point = ST_MakePoint(lng, lat)
    plaques = db.query(Plaque).filter(
        ST_Distance(Plaque.location, point) <= radius
    ).all()
    return plaques

@router.get("/{plaque_id}", response_model=PlaqueResponse)
def get_plaque(plaque_id: int, db: Session = Depends(get_db)):
    plaque = db.query(Plaque).filter(Plaque.id == plaque_id).first()
    if not plaque:
        raise HTTPException(status_code=404, detail="Plaque not found")
    return plaque

@router.post("", response_model=PlaqueResponse)
def create_plaque(
    plaque_data: PlaqueCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    plaque = Plaque(**plaque_data.dict(exclude={"category_ids"}))
    plaque.location = f"POINT({plaque_data.longitude} {plaque_data.latitude})"
    
    if plaque_data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(plaque_data.category_ids)).all()
        plaque.categories = categories
    
    db.add(plaque)
    db.commit()
    db.refresh(plaque)
    return plaque

@router.put("/{plaque_id}", response_model=PlaqueResponse)
def update_plaque(
    plaque_id: int,
    plaque_data: PlaqueUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    plaque = db.query(Plaque).filter(Plaque.id == plaque_id).first()
    if not plaque:
        raise HTTPException(status_code=404, detail="Plaque not found")
    
    update_data = plaque_data.dict(exclude_unset=True, exclude={"category_ids"})
    for field, value in update_data.items():
        setattr(plaque, field, value)
    
    if plaque_data.latitude and plaque_data.longitude:
        plaque.location = f"POINT({plaque_data.longitude} {plaque_data.latitude})"
    
    if plaque_data.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(plaque_data.category_ids)).all()
        plaque.categories = categories
    
    db.commit()
    db.refresh(plaque)
    return plaque

@router.delete("/{plaque_id}")
def delete_plaque(
    plaque_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    plaque = db.query(Plaque).filter(Plaque.id == plaque_id).first()
    if not plaque:
        raise HTTPException(status_code=404, detail="Plaque not found")
    db.delete(plaque)
    db.commit()
    return {"message": "Plaque deleted"}
