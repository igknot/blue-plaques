from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ...database import supabase, supabase_admin
from ...schemas import ImageResponse
from ...services.storage import upload_image, delete_image
from ...api.deps import get_admin_user
import uuid

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/plaques/{plaque_id}/images", response_model=ImageResponse)
async def upload_plaque_image(
    plaque_id: int,
    file: UploadFile = File(...),
    caption: str = None,
    photographer: str = None,
    year_taken: int = None,
    current_user=Depends(get_admin_user),
):
    plaque_resp = supabase.table("plaques").select("id").eq("id", plaque_id).execute()
    if not plaque_resp.data:
        raise HTTPException(status_code=404, detail="Plaque not found")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_data = await file.read()
    url = upload_image(file_data, filename, file.content_type)

    count_resp = supabase.table("images").select("id", count="exact").eq("plaque_id", plaque_id).execute()
    display_order = count_resp.count or 0

    row = {
        "plaque_id": plaque_id,
        "url": url,
        "caption": caption,
        "photographer": photographer,
        "year_taken": year_taken,
        "display_order": display_order,
    }
    result = supabase_admin.table("images").insert(row).execute()
    return result.data[0]


@router.delete("/{image_id}")
def delete_plaque_image(image_id: int, current_user=Depends(get_admin_user)):
    response = supabase.table("images").select("*").eq("id", image_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Image not found")
    image = response.data[0]
    filename = image["url"].split("/")[-1]
    delete_image(filename)
    supabase_admin.table("images").delete().eq("id", image_id).execute()
    return {"message": "Image deleted"}
