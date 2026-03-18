from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ...database import supabase
from ...schemas import PlaqueResponse, PlaqueListResponse, PlaqueCreate, PlaqueUpdate
from ...api.deps import get_admin_user

router = APIRouter(prefix="/plaques", tags=["plaques"])

PLAQUE_SELECT = "*, images(*), categories!plaque_categories(*)"


def _add_plaque_count(data):
    """Add plaque_count=0 to embedded categories."""
    if isinstance(data, list):
        for item in data:
            _add_plaque_count(item)
    elif isinstance(data, dict) and "categories" in data:
        for cat in data.get("categories", []):
            cat.setdefault("plaque_count", 0)


@router.get("", response_model=PlaqueListResponse)
def list_plaques(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None,
    category_ids: Optional[str] = None,
):
    offset = (page - 1) * page_size
    plaque_ids_filter = None

    if category_ids:
        cat_ids = [int(x) for x in category_ids.split(",")]
        link_resp = supabase.table("plaque_categories").select("plaque_id").in_("category_id", cat_ids).execute()
        plaque_ids_filter = list({r["plaque_id"] for r in link_resp.data})
        if not plaque_ids_filter:
            return {"total": 0, "page": page, "page_size": page_size, "plaques": []}

    # Count query
    count_q = supabase.table("plaques").select("id", count="exact")
    if search:
        count_q = count_q.or_(f"title.ilike.%{search}%,description.ilike.%{search}%,address.ilike.%{search}%")
    if plaque_ids_filter is not None:
        count_q = count_q.in_("id", plaque_ids_filter)
    count_resp = count_q.execute()
    total = count_resp.count

    # Data query
    query = supabase.table("plaques").select(PLAQUE_SELECT)
    if search:
        query = query.or_(f"title.ilike.%{search}%,description.ilike.%{search}%,address.ilike.%{search}%")
    if plaque_ids_filter is not None:
        query = query.in_("id", plaque_ids_filter)
    resp = query.range(offset, offset + page_size - 1).execute()

    _add_plaque_count(resp.data)
    return {"total": total, "page": page, "page_size": page_size, "plaques": resp.data}


@router.get("/nearby", response_model=List[PlaqueResponse])
def nearby_plaques(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(5000, ge=100, le=50000),
):
    rpc_resp = supabase.rpc("nearby_plaques", {"lat": lat, "lng": lng, "radius_m": radius}).execute()
    if not rpc_resp.data:
        return []
    ids = [r["id"] for r in rpc_resp.data]
    resp = supabase.table("plaques").select(PLAQUE_SELECT).in_("id", ids).execute()
    _add_plaque_count(resp.data)
    return resp.data


@router.get("/{plaque_id}", response_model=PlaqueResponse)
def get_plaque(plaque_id: int):
    resp = supabase.table("plaques").select(PLAQUE_SELECT).eq("id", plaque_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Plaque not found")
    _add_plaque_count(resp.data)
    return resp.data


@router.post("", response_model=PlaqueResponse)
def create_plaque(plaque_data: PlaqueCreate, current_user=Depends(get_admin_user)):
    data = plaque_data.dict(exclude={"category_ids"})
    resp = supabase.table("plaques").insert(data).execute()
    plaque = resp.data[0]

    if plaque_data.category_ids:
        links = [{"plaque_id": plaque["id"], "category_id": cid} for cid in plaque_data.category_ids]
        supabase.table("plaque_categories").insert(links).execute()

    return get_plaque(plaque["id"])


@router.put("/{plaque_id}", response_model=PlaqueResponse)
def update_plaque(plaque_id: int, plaque_data: PlaqueUpdate, current_user=Depends(get_admin_user)):
    existing = supabase.table("plaques").select("id").eq("id", plaque_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Plaque not found")

    update_data = plaque_data.dict(exclude_unset=True, exclude={"category_ids"})
    if update_data:
        supabase.table("plaques").update(update_data).eq("id", plaque_id).execute()

    if plaque_data.category_ids is not None:
        supabase.table("plaque_categories").delete().eq("plaque_id", plaque_id).execute()
        if plaque_data.category_ids:
            links = [{"plaque_id": plaque_id, "category_id": cid} for cid in plaque_data.category_ids]
            supabase.table("plaque_categories").insert(links).execute()

    return get_plaque(plaque_id)


@router.delete("/{plaque_id}")
def delete_plaque(plaque_id: int, current_user=Depends(get_admin_user)):
    existing = supabase.table("plaques").select("id").eq("id", plaque_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Plaque not found")
    supabase.table("plaques").delete().eq("id", plaque_id).execute()
    return {"message": "Plaque deleted"}
