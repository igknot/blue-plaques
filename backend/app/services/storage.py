from pathlib import Path

UPLOAD_DIR = Path(__file__).parent.parent.parent / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def upload_image(file_data: bytes, filename: str, content_type: str) -> str:
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(file_data)
    return f"/static/images/{filename}"

def delete_image(filename: str):
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
