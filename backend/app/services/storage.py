import boto3
from botocore.client import Config
from ..config import settings

s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_image(file_data: bytes, filename: str, content_type: str) -> str:
    s3_client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=filename,
        Body=file_data,
        ContentType=content_type
    )
    return f"{settings.R2_PUBLIC_URL}/{filename}"

def delete_image(filename: str):
    s3_client.delete_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=filename
    )
