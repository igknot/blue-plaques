from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ...database import get_db
from ...schemas import ImageResponse, ImageCreate
from ...models import Plaque, Image
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
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    plaque = db.query(Plaque).filter(Plaque.id == plaque_id).first()
    if not plaque:
        raise HTTPException(status_code=404, detail="Plaque not found")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_data = await file.read()
    
    url = upload_image(file_data, filename, file.content_type)
    
    image = Image(
        plaque_id=plaque_id,
        url=url,
        caption=caption,
        photographer=photographer,
        year_taken=year_taken,
        display_order=len(plaque.images)
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@router.delete("/{image_id}")
def delete_plaque_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    filename = image.url.split("/")[-1]
    delete_image(filename)
    
    db.delete(image)
    db.commit()
    return {"message": "Image deleted"}
